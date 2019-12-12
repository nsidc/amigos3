import os
import subprocess
from tempfile import NamedTemporaryFile
from datetime import datetime
import xml.etree.ElementTree as ET

import requests
from requests.auth import HTTPDigestAuth

from honcho.util import fail_gracefully, log_execution
from honcho.config import (
    DATA_DIR,
    DATA_TAGS,
    SOAP_ACTIONS,
    SOAP_ACTION_KEYS,
    ONVIF_TEMPLATE_DIR,
    ONVIF_TEMPLATE_FILES,
    CAMERA_USERNAME,
    CAMERA_PASSWORD,
    IMAGE_REDUCTION_FACTOR,
    PTZ_SERVICE_URL,
    PTZ,
    LOOK_PTZ,
    LOOK_SERIES,
    SNAPSHOP_URL,
    DJPEG_COMMAND,
    CJPEG_COMMAND,
    TIMESTAMP_FILENAME_FMT,
)
from honcho.tasks.upload import stage_path


def ns(tag):
    if tag in ('Body', 'Header', 'Envelope'):
        return '{http://www.w3.org/2003/05/soap-envelope}' + tag
    elif tag in (
        'AbsoluteMove',
        'GetStatus',
        'GetStatusResponse',
        'PTZStatus',
        'ProfileToken',
        'Position',
        'Speed',
    ):
        return '{http://www.onvif.org/ver20/ptz/wsdl}' + tag
    elif tag in ('PanTilt', 'Zoom'):
        return '{http://www.onvif.org/ver10/schema}' + tag


def get_ptz():
    headers = {
        'SOAPAction': SOAP_ACTIONS[SOAP_ACTION_KEYS.GET_STATUS],
        'Content-Type': 'application/soap+xml',
    }

    template_filepath = os.path.join(
        ONVIF_TEMPLATE_DIR, ONVIF_TEMPLATE_FILES[SOAP_ACTION_KEYS.GET_STATUS]
    )
    with open(template_filepath, 'r') as f:
        data = f.read()

    response = requests.post(PTZ_SERVICE_URL, data=data, headers=headers)

    root = ET.parse(response.content)

    pan_tilt = root.find(
        '/'.join(
            [
                ns('Body'),
                ns('GetStatusResponse'),
                ns('PTZStatus'),
                ns('Position'),
                ns('PanTilt'),
            ]
        )
    )
    pan = float(pan_tilt.attrib['x'])
    tilt = float(pan_tilt.attrib['y'])

    zoom = root.find(
        '/'.join(
            [
                ns('Body'),
                ns('GetStatusResponse'),
                ns('PTZStatus'),
                ns('Position'),
                ns('PanTilt'),
            ]
        )
    )

    return PTZ(pan=pan, tilt=tilt, zoom=zoom)


def serialize(value):
    return '{0}'.format(value)


def set_ptz(pan, tilt, zoom):
    pan = 0 if pan is None else pan
    tilt = 0 if tilt is None else tilt
    zoom = 0 if zoom is None else zoom
    headers = {
        'SOAPAction': SOAP_ACTIONS[SOAP_ACTION_KEYS.ABSOLUTE_MOVE],
        'Content-Type': 'application/soap+xml',
    }

    template_filepath = os.path.join(
        ONVIF_TEMPLATE_DIR, ONVIF_TEMPLATE_FILES[SOAP_ACTION_KEYS.ABSOLUTE_MOVE]
    )
    tree = ET.parse(template_filepath)
    root = tree.getroot()

    pan_tilt = root.find(
        '/'.join([ns('Body'), ns('AbsoluteMove'), ns('Position'), ns('PanTilt')])
    )
    pan_tilt.attrib['x'] = serialize(pan)
    pan_tilt.attrib['y'] = serialize(tilt)

    zoom = root.find(
        '/'.join([ns('Body'), ns('AbsoluteMove'), ns('Position'), ns('Zoom')])
    )
    zoom.attrib['x'] = serialize(zoom)

    data = ET.tostring(root)
    requests.post(PTZ_SERVICE_URL, data=data, headers=headers)


def snapshot(filepath):
    response = requests.get(
        SNAPSHOP_URL, auth=HTTPDigestAuth(CAMERA_USERNAME, CAMERA_PASSWORD)
    )
    with open(filepath, 'wb') as f:
        f.write(response.content)


def reduce_image(input_filepath, output_filepath, factor=IMAGE_REDUCTION_FACTOR):
    with NamedTemporaryFile() as temp_file:
        subprocess.check_call(
            '{cmd} {factor} {inf} > {outf}'.format(
                cmd=DJPEG_COMMAND,
                factor=factor,
                inf=input_filepath,
                outf=temp_file.name,
            ),
            shell=True,
        )
        subprocess.check_call(
            '{cmd} {factor} {inf} > {outf}'.format(
                cmd=CJPEG_COMMAND,
                factor='1/1',
                inf=temp_file.name,
                outf=output_filepath,
            ),
            shell=True,
        )


@fail_gracefully
@log_execution
def execute():
    for look in LOOK_SERIES:
        ptz = LOOK_PTZ[look]
        set_ptz(*ptz)

        timestamp = datetime.now()
        full_res_filename = '{timestamp}_{look}_full.jpg'.format(
            timestamp=timestamp.strftime(TIMESTAMP_FILENAME_FMT), look=look
        )
        full_res_filepath = os.path.join(DATA_DIR(DATA_TAGS.CAM), full_res_filename)
        snapshot(full_res_filepath)

        low_res_dir = os.path.join(DATA_DIR(DATA_TAGS.CAM), 'low_res')
        low_res_filename = '{timestamp}_{look}_low.jpg'.format(
            timestamp=timestamp.strftime(TIMESTAMP_FILENAME_FMT), look=look
        )
        low_res_filepath = os.path.join(low_res_dir, low_res_filename)
        reduce_image(full_res_filepath, low_res_filepath, IMAGE_REDUCTION_FACTOR)

    stage_path(low_res_filepath, prefix='CAM')


if __name__ == '__main__':
    execute()
