import hashlib
import itertools
import os


def get_hash(path):
    """Returns the MD5 hash of a file"""

    with open(path, 'rb') as file:
        file_content = file.read()

    hasher = hashlib.md5()
    hasher.update(file_content)

    return hasher.hexdigest()


def powerwalk(top):
    """Returns an iterator of os.DirEntry objects under top"""

    with os.scandir(top) as it:
        for entry in it:
            yield entry

            if entry.is_dir():
                yield from powerwalk(entry.path)


def get_duplicate_files(path):
    """Returns a list of duplicate files of a directory in the form of a hash-keyed dictionary"""

    file_list = []
    for entry in powerwalk(path):
        if entry.is_dir():
            continue

        file_size = entry.stat().st_size

        if file_size == 0:
            continue

        file_list.append((entry.path, file_size))

    key = lambda x: x[1]
    file_list = sorted(file_list, key=key)
    for file_size, file_paths in itertools.groupby(file_list, key=key):
        file_paths = [x[0] for x in file_paths]

        if len(file_paths) > 1:
            file_list = []
            for file_path in file_paths:
                hash = get_hash(file_path)
                file_list.append((file_path, hash))

            key = lambda x: x[1]
            file_list = sorted(file_list, key=key)
            for file_hash, file_paths in itertools.groupby(file_list, key=key):
                file_paths = [x[0] for x in file_paths]

                if len(file_paths) > 1:
                    yield file_hash, file_paths
