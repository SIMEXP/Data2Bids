#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 16:26:45 2019

@author: ltetrel
"""

import unittest
from operations.operations import add

class Test(unittest.TestCase):
    def test_add(self):
        res = add(1, 2)
        self.assertEqual(res, 3)