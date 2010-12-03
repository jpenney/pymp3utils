import eyeD3


def get_tag(target):
    if (isinstance(target, eyeD3.Tag)):
        return target
    if (isinstance(target, eyeD3.TagFile)):
        return target.getTag()
    if (isinstance(target, str)):
        return eyeD3.Mp3AudioFile(target).getTag()
    raise TypeError("unable to convert to eyeD3.Tag: %s" % str(target))


def get_filepath(target):
    if (isinstance(target, str)):
        return target
    if (isinstance(target, file)):
        return target.name
    if (isinstance(target, eyeD3.TagFile)):
        return target.fileName
    if (isinstance(target, eyeD3.Tag)):
        return target.linkedFile.name
    raise TypeError("unable to convert to filepath: %s" % str(target))
