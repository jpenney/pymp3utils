# copyright 2010 Jason Penney
#
# This file is part of pymp3utils
#
# pymp3utils is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pymp3utils is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pymp3utils. If not, see <http://www.gnu.org/licenses/>.

import hashlib
import inspect
import sys

import eyeD3
import argparse
from mp3 import MP3Error

from pymp3utils import get_tag
from pymp3utils.mp3sum import validate_sum, hash_type_default, \
    get_sum_frame, set_sum_frame, remove_sum_frame, build_hash


def _validate_files(files, verbose, quiet):
    err = 0
    for f in files:
        diag = False
        result = "'%s': " % f
        try:
            res = validate_sum(f)
        except MP3Error, v:
            result += 'ERROR: %s' % v.args[0]
            err += 1
            diag = True

        if not diag:
            if len(res) == 0:
                result += 'no checksums found'
                diag = True
            else:
                rstrings = []
                for r in res:
                    rstring = '%s:' % str(r[0])
                    if r[1]:
                        rstring += 'ok'
                    else:
                        rstring += 'CORRUPT'
                        diag = True
                        err += 1
                    rstrings.append(rstring)
                result += ', '.join(rstrings)
        if not quiet or diag:
            print result

    if err > 0:
        sys.exit(1)


def _update_files(
    files,
    verbose,
    sum_types,
    add,
    remove,
    quiet,
    version = eyeD3.ID3_ANY_VERSION,
    v1 = False
    ):

    for f in files:
        if verbose:
            print f
        update = False
        tag = get_tag(f)
        for s in sum_types:
            if remove:
                if get_sum_frame(tag, s) != None:
                    if verbose:
                        print '  removing %s' % s
                    remove_sum_frame(tag, s)
                    update = True
            if add:
                if get_sum_frame(tag, s) == None:
                    if verbose:
                        print '  adding %s' % s
                    try:
                        cs = build_hash(f, s)
                    except MP3Error, v:
                        print "ERROR in '%s': %s" % (f, v.args[0])
                        continue

                    set_sum_frame(tag, cs)
                    update = True
        if update:
            if verbose:
                print ' updating file'
            pymp3utils.set_tag_version(tag, version, v1)


def main():
    """
    Entrypoint for `mp3sum` command line utility
    """
    valid_types = []
    type_check = type(hashlib.md5())
    for (t, f) in inspect.getmembers(hashlib, inspect.isbuiltin):
        if isinstance(f(), type_check):
            valid_types.append(t)

    parser = \
        argparse.ArgumentParser(description='Manage checksums for mp3 '
                                'audio data in ID3v2 tags')
    parser.add_argument('files', metavar='file', type=str, nargs='+',
                        help='file(s) to process')
    parser.add_argument('-c', '--check', action='store_true',
                        help='verify checksums (default if no other '
                        + 'operation is requested)')
    parser.add_argument('-u', '--update', action='store_true',
                        help='calculate and store checksum(s) from '
                        'file(s)'
                        + " that don't already have the requested "
                        "checksum" + 'type(s)')
    parser.add_argument('-r', '--remove', action='store_true',
                        help='remove stored checksum(s) from file(s)')
    parser.add_argument(
        '-s',
        '--sum-type',
        nargs='?',
        metavar='hash',
        default=[hash_type_default],
        action='append',
        help='type(s) of checksum(s) to calculate',
        choices=valid_types,
        )
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-q', '--quiet', action='store_true')
    for ver in [eyeD3.ID3_V2_2, eyeD3.ID3_V2_3, eyeD3.ID3_V2_4]:
        verstr = '.'.join([str(num) for num in eyeD3.utils.constantToVersions(
            ver)[0:-1]])
        parser.add_argument('v'.join(['--id3', verstr]),
                            help='save as ID3v%s' % verstr,
                            action='store_const',
                            const=ver,
                            dest='version',
                            default=eyeD3.ID3_ANY_VERSION
                            )

    parser.add_argument('--id3v1',
                        action='store_true',
                        dest='v1')

    args = parser.parse_args()

    if args.quiet:
        args.verbose = False

    do_check = args.check
    if args.update or args.remove:
        _update_files(args.files, args.verbose, args.sum_type,
                      args.update, args.remove, args.quiet,
                      args.version, args.v1)
    else:
        do_check = True

    if do_check:
        _validate_files(args.files, args.verbose, args.quiet)
