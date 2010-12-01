# -*- coding: utf-8 -*-

"""
    g_octave.info
    ~~~~~~~~~~~~~

    This module implements a Python object to store the external dependencies
    and the licenses as named on the gentoo-x86 tree.

    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from __future__ import absolute_import
import json

# py3k compatibility
from .compat import open

__all__ = ['Info', 'InfoException']


class InfoException(Exception):
    pass


class Info(object):
    
    # dictionary with the dependencies
    dependencies = {}
    
    # dictionary with the licenses
    licenses = {}
    
    
    def __init__(self, filename):
        # try to read the file
        from_json = {}
        try:
            with open(filename) as fp:
                from_json = json.load(fp)
        except:
            raise InfoException('Failed to load JSON file: %r' % filename)
        else:
            if 'dependencies' in from_json:
                self.dependencies = from_json['dependencies']
            if 'licenses' in from_json:
                self.licenses = from_json['licenses']
