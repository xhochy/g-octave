# -*- coding: utf-8 -*-

"""
    test_checksum.py
    ~~~~~~~~~~~~~~~~
    
    test suite for the *g_octave.checksum* module
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
import tempfile
import unittest
import testcase

from g_octave import checksum, description_tree


class TestChecksum(testcase.TestCase):
    
    def setUp(self):
        testcase.TestCase.setUp(self)
        self._tempfile = tempfile.mkstemp()[1]
        with open(self._tempfile, 'w') as fp:
            # SHA1 checksum: 8aa49f56d049193b183cb2918f8fb59e0caf1283
            fp.write("I'm the walrus\n")
    
    def test_filechecksum(self):
        my_checksum = checksum.sha1_compute(self._tempfile)
        self.assertEqual(my_checksum, '8aa49f56d049193b183cb2918f8fb59e0caf1283')
    
    def test_dbchecksum(self):
        self.assertTrue(checksum.sha1_check_db(description_tree.DescriptionTree()))

    def tearDown(self):
        testcase.TestCase.tearDown(self)
        os.unlink(self._tempfile)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestChecksum('test_filechecksum'))
    suite.addTest(TestChecksum('test_dbchecksum'))
    return suite
