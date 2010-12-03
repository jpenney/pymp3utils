
import eyeD3
import hashlib
import mp3 as MP3
from pymp3utils import get_filepath, get_tag

sum_type_default = 'sha256'
owner_id_prefix = 'mp3sum'


def get_key(sum_type=sum_type_default):
    return '_'.join([owner_id_prefix, sum_type])


def get_sum_frame(target, sum_type=sum_type_default):
    tag = get_tag(target)
    key = get_key(sum_type)
    for utf in tag.getUserTextFrames():
        if utf.description == key:
            return utf

    return None


def read_sum(target, sum_type=sum_type_default):
    frame = get_sum_frame(target, sum_type)
    if isinstance(frame, eyeD3.frames.UserTextFrame):
        return frame.text
    return None


def set_sum_frame(target, hash):
    tag = get_tag(target)
    key = get_key(hash.name)
    tag.addUserTextFrame(key, hash.hexdigest())


def remove_sum_frame(target, sum_type=sum_type_default):
    tag = get_tag(target)
    key = get_key(sum_type)
    tag.addUniqueFileID(key, None)
    tag.removeUserTextFrame(key)


def calculate_sum(target, sum_type=sum_type_default):
    hgen = hashlib.new(sum_type)
    f = open(get_filepath(target), "rb")
    for hdr, frm in MP3.frames(f):
        hgen.update(frm)
    return hgen


def validate_file(file):
    tag = get_tag(file)
    sums = []
    results = []
    for utf in tag.getUserTextFrames():
        if utf.description.startswith(owner_id_prefix):
            sum_type = utf.description.split('_')[1]
            sums.append((sum_type, utf.text))
    for sum_type, sum_data in sums:
        calc = calculate_sum(file, sum_type)
        results.append((sum_type, (calc.hexdigest() == sum_data)))
    return results
