'''
Script to reconstitute {{original_filename}} from chunks

To run:
    $ python {{joiner_filename}}

NOTE: Assumes this file resides alongside the chunks!
'''
import os
from zipfile import ZipFile
from hashlib import md5
from pathlib import Path

original_filename = '{{original_filename}}'
zipped_filename = '{{zipped_filename}}'
correct_checksum = '{{correct_checksum}}'
chunk_filenames = {{chunk_filenames}}
chunk_size = {{chunk_size}}

current_dir = Path(__file__).parent

to_cleanup = set(chunk_filenames)
to_cleanup.add(zipped_filename)
to_cleanup.add(Path(__file__).name)

# Iterate through chunks, checking for re-uploads and using 'best'
for i, chunk_filename in enumerate(chunk_filenames):
    duplicates = list(current_dir.glob(chunk_filename + '*'))
    best = max(reversed(duplicates), key=lambda f: os.path.getsize(f))
    chunk_filenames[i] = best.name
    to_cleanup.update([el.name for el in duplicates])


# Write chunks to whole
zipped_filepath = current_dir / zipped_filename
with open(zipped_filepath, 'wb') as fo:
    for chunk_filename in chunk_filenames:
        chunk_filepath = current_dir / chunk_filename
        with open(chunk_filepath, 'rb') as fi:
            fo.write(fi.read())

# Check checksum
with open(zipped_filepath, 'rb') as f:
    checksum = md5(f.read()).hexdigest()
    assert checksum == correct_checksum, "Uh oh! Checksum mismatch!"

# Unzip
with ZipFile(zipped_filepath, 'r') as zf:
    zf.extractall(path=current_dir)

# Cleanup
for filename in to_cleanup:
    os.remove(current_dir / filename)
