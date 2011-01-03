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

import struct

import mutagen
import eyeD3
import mutagen.apev2
import mutagen.id3

import pymp3utils

_stringtags = ['MP3GAIN_ALBUM_MINMAX', 'MP3GAIN_MINMAX']
_floattags = ['REPLAYGAIN_ALBUM_PEAK', 'REPLAYGAIN_TRACK_PEAK',
              'REPLAYGAIN_ALBUM_GAIN', 'REPLAYGAIN_TRACK_GAIN']


class AACGainUtilityError(Exception):

    """
    Error when the aacgain/mp3gain command line utility can not be
    set up.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def get_aacgain_exec():
    """
    Returns `*gain` utility to use.

    :rtype: string
    """

    for ex in ['aacgain', 'mp3gain']:
        if pymp3utils._executable_available(ex):
            return ex
    raise AACGainUtilityError('could not find aacgain or mp3gain in '
                              'PATH')


def _get_mutagen_apev2(file):
    ape = None
    try:
        ape = mutagen.apev2.APEv2(file)
    except mutagen.apev2.APENoHeaderError:
        ape = mutagen.apev2.APEv2()
    return ape


def _get_mutagen_id3(file):
    pymp3utils.set_id3_version(file, eyeD3.ID3_V2_4)
    id3 = None
    try:
        id3 = mutagen.id3.ID3(file)
    except mutagen.id3.ID3NoHeaderError:
        print 'No ID3 header found; creating a new tag'
        id3 = mutagen.id3.ID3()
    return id3


def read_from_apev2(ape):
    """
    Reads replaygain/mp3gain headers from APEv2 tag.

    :param ape: `mutagen.apev2.APEv2` to read
    :rtype: dictionary
    """

    rg = {}
    for tagname in _stringtags:
        if tagname in ape:
            rg[tagname] = str(ape[tagname])

    for tagname in _floattags:
        if tagname in ape:
            rg[tagname] = float(ape[tagname][0].split(' ')[0])

    return rg


def read_from_id3(id3):
    """
    Reads replaygain/mp3gain headers from ID3v2 tag.

    :param id3: `mutagen.id3.ID3` to read
    :rtype: dictionary
    """

    rg = {}
    tags = []
    for t in _stringtags:
        tags.append(t.lower())
        tags.append(t.upper())
    for tagname in tags:
        matches = id3.getall('TXXX:' + tagname)
        if len(matches) > 0:
            rg[tagname.upper()] = matches[0].text[0]
    tags = []
    for t in _floattags:
        tags.append(t.lower())
        tags.append(t.upper())
    for tagname in _floattags:
        matches = id3.getall('TXXX:' + tagname)
        if len(matches) > 0:
            rg[tagname.upper()] = float(matches[0].text[0].split(' '
                    )[0])
    return rg


def add_to_apev2(rg, ape):
    """
    Adds/updates replaygain/mp3gain headers in APEv2 tag.

    :param id3: `mutagen.apev2.APEv2` to read
    """

    for tagname in _floattags + _stringtags:
        if tagname in ape:
            del ape[tagname]

    for tagname in rg.keys():
        ape[tagname] = str(rg[tagname])


def add_to_id3(rg, id3):
    """
    Adds/updates replaygain/mp3gain headers in ID3v2 tag, returns the
    number of updated tags.

    :param id3: `mutagen.id3.ID3` to read
    :rtype: int
    """

    old_rg = read_from_id3(id3)
    updated = 0

    # for tagname in _floattags + _stringtags:
    #    id3.delall('TXXX:' + tagname)

    for tagname in rg.keys():
        if tagname not in old_rg or old_rg[tagname] != rg[tagname] \
            or len(id3.getall('TXXX:' + tagname.lower())):
            updated += 1
            id3.delall('TXXX:' + tagname.upper())
            id3.delall('TXXX:' + tagname.lower())
            frame = mutagen.id3.Frames['TXXX'](encoding=3,
                    desc=tagname, text=str(rg[tagname]))
            id3.loaded_frame(frame)

    for tagname in old_rg.keys():
        if tagname not in rg.keys():
            updated += 1
            id3.delall('TXXX:' + tagname.upper())
            id3.delall('TXXX:' + tagname.lower())

    for tagname in _stringtags + _floattags:
        matches = id3.getall('TXXX:' + tagname.lower())
        if len(matches) > 0:
            updated += 1
            id3.delall('TXXX:' + tagname.lower())
            frame = mutagen.id3.Frames['TXXX'](encoding=3,
                    desc=tagname, text=matches[0].text)
            id3.loaded_frame(frame)

    rva2_tags = id3.getall('RVA2')
    for gtype in ['album', 'track']:
        gain_tag = 'REPLAYGAIN_' + gtype.upper() + '_GAIN'
        peak_tag = 'REPLAYGAIN_' + gtype.upper() + '_PEAK'
        if gain_tag in rg:
            rva2 = None
            for r in rva2_tags:
                if r.desc == gtype and r.channel == 1:
                    rva2 = r
                    try:
                        rva2_tags.remove(r)
                    except:
                        pass
                    break
            if not rva2:
                rva2 = mutagen.id3.Frames['RVA2'](channel=1, desc=gtype)
            peak = None
            gain = float(rg[gain_tag])
            if peak_tag in rg:
                peak = float(rg[peak_tag])
            rva2.gain = gain
            rva2.peak = peak
            rva2_tags.append(rva2)
    id3.delall('RVA2')
    for r in rva2_tags:
        id3.loaded_frame(r)

    return updated


def id3_to_ape(files):
    """
    Moves gain related tags from ID3v2 to APEv2, creating APEv2 if
    necessary.  **Note that ID3v2 tags are converted to ID3v2.4 before
    this process.**

    :param files: list of files to act on
    """

    for file in files:
        id3 = _get_mutagen_id3(file)
        ape = _get_mutagen_apev2(file)
        add_to_apev2(read_from_id3(id3), ape)
        ape.save(file)


def ape_to_id3(files, version=None):
    """
    Moves gain related tags from APEv2 to ID3v2, then deletes APEv2.

    :param files: list of files to act on
    :param version: ID3 tag version to save as (optional, tags will be ID3v2.4 if not provided)
    """

    for file in files:
        id3 = _get_mutagen_id3(file)
        ape = _get_mutagen_apev2(file)
        updated = add_to_id3(read_from_apev2(ape), id3)
        if updated > 0:
            print 'writing id3'
            id3.save(file)
        ape.delete(file)
        if version != None:
            pymp3utils.set_id3_version(file, version)


