import hashlib
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

    prev_size = None
    group_by_size = []
    for file_path, file_size in sorted(file_list, key=lambda x: x[1]) + [(None, None)]:
        if prev_size is None:
            prev_size = file_size
            group_by_size.append(file_path)
            continue

        if file_size == prev_size:
            group_by_size.append(file_path)
        else:
            if len(group_by_size) > 1:
                file_list_2 = []
                for file_path in group_by_size:
                    hash = get_hash(file_path)
                    file_list_2.append((file_path, hash))

                prev_hash = None
                group_by_hash = []
                for file_2_path, file_2_hash in sorted(file_list_2, key=lambda y: y[1]) + [(None, None)]:
                    if prev_hash is None:
                        prev_hash = file_2_hash
                        group_by_hash.append(file_2_path)
                        continue

                    if file_2_hash == prev_hash:
                        group_by_hash.append(file_2_path)
                    else:
                        if len(group_by_hash) > 1:
                            yield prev_hash, group_by_hash

                        group_by_hash.clear()

                        prev_hash = file_2_hash
                        group_by_hash.append(file_2_path)

            group_by_size.clear()

            prev_size = file_size
            group_by_size.append(file_path)
