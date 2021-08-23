#!/usr/bin/env python
import sys
import os
from pathlib import Path
from ftplib import FTP
from netrc import netrc
from tempfile import TemporaryDirectory
from contextlib import closing
from math import ceil
from zipfile import ZipFile, ZIP_LZMA
from jinja2 import Template
from hashlib import md5

HOST = 'restricted_ftp'
FTP_TIMEOUT = 60
UPLOAD_DIR = 'wallinb/field_uploads'
CHUNK_SIZE = 100000
CHUNK_ROOT_DIR = Path('./staged')
JOINER_TEMPLATE = './joiner_template.py'


def get_creds():
    nrc = netrc()
    user, _, passwd = nrc.hosts[HOST]

    return user, passwd


def chunk_file(filepath, chunk_dir):
    chunk_dir = Path(chunk_dir)
    filepath = Path(filepath)

    n = ceil(os.path.getsize(filepath) / CHUNK_SIZE)
    chunk_filepaths = []
    with open(filepath, 'rb') as fi:
        for i in range(n):
            chunk_filepath = chunk_dir / (filepath.name + f'.part{i}')
            chunk_filepaths.append(chunk_filepath)
            with open(chunk_filepath, 'wb') as fo:
                fo.write(fi.read(CHUNK_SIZE))

    return chunk_filepaths


def write_joiner(
    joiner_filepath,
    original_filename,
    zipped_filename,
    correct_checksum,
    chunk_filenames,
    chunk_size,
):
    with open(JOINER_TEMPLATE, 'r') as f:
        template = Template(f.read())
        rendered = template.render(
            original_filename=original_filename,
            joiner_filename=joiner_filepath.name,
            zipped_filename=zipped_filename,
            correct_checksum=correct_checksum,
            chunk_filenames=chunk_filenames,
            chunk_size=chunk_size,
        )

    with open(joiner_filepath, 'w') as f:
        f.write(rendered)


def zip_file(filepath, zipped_filepath=None):
    filepath = Path(filepath)
    if zipped_filepath is None:
        zipped_filepath = filepath.parent / (filepath.name + '.zip')

    with ZipFile(zipped_filepath, 'w', compression=ZIP_LZMA) as zf:
        zf.write(filepath, filepath.name)

    return zipped_filepath


def compute_checksum(filepath):
    with open(filepath, 'rb') as f:
        checksum = md5(f.read()).hexdigest()

    return checksum


def chunk_and_upload(original_filepath):
    original_filepath = Path(original_filepath)
    chunk_dir = CHUNK_ROOT_DIR / original_filepath.name

    os.makedirs(chunk_dir)

    # Zip file first to reduce size
    zipped_filepath = chunk_dir / (original_filepath.name + '.zip')
    zip_file(original_filepath, zipped_filepath)

    # Calculate checksum
    checksum = compute_checksum(zipped_filepath)

    # Dice up into chunks
    chunk_filepaths = chunk_file(zipped_filepath, chunk_dir)

    # Delete whole zipped file
    os.remove(zipped_filepath)

    # Write 'joiner' script
    joiner_filepath = chunk_dir / (zipped_filepath.name + '.join.py')
    write_joiner(
        joiner_filepath,
        original_filename=original_filepath.name,
        zipped_filename=zipped_filepath.name,
        correct_checksum=checksum,
        chunk_filenames=[el.name for el in chunk_filepaths],
        chunk_size=CHUNK_SIZE,
    )

    return
    # Upload everything to host
    with closing(FTP(HOST, timeout=FTP_TIMEOUT)) as ftp:
        ftp.login(*get_creds())

        # Create directory with filepanem to hold file
        ftp.cwd(UPLOAD_DIR)
        file_directory = ftp.mkd(original_filepath.name)
        ftp.cwd(file_directory)

        for chunk_filepath in chunk_filepaths:
            with open(chunk_filepath, 'r') as f:
                ftp.storlines('STOR {}'.format(chunk_filepath.name), f)
            # Chunk upload complete, delete chunk locally
            os.remove(chunk_filepath)

        # All done,   remove 'file' derectory
        os.rmdir(chunk_dir)


if __name__ == '__main__':
    filepath = sys.argv[1]
    chunk_and_upload(filepath)
