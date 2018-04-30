import hashlib
import os


def get_hash(path):
    """Returns the MD5 hash of a given file"""

    with open(path, 'rb') as file:
        file_content = file.read()

    hasher = hashlib.md5()
    hasher.update(file_content)

    return hasher.hexdigest()


def powerwalk(top):
    """Returns an iterator of os.DirEntry objects for files under top"""

    with os.scandir(top) as it:
        for entry in it:
            yield entry

            if entry.is_dir():
                yield from powerwalk(entry.path)


def get_duplicate_files(path):
    """Returns a list of duplicate files of a directory in the form of a hash-keyed dictionary"""

    paths_per_hash = {}
    hashes_per_size = {}
    firsts_of_size = {}

    for entry in powerwalk(path):
        if entry.is_dir():
            continue

        file_size = entry.stat().st_size

        if file_size == 0:
            continue

        if file_size not in firsts_of_size:
            firsts_of_size[file_size] = entry.path
            continue

        if file_size not in hashes_per_size:
            prev_hash = get_hash(firsts_of_size[file_size])
            hashes_per_size[file_size] = [prev_hash]
            paths_per_hash[prev_hash] = [firsts_of_size[file_size]]

        file_hash = get_hash(entry.path)

        if file_hash not in hashes_per_size[file_size]:
            hashes_per_size[file_size].append(file_hash)
            paths_per_hash[file_hash] = [entry.path]
        else:
            paths_per_hash[file_hash].append(entry.path)

    for file_hash, paths in paths_per_hash.items():
        if len(paths) > 1:
            yield file_hash, paths
