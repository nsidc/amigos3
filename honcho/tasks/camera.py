import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
from logging import getLogger
from tempfile import NamedTemporaryFile
from time import sleep

import requests
from requests.auth import HTTPDigestAuth

from honcho.config import (CAMERA_PASSWORD, CAMERA_STARTUP_WAIT, CAMERA_USERNAME,
                           CJPEG_COMMAND, DATA_DIR, DATA_TAGS, DJPEG_COMMAND, GPIO,
                           JPEGTRAN_COMMAND, LOOK_PTZ, LOOK_SERIES, ONVIF_TEMPLATE_DIR,
                           ONVIF_TEMPLATE_FILES, PTZ, PTZ_SERVICE_URL, SNAPSHOP_URL,
                           SOAP_ACTION_KEYS, SOAP_ACTIONS, TIMESTAMP_FILENAME_FMT)
from honcho.core.gpio import powered
from honcho.tasks.archive import archive_filepaths
from honcho.tasks.common import task
from honcho.tasks.upload import queue_filepaths
from honcho.util import clear_directory

logger = getLogger(__name__)


def ns(tag):
    if tag in ("Body", "Header", "Envelope"):
        return "{http://www.w3.org/2003/05/soap-envelope}" + tag
    elif tag in (
        "AbsoluteMove",
        "GetStatus",
        "GetStatusResponse",
        "PTZStatus",
        "ProfileToken",
        "Position",
        "Speed",
    ):
        return "{http://www.onvif.org/ver20/ptz/wsdl}" + tag
    elif tag in ("PanTilt", "Zoom"):
        return "{http://www.onvif.org/ver10/schema}" + tag


def get_ptz():
    headers = {
        "SOAPAction": SOAP_ACTIONS[SOAP_ACTION_KEYS.GET_STATUS],
        "Content-Type": "application/soap+xml",
    }

    template_filepath = os.path.join(
        ONVIF_TEMPLATE_DIR, ONVIF_TEMPLATE_FILES[SOAP_ACTION_KEYS.GET_STATUS]
    )
    with open(template_filepath, "r") as f:
        data = f.read()

    response = requests.post(PTZ_SERVICE_URL, data=data, headers=headers)

    root = ET.fromstring(response.content)

    position = root.find(
        "/".join(
            [
                ns("Body"),
                ns("GetStatusResponse"),
                ns("PTZStatus"),
                "{http://www.onvif.org/ver10/schema}Position",
            ]
        )
    )
    pan_tilt = position.find(ns("PanTilt"))
    pan = float(pan_tilt.attrib["x"])
    tilt = float(pan_tilt.attrib["y"])

    zoom = position.find(ns("Zoom"))
    zoom = float(zoom.attrib["x"])

    return PTZ(pan=pan, tilt=tilt, zoom=zoom)


def serialize(value):
    return "{0}".format(value)


def set_ptz(pan, tilt, zoom):
    logger.debug("Moving to ptz: {0} {1} {2}".format(pan, tilt, zoom))
    pan = 0 if pan is None else pan
    tilt = 0 if tilt is None else tilt
    zoom = 0 if zoom is None else zoom
    headers = {
        "SOAPAction": SOAP_ACTIONS[SOAP_ACTION_KEYS.ABSOLUTE_MOVE],
        "Content-Type": "application/soap+xml",
    }

    template_filepath = os.path.join(
        ONVIF_TEMPLATE_DIR, ONVIF_TEMPLATE_FILES[SOAP_ACTION_KEYS.ABSOLUTE_MOVE]
    )
    tree = ET.parse(template_filepath)
    root = tree.getroot()

    pan_tilt_el = root.find(
        "/".join([ns("Body"), ns("AbsoluteMove"), ns("Position"), ns("PanTilt")])
    )
    pan_tilt_el.attrib["x"] = serialize(pan)
    pan_tilt_el.attrib["y"] = serialize(tilt)

    zoom_el = root.find(
        "/".join([ns("Body"), ns("AbsoluteMove"), ns("Position"), ns("Zoom")])
    )
    zoom_el.attrib["x"] = serialize(zoom)

    data = ET.tostring(root)
    requests.post(PTZ_SERVICE_URL, data=data, headers=headers)

    sleep(5)


def snapshot(filepath):
    response = requests.get(
        SNAPSHOP_URL, auth=HTTPDigestAuth(CAMERA_USERNAME, CAMERA_PASSWORD)
    )
    logger.debug("Taking snapshot: {0}".format(filepath))
    with open(filepath, "wb") as f:
        f.write(response.content)


def reduce_image(input_filepath, output_filepath, factor):
    logger.debug("Reducing image by {0}".format(factor))
    with NamedTemporaryFile() as temp_file:
        subprocess.check_call(
            "{cmd} -scale {factor} {inf} > {outf}".format(
                cmd=DJPEG_COMMAND,
                factor=factor,
                inf=input_filepath,
                outf=temp_file.name,
            ),
            shell=True,
        )
        subprocess.check_call(
            "{cmd} -scale {factor} {inf} > {outf}".format(
                cmd=CJPEG_COMMAND,
                factor="1/1",
                inf=temp_file.name,
                outf=output_filepath,
            ),
            shell=True,
        )


def crop_image(input_filepath, output_filepath, crop):
    subprocess.check_call(
        "{cmd} -crop {width}x{height}+{x}+{y} -outfile {outf} {inf}".format(
            cmd=JPEGTRAN_COMMAND,
            inf=input_filepath,
            outf=output_filepath,
            **crop._asdict()
        ),
        shell=True,
    )


@task
def execute():
    with powered([GPIO.CAM, GPIO.HUB]):
        logger.debug(
            "Sleeping {0} seconds for camera startup".format(CAMERA_STARTUP_WAIT)
        )
        sleep(CAMERA_STARTUP_WAIT)
        raw_filepaths, processed_filepaths = [], []
        for look in LOOK_SERIES:
            logger.debug("Looking at {0}".format(look))
            ptz = LOOK_PTZ[look]["ptz"]
            scale = LOOK_PTZ[look]["scale"]
            crop = LOOK_PTZ[look]["crop"]
            set_ptz(**ptz._asdict())

            data_dir = DATA_DIR(DATA_TAGS.CAM)

            timestamp = datetime.now()
            raw_filename = "{timestamp}_{look}_full.jpg".format(
                timestamp=timestamp.strftime(TIMESTAMP_FILENAME_FMT), look=look
            )
            raw_filepath = os.path.join(data_dir, raw_filename)
            snapshot(raw_filepath)
            raw_filepaths.append(raw_filepath)

            processed_filename = "{timestamp}_{look}_low.jpg".format(
                timestamp=timestamp.strftime(TIMESTAMP_FILENAME_FMT), look=look
            )
            processed_filepath = os.path.join(data_dir, processed_filename)
            shutil.copy(raw_filepath, processed_filepath)
            processed_filepaths.append(processed_filepath)

            if crop is not None:
                crop_image(processed_filepath, processed_filepath, crop)
            if scale is not None:
                reduce_image(processed_filepath, processed_filepath, scale)

    tag = DATA_TAGS.CAM
    queue_filepaths(processed_filepaths, postfix=tag, tarball=False)
    archive_filepaths(raw_filepaths, postfix=tag)
    clear_directory(data_dir)
