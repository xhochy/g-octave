# -*- coding: utf-8 -*-

"""
    g_octave.checksum
    ~~~~~~~~~~~~~~~~~
    
    This module implements functions for compute/generate SHA1 checksums
    for DESCRIPTION files.
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from __future__ import absolute_import

__all__ = [
    'sha1_compute',
    'sha1_check',
    'sha1_check_db',
]

import hashlib
import json
import os

from .config import Config
config = Config()


def sha1_compute(filename):
    '''Computes the SHA1 checksum of a file'''
    with open(filename, 'rb') as fp:
        return hashlib.sha1(fp.read()).hexdigest()

def sha1_check(db, p):
    '''Checks if the SHA1 checksum of the package is OK.'''
    description = db.get(p)
    manifest = {}
    with open(os.path.join(config.db, 'manifest.json')) as fp:
        manifest = json.load(fp)
    if p not in manifest:
        return False
    return manifest[p] == description.sha1sum()

def sha1_check_db(db):
    '''Checks if the SHA1 checksums of the package database are OK.'''
    for pkg in db:
        if not sha1_check(db, pkg.P):
            return False
    return True
