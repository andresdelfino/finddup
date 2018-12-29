#!/usr/bin/env python

import argparse
import os

import finddup


def main():
    parser = argparse.ArgumentParser(description='Find duplicate files.')
    parser.add_argument('-d', action='store_true', dest='delete', help='Delete duplicate files.')
    parser.add_argument('path', help='Path to search.')

    args = parser.parse_args()

    for hash, size, ocurrences in finddup.get_duplicate_files(args.path):
        if not args.delete:
            print(f'{hash}:')

        for path in ocurrences[0 if not args.delete else 1:]:
            print(path)

            if args.delete:
                try:
                    os.remove(path)
                except PermissionError:
                    print('PermissionError while deleting:', path)

        print()


if __name__ == '__main__':
    main()
