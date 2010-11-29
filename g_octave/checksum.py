# -*- coding: utf-8 -*-

"""
    checksum.py
    ~~~~~~~~~~~
    
    This module implements functions for compute/generate SHA1 checksums
    for files.
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from __future__ import absolute_import

__all__ = [
    'sha1_compute',
    'sha1_check',
]

from .compat import open
from hashlib import sha1


def sha1_compute(filename):
    with open(filename) as fp:
        return sha1(fp.read()).hexdigest()

def sha1_check(filename, checksum):
    return sha1_compute(filename) == checksum
