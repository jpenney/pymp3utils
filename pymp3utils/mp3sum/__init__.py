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

import eyeD3
import mp3 as MP3

from pymp3utils import get_filename, get_tag, memoize


hash_type_default = 'sha256'
"""
Default hash to use if not specified in all functions that have a
`hash_type` parameter.
"""
_owner_id_prefix = 'mp3sum'

@memoize
def get_key(hash_type=hash_type_default):
    """
    Returns mp3sum user text frame description for given hash type.

    :rtype: string
    """
    return '_'.join([_owner_id_prefix, hash_type])


def get_sum_frame(target, hash_type=hash_type_default):
    """
    Retrieve mp3sum user text frame for given hash type.

    :param target: object to act on
    :param hash_type: hash to retrieve (optional)
    :type hash_type: string
    :returns: frame containing mp3sum for given hash or `None`
    :rtype: `eyeD3.tag.UserTextFrame`
    """
    tag = get_tag(target)
    key = get_key(hash_type)
    for utf in tag.getUserTextFrames():
        if utf.description == key:
            return utf

    return None


def read_sum(target, hash_type=hash_type_default):
    """
     Retrieve mp3sum for given hash type.

    :param target: object to act on
    :param hash_type: hash to retrieve (optional)
    :type hash_type: string
    :returns: hexdigest mp3sum for given hash or `None`
    :rtype: string
    """
    frame = get_sum_frame(target, hash_type)
    if isinstance(frame, eyeD3.frames.UserTextFrame):
        return frame.text
    return None


def set_sum_frame(target, hash):
    """
    Store mp3sum in target

    :param target: object to act on
    :param hash: hashlib object populated with audio data frames from `target`
    """
    tag = get_tag(target)
    key = get_key(hash.name)
    tag.addUserTextFrame(key, hash.hexdigest())


def remove_sum_frame(target, hash_type=hash_type_default):
    """
    Remove mp3sum user text frame for given hash type, if present.

    :param target: object to act on
    :param hash_type: hash to retrieve (optional)
    :type hash_type: string
    """

    tag = get_tag(target)
    key = get_key(hash_type)
    tag.addUniqueFileID(key, None)
    tag.removeUserTextFrame(key)


def build_hash(target, hash_type=hash_type_default):
    """
    Build hash from mp3 data frames in target.

    :param target: object to act on
    :param hash_type: hash to retrieve (optional)
    :rtype: hashlib HASH
    """
    hgen = hashlib.new(hash_type)
    f = open(get_filename(target), 'rb')
    for (hdr, frm) in MP3.frames(f):
        hgen.update(frm)
    return hgen


def validate_sum(target):
    """
    Validates all mp3sums found stored on target.
    
    :param target: object to act on
    :rtype: list of tuples
    :returns: hashes found in target, with validation status
    """
    tag = get_tag(target)
    sums = []
    results = []
    for utf in tag.getUserTextFrames():
        if utf.description.startswith(_owner_id_prefix):
            hash_type = utf.description.split('_')[1]
            sums.append((hash_type, utf.text))
    for (hash_type, sum_data) in sums:
        calc = build_hash(target, hash_type)
        results.append((hash_type, calc.hexdigest() == sum_data))
    return results


