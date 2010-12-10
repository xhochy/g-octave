# -*- coding: utf-8 -*-

"""
    testcase.py
    ~~~~~~~~~~~
    
    Custom test-case class for g-octave. The g_octave.config test suite
    SHOULD NOT inherit this class.
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
import shutil
import tempfile
import unittest

from g_octave.config import Config


class TestCase(unittest.TestCase):
    
    def setUp(self):
        self._tempdir = tempfile.mkdtemp()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        os.environ['GOCTAVE_DB'] = os.path.join(current_dir, 'files')
        os.environ['GOCTAVE_OVERLAY'] = os.path.join(self._tempdir, 'overlay')
        self._config = Config()
    
    def tearDown(self):
        shutil.rmtree(self._tempdir)
        del os.environ['GOCTAVE_DB']
        del os.environ['GOCTAVE_OVERLAY']
