import inspect
import argparse
import hashlib
import sys
from mp3 import MP3Error
from pymp3utils import get_tag
from pymp3utils.mp3sum import validate_file, sum_type_default, get_sum_frame, set_sum_frame, remove_sum_frame, calculate_sum


def _validate_files(files, verbose):
    err = 0
    for f in files:
        print "'%s':" % f,
        try:
            res = validate_file(f)
        except MP3Error, v:
            print "ERROR: %s" % v.args[0],
            err += 1
            continue
        if len(res) == 0:
            print "no checksums found",
        else:
            for r in res:
                print "%s:" % r[0],
                if r[1]:
                    print "ok",
                else:
                    print "CORRUPT",
                    err += 1
        print ""

    if err > 0:
        sys.exit(1)


def _update_files(files, verbose, sum_types, add, remove):
    for f in files:
        if verbose:
            print f
        update = False
        tag = get_tag(f)
        for s in sum_types:
            if remove:
                if get_sum_frame(tag, s) != None:
                    if verbose:
                        print "  removing %s" % s
                    remove_sum_frame(tag, s)
                    update = True
            if add:
                if get_sum_frame(tag, s) == None:
                    if verbose:
                        print "  adding %s" % s
                    try:
                        cs = calculate_sum(f, s)
                    except MP3Error, v:
                        print "ERROR in '%s': %s" % (f, v.args[0])
                        continue

                    set_sum_frame(tag, cs)
                    update = True
        if update:
            if verbose:
                print " updating file"
            tag.update()


def main():
    valid_types = []
    type_check = type(hashlib.md5())
    for t, f in inspect.getmembers(hashlib, inspect.isbuiltin):
        if isinstance(f(), type_check):
            valid_types.append(t)

    parser = argparse.ArgumentParser(
        description='Manage checksums for mp3 audio data in ID3v2 tags')
    parser.add_argument('files', metavar='file', type=str, nargs='+',
                        help='file(s) to process')
    parser.add_argument('-c', '--check',
                        action='store_true',
                        help='verify checksums (default if no other ' +
                        'operation is requested)')
    parser.add_argument('-u', '--update',
                        action='store_true',
                        help='calculate and store checksum(s) from file(s)' +
                        ' that don\'t already have the requested checksum' +
                        'type(s)')
    parser.add_argument('-r', '--remove',
                        action='store_true',
                        help='remove stored checksum(s) from file(s)')
    parser.add_argument('-s', '--sum-type', nargs='?', metavar='hash',
                        default=[sum_type_default], action='append',
                        help='type(s) of checksum(s) to calculate',
                        choices=valid_types)
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()

    do_check = args.check
    if args.update or args.remove:
        _update_files(args.files, args.verbose, args.sum_type, args.update,
                      args.remove)
    else:
        do_check = True

    if do_check:
        _validate_files(args.files, args.verbose)