==========
pymp3utils
==========

Utilities
=========

mp3gainer
---------

This is a simple wrapper for mp3gain_ and/or /aacgain_.  These tools
store their replaygain data in APEv2_ tags, which I don't use.  This
wrapper allows the tags to be stored in ID3v2_ tags instead (similar
to metamp3_).

.. _mp3gain: http://mp3gain.sourceforge.net/
.. _aacgain: http://altosdesign.com/aacgain/
.. _APEv2: http://en.wikipedia.org/wiki/APE_tag
.. _ID3v2: http://www.id3.org/
.. _metamp3: http://www.hydrogenaudio.org/forums/index.php?showtopic=49751

mp3sum
------

This is a utility for adding check-sum tags to mp3 files.  The checksum
is calculated on *only* the mp3 data frames, so changing meta-data on
the mp3 does not invalidate the checksum.  Any (and all) of the hash
algorithms supported by hashlib_ can be used.

I wrote this after a friend of mine had some hard drive issues on his
media drive, and was disappointed to find out there wasn't a way to
test the integrity of his mp3 files like he could with his flac_
files.::

  usage: mp3sum [-h] [-c] [-u] [-r] [-s [hash]] [-v] file [file ...]
  
  Manage checksums for mp3 audio data in ID3v2 tags
  
  positional arguments:
    file                  file(s) to process
  
  optional arguments:
    -h, --help            show this help message and exit
    -c, --check           verify checksums (default if no other
                          operation is requested)
    -u, --update          calculate and store checksum(s) from file(s)
                          that don't already have the requested
                          checksumtype(s)
    -r, --remove          remove stored checksum(s) from file(s)
    -s [hash], --sum-type [hash]
                          type(s) of checksum(s) to calculate
    -v, --verbose


.. _hashlib: http://docs.python.org/library/hashlib.html 
.. _flac: http://flac.sourceforge.net/
