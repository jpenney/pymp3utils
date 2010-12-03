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

import sys
import subprocess
import os.path

import pymp3utils
from pymp3utils.mp3gain import id3_to_ape, ape_to_id3, \
    get_aacgain_exec, AACGainUtilityError


# def _mp3albumgainer(argv):
#     id3_to_ape(argv)
#     cmd = ['aacgain']
#     cmd.extend(argv)
#     scan = subprocess.Popen(cmd, stdout=subprocess.PIPE)
#     scan_output = scan.communicate()[0]
#     if 'Recommended "Album" mp3 gain change for all files: 0' \
#         not in scan_output:
#         print 'needs adjustment'
#         cmd.insert(1, '-a')
#         cmd.insert(1, '-t')
#         cmd.insert(1, '-k')
#         subprocess.call(cmd)
#     ape_to_id3(argv)


def _find_exec():
    """
    Calls `get_aacgain_exec` and returns the
    result.  If the result is `None` a `AACGainUtilityError` is raised.

    :rtype: string
    """
    try:
        return get_aacgain_exec()
    except AACGainUtilityError, e:
        print e.value
        sys.exit(2)


def main():
    """
    Executes `mp3gainer` entry point.
    """
    bn = os.path.basename(sys.argv[0])
    args = sys.argv[1:]
    mp3s = filter(pymp3utils.is_mp3, args)
    id3_to_ape(mp3s)
    cmd = [_find_exec()]
    cmd.extend(args)
    if '-v' in args or '-h' in args or len(args) == 0:
        print '%s version %s, wrapping:' % (bn, pymp3utils.__version__)
    subprocess.call(cmd)
    ape_to_id3(mp3s)


