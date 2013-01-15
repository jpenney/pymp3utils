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

from functools import wraps

__version__ = 'unknown'
try:
    from pymp3utils._version import __version__ as v
    __version__ = v
except:
    pass

def memoize(func):
    func._memoize_cache = {}

    @wraps(func)
    def _memoize(*args, **kwargs):
        try:
            if kwargs:
                key = args, frozenset(kwargs.items())
            else:
                key = args
        
            hash(key)
        except TypeError:
            # in case something wasn't hashable, just call the func
            return func(*args, **kwargs)

        cache = func._memoize_cache
        if not key in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]

    return _memoize

# originally taken from flashbake
# optimized using generators (early matches about 10x faster)
@memoize
def _find_executable(executable):
    ex_paths = (os.path.join(path, executable) for path in \
                    os.getenv('PATH').split(os.pathsep))
    paths = (ex_path for ex_path in ex_paths \
                 if os.path.exists(ex_path))
    return next(paths, None)

# taken from flashbake
def _executable_available(executable):
    return _find_executable(executable) != None

def set_id3_version(target, version, v1=False, force_update=False):
    """
    Changes the tag to the specified version if necessary.

    :param target: target to act on
    :type target: `eyeD3.Tag`, `eyeD3.TagFile`, or string
    :param version: tag version as defined by `eyeD3`
    :param v1: flag to also save ID3v1 tags
    :type v1: bool
    :pram force_update: 
        force tag v2.x tag to write even if version is not changed

    :type force_update: bool
    """
    try:
        tag = get_tag(target)
    except:
        tag = None

    if tag != None:
        if force_update or tag.getVersion() != version:
            tag.update(version)
        if v1:
            tag.update(eyeD3.ID3_V1)


def get_tag(target, version=eyeD3.ID3_ANY_VERSION):
    """
    Returns `eyeD3.Tag` for `target`.

    :param target: Object to load tag from
    :type target: `eyeD3.Tag`, `eyeD3.TagFile`, or string
    :rtype: `exes3.Tag`
    """

    if isinstance(target, eyeD3.TagFile):
        target = target.getTag()

    if isinstance(target, eyeD3.Tag):
        if version == eyeD3.ID3_ANY_VERSION or \
               version == target.getVersion():
            return target
        target = target.linkedFile

    if isinstance(target, str):
        return eyeD3.Mp3AudioFile(target, version).getTag()

    raise TypeError('unable to convert to eyeD3.Tag: %s' % str(target))

@memoize
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

@memoize
def is_mp3(target):
    """
    Return true if `target` is an mp3 target

    :param target: file to test
    :type target: `eyeD3.Tag`, `eyeD3.TagFile`, or string
    """

    try:
        t = get_filename(target)
        target = t
    except:
        pass
    return eyeD3.isMp3File(target)


def find_frame(target, key, search=None):
    match = None
    tag = get_tag(target)
    if len(tag.frames[key]) > 0:
        match = tag.frames[key][0]
    if match == None and search != None:
        for frm in tag.frames[search]:
            if frm.description == key:
                match = frm
                break

    return match


def convert_frame(target, oldID, newID):
    """
     Convert frames of type `oldID`, or `TXXX` frames with
     description `oldID` to frames of type `newID`

     Return number of changed frames

     Keyword arguments:
     tag - the eyeD3.tag to act on
     oldID - frame id to match
     newID - frame id to convert to

     Example usage:
     >>> count = convertFrames(tag, 'XSOP', 'TSOP')

     """

    tag = get_tag(target)
    count = 0
    for frm in tag.frames[oldID]:
        frm.header.id = newID
        count = count + 1

    frm = find_frame(tag, oldID, 'TXXX')
    if frm != None:
        frm.header.id = newID
        frm.description = frm.text
        frm.text = ''
        count = count + 1

    return count
