# -*- coding: utf-8 -*-

"""
    g_octave.package_manager
    ~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements some Python classes for the implementation of
    the multiple package manager support.

    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

__all__ = [
    'Portage',
    'Pkgcore',
    'Paludis',
    'get_by_name',
]

import grp
import os
import pwd
import subprocess

from g_octave.config import Config
from g_octave.ebuild import Ebuild
from g_octave.compat import open

conf = Config()

class Base:
    
    _client = ''
    _group = None
    
    post_install = []
    post_uninstall = []
    
    check_overlay = lambda a,b,c: True
    create_manifest = lambda a,b: os.EX_OK
    
    def is_installed(self):
        if self._client != '':
            return os.path.exists(self._client)
        return False
    
    def do_ebuilds(self, packages):
        for package in packages:
            Ebuild(package[len('g-octave/'):], pkg_manager=self).create()
    
    def allowed_users(self):
        if self._group is None:
            return [i.pw_name for i in pwd.getpwall()]
        try:
            users = grp.getgrnam(self._group).gr_mem
        except KeyError:
            users = []
        # root is the master!!! :P
        if 'root' not in users:
            users.append('root')
        return users


class Portage(Base):
    
    _client = '/usr/bin/emerge'
    _group = 'portage'
    
    post_uninstall = [
        'You may want to remove the dependencies too, using:',
        '# emerge -av --depclean',
    ]
    
    def __init__(self, ask=False, verbose=False, pretend=False, oneshot=False, nocolor=False):
        self._fullcommand = [self._client]
        ask and self._fullcommand.append('--ask')
        verbose and self._fullcommand.append('--verbose')
        pretend and self._fullcommand.append('--pretend')
        oneshot and self._fullcommand.append('--oneshot')
        nocolor and self._fullcommand.append('--color=n')
    
    def run_command(self, command):
        return subprocess.call(self._fullcommand + command)
    
    def install_package(self, pkgatom, catpkg):
        return self.run_command([pkgatom])

    def uninstall_package(self, pkgatom, catpkg):
        return self.run_command(['--unmerge', catpkg])
    
    def update_package(self, pkgatom=None, catpkg=None):
        if catpkg is None:
            catpkg = self.installed_packages()
        else:
            catpkg = [catpkg]
        self.do_ebuilds(catpkg)
        return self.run_command(['--update'] + catpkg)
    
    def installed_packages(self):
        packages = []
        with open('/var/lib/portage/world') as fp:
            for line in fp:
                if line.startswith('g-octave/'):
                    packages.append(line.strip())
        return packages
    
    def create_manifest(self, ebuild):
        return subprocess.call(['ebuild', ebuild, 'manifest'])
    
    def check_overlay(self, overlay, out):
        import portage
        if overlay not in portage.settings['PORTDIR_OVERLAY'].split(' '):
            out.eerror('g-octave overlay is not configured!')
            out.eerror('You must append your overlay directory to PORTDIR_OVERLAY.')
            out.eerror('Overlay: %s' % overlay)
            return False
        return True


class Pkgcore(Base):
    
    _client = '/usr/bin/pmerge'
    _group = 'portage'
    
    post_uninstall = [
        'You may want to remove the dependencies too, using:',
        '# pmerge -av --clean',
    ]
    
    def __init__(self, ask=False, verbose=False, pretend=False, oneshot=False, nocolor=False):
        self._fullcommand = [self._client]
        ask and self._fullcommand.append('--ask')
        verbose and self._fullcommand.append('--verbose')
        pretend and self._fullcommand.append('--pretend')
        oneshot and self._fullcommand.append('--oneshot')
        nocolor and self._fullcommand.append('--nocolor')
    
    def run_command(self, command):
        return subprocess.call(self._fullcommand + command)
    
    def install_package(self, pkgatom, catpkg):
        return self.run_command([pkgatom])

    def uninstall_package(self, pkgatom, catpkg):
        return self.run_command(['--unmerge', catpkg])
    
    def update_package(self, pkgatom=None, catpkg=None):
        if catpkg is None:
            catpkg = self.installed_packages()
        else:
            catpkg = [catpkg]
        self.do_ebuilds(catpkg)
        return self.run_command(['--upgrade', '--noreplace'] + catpkg)
    
    def installed_packages(self):
        packages = []
        p = subprocess.Popen([
            'pquery',
            '--vdb',
            '--pkgset=world',
            '--no-version',
            'g-octave/*',
        ], stdout=subprocess.PIPE)
        if p.wait() == os.EX_OK:
            for line in p.stdout:
                packages.append(line.strip())
        return packages
    
    def create_manifest(self, ebuild):
        # using portage :(
        return subprocess.call(['ebuild', ebuild, 'manifest'])


class Paludis(Base):
    
    _client = '/usr/bin/paludis'
    _group = 'paludisbuild'
    
    post_uninstall = [
        'You may want to remove the dependencies too, using:',
        '# paludis --pretend --uninstall-unused',
    ]
    
    def __init__(self, ask=False, verbose=False, pretend=False, oneshot=False, nocolor=False):
        self._fullcommand = [self._client]
        self._oneshot = oneshot
        # paludis doesn't supports '--ask'
        if verbose:
            self._fullcommand += [
                '--show-reasons', 'full',
                '--show-use-descriptions', 'all',
                '--show-package-descriptions', 'all',
            ]
        pretend and self._fullcommand.append('--pretend')
        oneshot and self._fullcommand.append('--preserve-world')
        nocolor and self._fullcommand.append('--no-color')
    
    def run_command(self, command):
        return subprocess.call(self._fullcommand + command)
    
    def install_package(self, pkgatom, catpkg):
        cmd = [
            '--install',
            '--dl-upgrade', 'as-needed'
        ]
        if not self._oneshot:
            cmd += ['--add-to-world-spec', catpkg]
        cmd.append(pkgatom)
        return self.run_command(cmd)

    def uninstall_package(self, pkgatom, catpkg):
        return self.run_command(['--uninstall', catpkg])
    
    def update_package(self, pkgatom=None, catpkg=None):
        if catpkg is None:
            catpkg = self.installed_packages()
        else:
            catpkg = [catpkg]
        self.do_ebuilds(catpkg)
        return self.run_command([
            '--install',
            '--dl-upgrade', 'as-needed',
            '--dl-reinstall-targets', 'never',
        ] + catpkg)
    
    def installed_packages(self):
        packages = []
        p = subprocess.Popen([
            'cave',
            'print-ids',
            '--matching', 'g-octave/*::installed',
            '--format', '%c/%p\n',
        ], stdout=subprocess.PIPE)
        if p.wait() == os.EX_OK:
            for line in p.stdout:
                packages.append(line.strip())
        return packages


def get_by_name(name):
    if name.lower() == 'portage':
        return Portage
    elif name.lower() == 'paludis':
        return Paludis
    elif name.lower() == 'pkgcore':
        return Pkgcore
    else:
        return None
