import hashlib
import os
import sys

def get_hash(path):
    hasher = hashlib.md5()
    with open(path, 'rb') as file:
        file_content = file.read()
    hasher.update(file_content)
    return hasher.hexdigest()

def get_duplicate_files(path):
    def dup(path, paths_per_hash, hashes_per_size, firsts_of_size, sizes_found):
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_dir():
                    dup(entry.path, paths_per_hash, hashes_per_size, firsts_of_size, sizes_found)
                else:
                    size = entry.stat().st_size
                    if size:
                        if size not in sizes_found:
                            sizes_found.append(size)
                            firsts_of_size[size] = entry.path
                        else:
                            if size not in hashes_per_size:
                                prev_hash = get_hash(firsts_of_size[size])
                                hashes_per_size[size] = [prev_hash]
                                paths_per_hash[prev_hash] = [firsts_of_size[size]]
                            hash = get_hash(entry.path)
                            if hash not in hashes_per_size[size]:
                                hashes_per_size[size].append(hash)
                                paths_per_hash[hash] = [entry.path]
                            else:
                                paths_per_hash[hash].append(entry.path)

    paths_per_hash = {}
    dup(path, paths_per_hash, {}, {}, [])

    duplicate_files = {}
    for hash, paths in paths_per_hash.items():
        if len(paths) > 1:
            duplicate_files[hash] = paths

    return duplicate_files

if __name__ == '__main__':
    if sys.argv[1] == '--delete':
        delete = True
    else:
        delete = False

    duplicate_files = get_duplicate_files(sys.argv[-1])

    if not delete:
        for hash in duplicate_files:
            for path in duplicate_files[hash]:
                print(f'{hash}: {path}')
    else:
        for hash in duplicate_files:
            for path in duplicate_files[hash][1:]:
                print(path)
                os.remove(path)