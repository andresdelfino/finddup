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
    """Returns an iterator of os.DirEntry objects for files under top"""

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
    group = []

    for file in sorted(file_list, key=lambda x: x[1]):
        if prev_size is None:
            prev_size = file[1]
            group.append(file[0])
            continue

        if file[1] == prev_size:
            group.append(file[0])
        else:
            if len(group) > 1:
                files = []
                duplicate_files = []

                for file_path in group:
                    hash = get_hash(file_path)
                    files.append((file_path, hash))

                prev_hash = None
                duplicate_files = []
                for file_spam in sorted(files, key=lambda x: x[1]):
                    if prev_hash is None:
                        prev_hash = file_spam[1]
                        duplicate_files.append(file_spam[0])
                        continue

                    if file_spam[1] == prev_hash:
                        duplicate_files.append(file_spam[0])
                    else:
                        if len(duplicate_files) > 1:
                            yield prev_hash, duplicate_files

                        duplicate_files.clear()

                        prev_hash = file_spam[1]
                        duplicate_files.append(file_spam[0])

            group.clear()

            prev_size = file[1]
            group.append(file[0])
