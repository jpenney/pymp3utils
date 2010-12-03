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

import os
import os.path

import eyeD3


__version__ = 'unknown'
try:
    from pymp3utils._version import __version__
except:
    pass


# taken from flashbake
def _find_executable(executable):
    found = filter(lambda ex: os.path.exists(ex),
                   map(lambda path_token:
                       os.path.join(path_token, executable),
                       os.getenv('PATH').split(os.pathsep)))
    if (len(found) == 0):
        return None
    return found[0]


# taken from flashbake


def _executable_available(executable):
    return _find_executable(executable) != None


def set_id3_version(target, version):
    """
    Changes the tag to the specified version if necessary.

    :param target: target to act on
    :param version: tag version as defined by `eyeD3` 
    """

    try:
        tag = get_tag(target)
    except:
        tag = None

    if tag != None:
        if tag.getVersion() != version:
            tag.update(version)


def get_tag(target):
    """
    Returns `eyeD3.Tag` for `target`.

    :param target: Object to load tag from
    :type target: `eyeD3.Tag`, `eyeD3.TagFile`, or string
    :rtype: `exes3.Tag`
    """
    if isinstance(target, eyeD3.Tag):
        return target
    if isinstance(target, eyeD3.TagFile):
        return target.getTag()
    if isinstance(target, str):
        return eyeD3.Mp3AudioFile(target).getTag()
    raise TypeError('unable to convert to eyeD3.Tag: %s' % str(target))


def get_filename(target):
    """
    Returns string containing a filepath for `target`

    :param target: Object to return filepath for.
    :type target: `eyeD3.Tag`, `eyeD3.TagFile`, `file`, or string
    :rtype: string
    """

    if isinstance(target, str):
        return target
    if isinstance(target, file):
        return target.name
    if isinstance(target, eyeD3.TagFile):
        return target.fileName
    if isinstance(target, eyeD3.Tag):
        return target.linkedFile.name
    raise TypeError('unable to convert to filepath: %s' % str(target))


def is_mp3(target):
    """
    Return true if `target` is an mp3 target

    :param target: file to test
    """
    try:
        t = get_filename(target)
        target = t
    except:
        pass
    try:
        eyeD3.Mp3AudioFile(target)
    except:
        return False
    return True
