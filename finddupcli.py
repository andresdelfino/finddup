import os
import sys

import finddup


def main():
    if len(sys.argv) == 3 and sys.argv[1] == '--delete':
        delete = True
    else:
        delete = False

    for hash, ocurrences in finddup.get_duplicate_files(sys.argv[-1]):
        if not delete:
            print(f'{hash}:')

        for path in ocurrences[0 if not delete else 1:]:
            print(path)

            if delete:
                os.remove(path)

        print()


if __name__ == '__main__':
    main()
