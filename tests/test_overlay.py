#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test_overlay.py
    ~~~~~~~~~~~~~~~
    
    test suite for the *g_octave.overlay* module
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
import unittest
import testcase

from g_octave import config, overlay


class TestOverlay(testcase.TestCase):

    def test_overlay(self):
        overlay.create_overlay(quiet=True)
        files = {
            os.path.join(self._config.overlay, 'profiles', 'repo_name'): 'g-octave',
            os.path.join(self._config.overlay, 'profiles', 'categories'): 'g-octave',
        }
        for _file in files:
            self.assertTrue(os.path.exists(_file))
            with open(_file) as fp:
                self.assertEqual(fp.read(), files[_file])
        self.assertTrue(os.path.islink(
            os.path.join(self._config.overlay, 'eclass', 'g-octave.eclass')
        ))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestOverlay('test_overlay'))
    return suite
        
