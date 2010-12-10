# -*- coding: utf-8 -*-

"""
    description_tree.py
    ~~~~~~~~~~~~~~~~~~~
    
    This module implements a Python object with the content of a directory
    tree with DESCRIPTION files. The object contains *g_octave.Description*
    objects for each DESCRIPTION file.
    
    :copyright: (c) 2009-2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from __future__ import absolute_import

__all__ = ['DescriptionTree']

import os
import re

from portage.versions import vercmp

from .config import Config, ConfigException
from .description import *
from .exception import DescriptionTreeException
from .log import Log
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

class DescriptionTree(object):
    
    def __init__(self, parse_sysreq=True):
        
        log.info('Parsing the package database.')
        
        self._parse_sysreq = parse_sysreq
        self.pkg_list = {}
        self._db_path = os.path.join(config.db, 'octave-forge')
        
        if not os.path.isdir(self._db_path):
            log.error('Invalid db: %s' % self._db_path)
            raise DescriptionTreeException('Invalid db: %s' % self._db_path)
        
        self.categories = {}
        for cat in [i.strip() for i in config.categories.split(',')]:
            catdir = os.path.join(self._db_path, cat)
            if os.path.isdir(catdir):
                self.pkg_list[cat] = []
                pkgs = os.listdir(catdir)
                for pkg in pkgs:
                    pkgdir = os.path.join(catdir, pkg)
                    for desc_file in os.listdir(pkgdir):
                        pkg_p = desc_file[:-len('.DESCRIPTION')]
                        mypkg = re_pkg_atom.match(pkg_p)
                        if mypkg is None:
                            log.error('Invalid Atom: %s' % pkg_p)
                            raise DescriptionTreeException('Invalid Atom: %s' % pkg_p)
                        self.categories[mypkg.group(1)] = cat
                        self.pkg_list[cat].append({
                            'name': mypkg.group(1),
                            'version': mypkg.group(2),
                        })
    
    
    def __getitem__(self, key):
        
        mykey = re_pkg_atom.match(key)
        if mykey == None:
            return None
        
        name = mykey.group(1)
        version = mykey.group(2)
        
        for cat in self.pkg_list:
            for pkg in self.pkg_list[cat]:
                if pkg['name'] == name and pkg['version'] == version:
                    pkgfile = os.path.join(
                        self._db_path,
                        cat,
                        pkg['name'],
                        '%s-%s.DESCRIPTION' % (pkg['name'], pkg['version']),
                    )
                    return Description(pkgfile, parse_sysreq=self._parse_sysreq)
        
        return None
    
    
    def package_versions(self, pkgname):
        
        tmp = []
        
        for cat in self.pkg_list:
            for pkg in self.pkg_list[cat]:
                if pkg['name'] == pkgname:
                    tmp.append(pkg['version'])
        
        tmp.sort(key=cmp_to_key(vercmp))
        return tmp
        
    
    def latest_version(self, pkgname):
        
        tmp = self.package_versions(pkgname)
        return (len(tmp) > 0) and tmp[-1] or None


    def version_compare(self, versions):
        
        tmp = list(versions[:])
        tmp.sort(key=cmp_to_key(vercmp))
        return (len(tmp) > 0) and tmp[-1] or None

    
    def packages(self):
        
        packages = []
        
        for cat in self.pkg_list:
            for pkg in self.pkg_list[cat]:
                packages.append(pkg['name'] + '-' + pkg['version'])
        
        packages.sort()
        return packages

    
    def search(self, term):
        
        # term can be a regular expression
        re_term = re.compile(r'%s' % term)
        packages = {}
        
        for cat in self.pkg_list:
            for pkg in self.pkg_list[cat]:
                if re_term.search(pkg['name']) is not None:
                    if pkg['name'] not in packages:
                        packages[pkg['name']] = [pkg['version'], '9999']
                    else:
                        packages[pkg['name']].insert(-1, pkg['version'])
                    packages[pkg['name']].sort(key=cmp_to_key(vercmp))
        
        return packages

    def list(self):
        
        packages = {}
        
        for cat in self.pkg_list:
            packages[cat] = {}
            for pkg in self.pkg_list[cat]:
                if pkg['name'] not in packages[cat]:
                    packages[cat][pkg['name']] = [pkg['version'], '9999']
                else:
                    packages[cat][pkg['name']].insert(-1, pkg['version'])
                    packages[cat][pkg['name']].sort(key=cmp_to_key(vercmp))
        
        return packages
