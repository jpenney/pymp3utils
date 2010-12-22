#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import eyeD3
from pymp3utils import get_tag, find_frame, convert_frame


def gain2sc(gain, base):
    result = round(10 ** (-1 * float(gain.split(' ')[0]) / 10) * base)
    if result > 65534:
        result = 65534

    return '%08x' % result


def update_soundcheck(target):
    """
    """

    tag = get_tag(target)

    count = 0

    gain = find_frame(tag, 'REPLAYGAIN_TRACK_GAIN', 'TXXX')
    if not gain:
        gain = find_frame(tag, 'replaygain_track_gain', 'TXXX')
    peak = find_frame(tag, 'REPLAYGAIN_TRACK_PEAK', 'TXXX')
    if not peak:
            peak = find_frame(tag, 'replaygain_track_peak', 'TXXX')

    if gain != None and peak != None:
        soundcheck = []
        soundcheck.append(gain2sc(gain.text, 1000))
        soundcheck.append(soundcheck[0])
        soundcheck.append(gain2sc(gain.text, 2500))
        soundcheck.append(soundcheck[2])
        soundcheck.append('00024CA8')
        soundcheck.append(soundcheck[4])
        soundcheck.append('00007FFF')
        soundcheck.append(soundcheck[6])
        soundcheck.append(soundcheck[4])
        soundcheck.append(soundcheck[4])

        newval = ' '.join(soundcheck)

        iTunNORM = find_frame(tag, 'iTunNORM', 'COMM')

        if iTunNORM == None:
            header = eyeD3.frames.FrameHeader()
            header.id = 'COMM'
            header.compressed = 0
            iTunNORM = eyeD3.frames.CommentFrame(header, None, '',
                    u'iTunNORM')
            tag.frames.addFrame(iTunNORM)

        if iTunNORM.comment != newval:
            count += 1
            iTunNORM.comment = newval

    return count

def fix_sort_tag(target):
    pass
