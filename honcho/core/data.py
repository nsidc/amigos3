import os
from hashlib import md5
from math import ceil

from honcho.config import DATA_LOG_FILENAME, FTP_CHUNK_SIZE, JOINER_TEMPLATE, SEP


def log_serialized(s, tag):
    if not s.endswith("\n"):
        s += "\n"

    with open(DATA_LOG_FILENAME(tag), "a") as f:
        f.write(s)


def serialize(sample, conversions):
    converted = []
    for key in sample._fields:
        try:
            value = getattr(sample, key)
            if conversions[key] is not None:
                converted.append(conversions[key].format(value))
        except Exception:
            converted.append(str(value))
    serialized = SEP.join(converted)

    return serialized


def deserialize(serialized, conversions, constructor):
    split = serialized.split(SEP)

    deserialized = constructor(
        **dict((key, conversions[key](split[i])) for i, key in enumerate(conversions))
    )

    return deserialized


def print_samples(samples, conversion):
    print(", ".join(samples[0]._fields))
    print("-" * 80)
    for sample in samples:
        print(serialize(sample, conversion).replace(SEP, ", "))


def compute_checksum(filepath):
    with open(filepath, "rb") as f:
        checksum = md5(f.read()).hexdigest()

    return checksum


def chunk_file(filepath, output_dir):
    filename = os.path.basename(filepath)
    n = int(ceil(os.path.getsize(filepath) / float(FTP_CHUNK_SIZE)))
    chunk_filepaths = []
    n_len = len(str(n))
    with open(filepath, "rb") as fi:
        for i in range(n):
            fmt = ".part{0:0" + str(n_len) + "d}"
            chunk_filepath = os.path.join(output_dir, filename + fmt.format(i))
            chunk_filepaths.append(chunk_filepath)
            with open(chunk_filepath, "wb") as fo:
                fo.write(fi.read(FTP_CHUNK_SIZE))

    return chunk_filepaths


def make_chunk_joiner(chunk_filepaths, checksum):
    original_filename = os.path.basename(chunk_filepaths[0].split(".part")[0])
    with open(JOINER_TEMPLATE, "r") as f:
        template = f.read()

    chunk_filenames = [os.path.basename(filepath) for filepath in chunk_filepaths]
    rendered = (
        template.replace("{{original_filename}}", original_filename)
        .replace("{{correct_checksum}}", checksum)
        .replace("{{chunk_filenames}}", repr(chunk_filenames))
        .replace("{{chunk_size}}", str(FTP_CHUNK_SIZE))
    )

    joiner_filepath = os.path.join(
        os.path.dirname(chunk_filepaths[0]), original_filename + ".join.py"
    )
    with open(joiner_filepath, "w") as f:
        f.write(rendered)

    return joiner_filepath
