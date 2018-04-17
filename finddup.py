import hashlib
import os
import os.path
import sys


def get_hash(path):
    """Returns the MD5 hash of a given file"""

    hasher = hashlib.md5()
    with open(path, 'rb') as file:
        file_content = file.read()
    hasher.update(file_content)
    return hasher.hexdigest()


def powerwalk(top):
    with os.scandir(top) as it:
        for entry in it:
            if entry.is_dir():
                yield from powerwalk(entry.path)
            else:
                yield entry


def get_duplicate_files(path):
    """Returns a list of duplicate files of a directory in the form of a hash-keyed dictionary"""

    paths_per_hash = {}
    hashes_per_size = {}
    firsts_of_size = {}

    for entry in powerwalk(path):
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

    duplicate_files = {}
    for file_hash, paths in paths_per_hash.items():
        if len(paths) > 1:
            duplicate_files[file_hash] = paths

    return duplicate_files


if __name__ == '__main__':
    duplicate_files = get_duplicate_files(sys.argv[-1])

    if not sys.argv[1] == '--delete':
        for file_hash in duplicate_files:
            for path in duplicate_files[file_hash]:
                print(f'{file_hash}: {path}')
    else:
        for file_hash in duplicate_files:
            for path in duplicate_files[file_hash][1:]:
                print(path)
                os.remove(path)
