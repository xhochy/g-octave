# -*- coding: utf-8 -*-

"""
    checksum.py
    ~~~~~~~~~~~
    
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

from hashlib import sha1
import json
import os

from .config import Config
config = Config(True)


def sha1_compute(filename):
    with open(filename) as fp:
        return sha1(fp.read()).hexdigest()

def sha1_check(db, p):
    description = db[p]
    manifest = {}
    with open(os.path.join(config.db, 'manifest.json')) as fp:
        manifest = json.load(fp)
    if p not in manifest:
        return False
    return manifest[p] == description.sha1sum()

def sha1_check_db(db):
    for cat in db.pkg_list:
        for pkg in db.pkg_list[cat]:
            p = pkg['name']+'-'+pkg['version']
            if not sha1_check(db, p):
                return False
    return True
