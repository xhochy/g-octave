# -*- coding: utf-8 -*-

"""
    g_octave.description_tree
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    This module implements a Python object with the content of a directory
    tree with DESCRIPTION files. The object contains *g_octave.Description*
    objects for each DESCRIPTION file.
    
    :copyright: (c) 2009-2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from __future__ import absolute_import

__all__ = ['DescriptionTree']

import glob
import os
import re

from .config import Config
from .description import Description
from .log import Log
from portage.versions import vercmp

log = Log('g_octave.description_tree')
config = Config()


# from http://wiki.python.org/moin/HowTo/Sorting/
def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    
    return K


class DescriptionTree(list):
    
    def __init__(self, parse_sysreq=True):
        log.info('Parsing the package database.')
        list.__init__(self)
        self._categories = [i.strip() for i in config.categories.split(',')]
        for my_file in glob.glob(os.path.join(config.db, 'octave-forge', \
                                              '**', '**', '*.DESCRIPTION')):
            description = Description(my_file, parse_sysreq=parse_sysreq)
            if description.CAT in self._categories:
                self.append(description)
    
    def package_versions(self, pn):
        tmp = []
        for pkg in self:
            if pkg.PN == pn:
                tmp.append(pkg.PV)
        tmp.sort(key=cmp_to_key(vercmp))
        return tmp
    
    def latest_version(self, pn):
        tmp = self.package_versions(pn)
        return (len(tmp) > 0) and tmp[-1] or None

    def latest_version_from_list(self, pv_list):
        tmp = pv_list[:]
        tmp.sort(key=cmp_to_key(vercmp))
        return (len(tmp) > 0) and tmp[-1] or None
    
    def search(self, term):
        # term can be a regular expression
        re_term = re.compile(r'%s' % term)
        packages = {}
        for pkg in self:
            if re_term.search(pkg.PN) is not None:
                if pkg.PN not in packages:
                    packages[pkg.PN] = []
                packages[pkg.PN].append(pkg.PV)
                packages[pkg.PN].sort(key=cmp_to_key(vercmp))
        return packages

    def list(self):
        packages = {}
        for category in self._categories:
            packages[category] = {}
        for pkg in self:
            if pkg.PN not in packages[pkg.CAT]:
                packages[pkg.CAT][pkg.PN] = []
            packages[pkg.CAT][pkg.PN].append(pkg.PV)
            packages[pkg.CAT][pkg.PN].sort(key=cmp_to_key(vercmp))
        return packages
    
    def get(self, p):
        for pkg in self:
            if pkg.P == p:
                return pkg
        return None
