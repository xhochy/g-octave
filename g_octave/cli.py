# -*- coding: utf-8 -*-

"""
    g_octave.cli
    ~~~~~~~~~~~~

    This module implements a command-line interface for g-octave.

    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from __future__ import absolute_import, print_function

import argparse
import getpass
import os
import portage
import tempfile
import traceback
import shutil
import sys

from .checksum import sha1_check_db
from .config import Config
from .description_tree import DescriptionTree
from .ebuild import Ebuild
from .exception import GOctaveError
from .fetch import fetch
from .log import Log
from .overlay import create_overlay
from .package_manager import get_by_name

config = Config()
log = Log('g_octave.cli')
out = portage.output.EOutput()


class Cli:

    bug_tracker = 'https://bugs.gentoo.org/'

    def __init__(self):
        log.info('Initializing g-octave.')

        self.parser = argparse.ArgumentParser(
            description='A tool that generates and installs ebuilds for the octave-forge packages'
        )

        self.parser.set_defaults(
            action=self.merge,
            scm=(config.use_scm.lower() == 'true')
        )

        self.actions = self.parser.add_mutually_exclusive_group()
        self.scm = self.parser.add_mutually_exclusive_group()

        self.actions.add_argument(
            '--sync',
            action = 'store_const',
            const = self.sync,
            dest = 'action',
            help = 'search for updates of the package database, patches and auxiliary files.'
        )

        self.actions.add_argument(
            '-l', '--list',
            action = 'store_const',
            const = self.list,
            dest = 'action',
            help = 'show a list of packages available to install (separed by categories) and exit.'
        )

        self.actions.add_argument(
            '--list-raw',
            action = 'store_const',
            const = self.list_raw,
            dest = 'action',
            help = 'show a list of packages available to install (a package per line, without colors) and exit.'
        )

        self.actions.add_argument(
            '-i', '--info',
            action = 'store_const',
            const = self.info,
            dest = 'action',
            help = 'show a description of the required package and exit.'
        )

        self.actions.add_argument(
            '-u', '--update',
            action = 'store_const',
            const = self.update,
            dest = 'action',
            help = 'try to update a package or all the installed packages, if no atom provided.'
        )

        self.actions.add_argument(
            '-s', '--search',
            action = 'store_const',
            const = self.search,
            dest = 'action',
            help = 'package search (regular expressions allowed).'
        )

        self.actions.add_argument(
            '-C', '--unmerge',
            action = 'store_const',
            const = self.unmerge,
            dest = 'action',
            help = 'try to unmerge a package, instead of merge.'
        )

        self.actions.add_argument(
            '--config',
            action = 'store_const',
            const = self.config,
            dest = 'action',
            help = 'return a value from the configuration file (/etc/g-octave.cfg)'
        )

        self.parser.add_argument(
            '-p', '--pretend',
            action = 'store_true',
            dest = 'pretend',
            help = 'don\'t (un)merge packages, only create ebuilds and solve the dependencies'
        )

        self.parser.add_argument(
            '-a', '--ask',
            action = 'store_true',
            dest = 'ask',
            help = 'ask for confirmation before perform (un)merges'
        )

        self.parser.add_argument(
            '-v', '--verbose',
            action = 'store_true',
            dest = 'verbose',
            help = 'package manager\'s makes a lot of noise.'
        )

        self.parser.add_argument(
            '-1', '--oneshot',
            action = 'store_true',
            dest = 'oneshot',
            help = 'do not add the packages to the world file for later updating.'
        )

        self.scm.add_argument(
            '--scm',
            action = 'store_true',
            dest = 'scm',
            help = 'enable the installation of the current live version of a package, if disabled on the configuration file'
        )

        self.scm.add_argument(
            '--no-scm',
            action = 'store_false',
            dest = 'scm',
            help = 'disable the installation of the current live version of a package, if enabled on the configuration file'
        )

        self.parser.add_argument(
            '--force',
            action = 'store_true',
            dest = 'force',
            help = 'forces the recreation of the ebuilds'
        )

        self.parser.add_argument(
            '--force-all',
            action = 'store_true',
            dest = 'force_all',
            help = 'forces the recreation of the overlay and of the ebuilds'
        )

        self.parser.add_argument(
            '--no-colors',
            action = 'store_false',
            dest = 'colors',
            help = 'don\'t use colors on the CLI'
        )

        self.parser.add_argument(
            'atom',
            metavar='ATOM',
            type=str,
            nargs='?',
            help='Package atom or regular expression (for search) or configuration key'
        )

    def _init_tree(self):
        log.info('Initializing DescriptionTree.')
        self.tree = DescriptionTree()

    def _required_atom(self):
        if self.args.atom is None:
            self.parser.error('You need to provide a positional argument')

    def _init_pkg_manager(self):
        log.info('Initializing Package Manager.')
        pm = get_by_name(config.package_manager)
        if pm is None:
            raise GOctaveError('Invalid package manager: %s' % config.package_manager)
        self.pkg_manager = pm(self.args.ask, self.args.verbose, self.args.pretend,
            self.args.oneshot, not self.args.colors)

        # checking if the package manager is installed
        if not self.pkg_manager.is_installed():
            raise GOctaveError('Package manager not installed: %s' % config.package_manager)

        current_user = getpass.getuser()
        if current_user not in self.pkg_manager.allowed_users():
            raise GOctaveError(
                'The current user (%s) can\'t run the current selected '
                'package manager (%s)' % (current_user, config.package_manager)
            )

        # checking if the overlay is properly configured
        if not self.pkg_manager.check_overlay(config.overlay, out):
            raise GOctaveError('Overlay not properly configured.')

    def _init_ebuild(self):
        log.info('Initializing Ebuild: %s' % self.args.atom)
        self._required_atom()
        self._init_pkg_manager()
        self._init_overlay()
        self.ebuild = Ebuild(self.args.atom, self.args.force, self.args.scm, \
            self.pkg_manager)
        self.pkgatom = '=g-octave/' + self.ebuild.description.P
        self.catpkg = 'g-octave/' + self.ebuild.description.PN

    def _init_overlay(self):
        log.info('Initializing Overlay.')
        create_overlay(self.args.force_all)

    def list(self):
        log.info('Listing packages.')
        self._init_tree()
        print()
        print(portage.output.blue('Available packages:'))
        print()
        packages = self.tree.list()
        for category in packages:
            print(
                portage.output.blue('Category:'),
                portage.output.white(category)
            )
            print()
            for pkg in packages[category]:
                print(
                    portage.output.green('    Package:'),
                    portage.output.white(pkg)
                )
                print(
                    portage.output.green('    Available versions:'),
                    portage.output.red(', '.join(packages[category][pkg]))
                )
                print()

    def list_raw(self):
        log.info('Listing packages (raw mode).')
        self._init_tree()
        packages = self.tree.list()
        for cat in packages:
            for pkg in packages[cat]:
                print(pkg)

    def info(self):
        log.info('Listing description of a package.')
        self._init_ebuild()
        pkg = self.ebuild.description
        print(portage.output.blue('Package:'), portage.output.white(str(pkg.name)))
        print(portage.output.blue('Version:'), portage.output.white(str(pkg.version)))
        print(portage.output.blue('Date:'), portage.output.white(str(pkg.date)))
        print(portage.output.blue('Maintainer:'), portage.output.white(str(pkg.maintainer)))
        print(portage.output.blue('Description:'), portage.output.white(str(pkg.description)))
        print(portage.output.blue('Categories:'), portage.output.white(str(pkg.categories)))
        print(portage.output.blue('License:'), portage.output.white(str(pkg.license)))
        print(portage.output.blue('Url:'), portage.output.white(str(pkg.url)))

    def update(self):
        self._init_pkg_manager()
        if self.args.atom is not None:
            log.info('Calling the package manager to update the package.')
            self._init_ebuild()
            ret = self.pkg_manager.update_package(self.pkgatom, self.catpkg)
        else:
            log.info('Calling the package manager to update all the installed packages.')
            ret = self.pkg_manager.update_package()
        if ret != os.EX_OK:
            raise GOctaveError('Update failed!')

    def search(self):
        self._init_tree()
        self._init_overlay()
        self._required_atom()
        log.info('Searching for packages: %s' % self.args.atom)
        print(
            portage.output.blue('Search results for '),
            portage.output.white(self.args.atom),
            portage.output.blue(':\n'),
            sep = ''
        )
        packages = self.tree.search(self.args.atom)
        for pkg in packages:
            print(
                portage.output.green('Package:'),
                portage.output.white(pkg)
            )
            print(
                portage.output.green('Available versions:'),
                portage.output.red(', '.join(packages[pkg]))
            )
            print()

    def merge(self):
        self._init_pkg_manager()
        self._init_ebuild()
        self._required_atom()
        log.info('Merging package: %s' % self.args.atom)
        self.ebuild.create()
        ret = self.pkg_manager.install_package(self.pkgatom, self.catpkg)
        if ret != os.EX_OK:
            raise GOctaveError('Merge failed!')

    def unmerge(self):
        self._init_pkg_manager()
        self._init_ebuild()
        self._required_atom()
        log.info('Unmerging package: %s' % self.args.atom)
        self.ebuild.create()
        ret = self.pkg_manager.uninstall_package(self.pkgatom, self.catpkg)
        if ret != os.EX_OK:
            raise GOctaveError('Unmerge failed!')

    def sync(self):
        log.info('Searching updates ...')
        out.einfo('Searching updates ...')

        if self.args.force and os.path.exists(config.db):
            shutil.rmtree(config.db)

        if not self.updates.fetch_db():
            log.info('No updates available')
            out.einfo('No updates available')
        else:
            self.updates.extract()
            log.info('Checking SHA1 checksums ...')
            out.ebegin('Checking SHA1 checksums')
            self._init_tree()
            if sha1_check_db(self.tree):
                out.eend(0)
            else:
                out.eend(1)
                if os.path.exists(config.db):
                    shutil.rmtree(config.db)
                raise GOctaveError('Package database SHA1 checksum failed!')

    def config(self):
        log.info('Retrieving configuration option.')
        self._required_atom()
        print(config.__getattr__(self.args.atom))

    def _run(self):
        log.info('Running the command-line interface.')
        self.args = self.parser.parse_args()
        if not self.args.colors:
            portage.output.nocolor()

        self.updates = fetch()

        # validating the db_mirror
        if self.updates is None:
            raise GOctaveError('Your db_mirror value is invalid. Fix it, or leave empty to use the default.')

        # checking if we have a package database
        if self.updates.need_update() and self.args.action != self.sync:
            raise GOctaveError('No package database found! Please run `g-octave --sync`')

        self.args.action()
        return os.EX_OK

    def run(self):
        try:
            return self._run()
        except GOctaveError as err:
            log.error(str(err))
            out.eerror(str(err))
            return os.EX_USAGE
        except Exception as err:
            tb = traceback.format_exc()
            log.error(tb)
            out.eerror('Unknown error - ' + str(err))
            fd, filename = tempfile.mkstemp(prefix='g-octave-', suffix='.log')
            error_log = 'Command: ' + ' '.join(sys.argv) + '\n\n' + tb
            if os.write(fd, error_log) != len(error_log):
                out.eerror('Failed to save the traceback!')
            else:
                out.eerror('Traceback saved: ' + filename)
            out.eerror('Please report a bug with traceback and `emerge --info` attached.')
            out.eerror('Bug tracker: ' + self.bug_tracker)
            os.fchmod(fd, 0o777)
            os.close(fd)
            return os.EX_SOFTWARE
