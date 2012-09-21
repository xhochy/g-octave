# -*- coding: utf-8 -*-

"""
    g_octave.config
    ~~~~~~~~~~~~~~~

    This module implements a Python object to handle the configuration
    of g-octave.

    :copyright: (c) 2009-2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from __future__ import absolute_import
import os

from .exception import GOctaveError

# py3k compatibility
from .compat import py3k
if py3k:
    import configparser
else:
    import ConfigParser as configparser

__all__ = ['Config']


class Config(object):

    _defaults = {
        'db': '/var/cache/g-octave',
        'overlay': '/var/lib/g-octave',
        'categories': 'main,extra,language',
        'db_mirror': 'github://rafaelmartins/g-octave-db',
        'trac_user': '',
        'trac_passwd': '',
        'log_level': '',
        'log_file': '/var/log/g-octave.log',
        'package_manager': 'portage',
        'use_scm': 'false',
    }

    _section_name = 'main'
    _environ_namespace = 'GOCTAVE_'


    def __init__(self, config_file=None):
        # config Parser
        self._config = configparser.ConfigParser(self._defaults)

        # current directory
        cwd = os.path.dirname(os.path.realpath(__file__))

        # no configuration file provided as parameter
        if config_file is None:
            # we just want one of the following configuration files:
            # '/etc/g-octave.cfg', '../etc/g-octave.cfg'
            available_files = [
                os.path.join('/etc', 'g-octave.cfg'),
                os.path.join(cwd, '..', 'etc', 'g-octave.cfg'),
            ]

            # get the first one available
            for my_file in available_files:
                if os.path.exists(my_file):
                    config_file = my_file
                    break

        # parse the wanted file using ConfigParser
        parsed_files = self._config.read(config_file)

        # no file to parsed
        if len(parsed_files) == 0:
            raise GOctaveError('File not found: %r' % config_file)

    def _evaluate_from_file(self, attr):
        # return the value from the configuration file
        try:
            return self._config.get(self._section_name, attr)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return None

    def _evaluate_from_environ(self, attr):
        # return the value from the environment variables namespace
        return os.environ.get(self._environ_namespace + attr.upper(), None)

    def __getattr__(self, attr):
        # valid attribute?
        if attr in self._defaults:
            # try the environment variable first
            from_env = self._evaluate_from_environ(attr)
            if from_env is not None:
                return from_env
            # default to the configuration file
            return self._evaluate_from_file(attr)
        else:
            raise GOctaveError('Invalid option: %r' % attr)
