# -*- coding: utf-8 -*-

"""
    test_description_tree.py
    ~~~~~~~~~~~~~~~~~~~~~~~~
    
    test suite for the *g_octave.description_tree* module
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
import shutil
import unittest
import testcase

from g_octave import description, description_tree


class TestDescriptionTree(testcase.TestCase):
    
    def setUp(self):
        testcase.TestCase.setUp(self)
        self._tree = description_tree.DescriptionTree()
    
    def test_package_versions(self):
        versions = {
            'main1': ['0.0.1'],
            'main2': ['0.0.1', '0.0.2'],
            'extra1': ['0.0.1'],
            'extra2': ['0.0.1', '0.0.2'],
            'language1': ['0.0.1'],
            'language2': ['0.0.1', '0.0.2'],
        }
        for pkg in versions:
            ver = self._tree.package_versions(pkg)
            ver.sort()
            versions[pkg].sort()
            self.assertEqual(versions[pkg], ver)
    
    def test_latest_version(self):
        versions = {
            'main1': '0.0.1',
            'main2': '0.0.2',
            'extra1': '0.0.1',
            'extra2': '0.0.2',
            'language1': '0.0.1',
            'language2': '0.0.2',
        }
        for pkg in versions:
            self.assertEqual(
                versions[pkg],
                self._tree.latest_version(pkg)
            )
    
    def test_latest_version_from_list(self):
        # TODO: cover a better range of versions
        versions = [
            # ([version1, version2], latest_version)
            (['1', '2'], '2'),
            (['0.1', '1'], '1'),
            (['0.1', '0.2'], '0.2'),
            (['0.0.1', '1'], '1'),
            (['0.0.1', '0.1'], '0.1'),
            (['0.0.1', '0.0.2'], '0.0.2'),
            (['2', '1'], '2'),
            (['1', '0.1'], '1'),
            (['0.2', '0.1'], '0.2'),
            (['1', '0.0.1'], '1'),
            (['0.1', '0.0.1'], '0.1'),
            (['0.0.2', '0.0.1'], '0.0.2'),
        ]
        for ver, latest in versions:
            self.assertEqual(self._tree.latest_version_from_list(ver), latest)
    
    def test_description_files(self):
        packages = [
            'main1-0.0.1',
            'main2-0.0.1',
            'main2-0.0.2',
            'extra1-0.0.1',
            'extra2-0.0.1',
            'extra2-0.0.2',
            'language1-0.0.1',
            'language2-0.0.1',
            'language2-0.0.2',
        ]
        for pkg in packages:
            self.assertTrue(
                isinstance(
                    self._tree.get(pkg),
                    description.Description
                )
            )


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestDescriptionTree('test_package_versions'))
    suite.addTest(TestDescriptionTree('test_latest_version'))
    suite.addTest(TestDescriptionTree('test_latest_version_from_list'))
    suite.addTest(TestDescriptionTree('test_description_files'))
    return suite
