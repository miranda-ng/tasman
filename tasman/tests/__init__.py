# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
#

import os.path
import unittest


def main():
    suite = unittest.TestSuite()
    for root, dirs, files in os.walk('.'):
        for file in files:
            if not (file.startswith('test_') and file.endswith('.py')):
                continue
            name = file.split('.')[0]
            modname = os.path.join(root, name).replace(os.path.sep, '.')
            modname = modname.lstrip('.')
            try:
                tests = unittest.defaultTestLoader.loadTestsFromName(modname)
            except Exception, err:
                print modname, ':', type(err), err
            else:
                for test in tests:
                    suite.addTests(test)
                print modname, ':', tests.countTestCases(), 'tests'
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='main')
