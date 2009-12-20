#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    'DescriptionTree',
    'DescriptionTreeException',
]

from config import Config
conf = Config()

from description import *

import os

class DescriptionTreeException(Exception):
    pass


class DescriptionTree(object):
    
    def __init__(self):
        
        self.pkg_list = {}
        
        self.__db_path = conf.db+'/octave-forge'
        
        if not os.path.isdir(self.__db_path):
            raise DescriptionTreeException('Invalid db: %s' % self.__db_path)
        
        for cat in [i.strip() for i in conf.categories.split(',')]:
            catdir = os.path.join(self.__db_path, cat)
            if os.path.isdir(catdir):
                self.pkg_list[cat] = []
                pkgs = os.listdir(catdir)
                for pkg in pkgs:
                    mypkg = re_pkg_atom.match(pkg)
                    if mypkg == None:
                        raise DescriptionTreeException('Invalid Atom: %s' % mypkg)
                    if mypkg.group(1) not in conf.blacklist:
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
                        self.__db_path,
                        cat,
                        '%s-%s' % (pkg['name'], pkg['version']),
                        'DESCRIPTION'
                    )
                    return Description(pkgfile)
        
        return None
    
    
    def package_versions(self, pkgname):
        
        tmp = []
        
        for cat in self.pkg_list:
            for pkg in self.pkg_list[cat]:
                if pkg['name'] == pkgname:
                    tmp.append(pkg['version'])
        
        return tmp
        
    
    def latest_version(self, pkgname):
        
        tmp = self.package_versions(pkgname)
        return self.version_compare(tmp)


    def version_compare(self, versions):
        
        max = ('0',)
        maxstr = None
        
        for version in versions:
            tmp = tuple(version.split('.'))
            if tmp > max:
                max = tmp
                maxstr = version
        
        return maxstr
        


if __name__ == '__main__':
    a = DescriptionTree()
    print a.latest_version('parallel')
