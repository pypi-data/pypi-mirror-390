#!/usr/bin/env python
# # -*- coding: utf-8 -*-
# # File: exceptions.py
# #
# # Copyright 2018 Wim van den Herik
# #
# # Permission is hereby granted, free of charge, to any person obtaining a copy
# #  of this software and associated documentation files (the "Software"), to
# #  deal in the Software without restriction, including without limitation the
# #  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# #  sell copies of the Software, and to permit persons to whom the Software is
# #  furnished to do so, subject to the following conditions:
# #
# # The above copyright notice and this permission notice shall be included in
# #  all copies or substantial portions of the Software.
# #
# # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# #  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# #  FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# #  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# #  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# #  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# #  DEALINGS IN THE SOFTWARE.
#
""" Helper objects for pyatagone """

__author__ = '''Wim van den Herik'''
__docFormat__ = 'plaintext'
__date__ = '''27-09-2025'''
__copyright__ = '''Copyright 2025, Wim van den Herik'''
__credits__ = ["Wim van den Herik"]
__license__ = '''MIT'''
__maintainer__ = '''Wim van den Herik'''
__email__ = '''<wvdh2002@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


class AtagNotPaired(Exception):
    """ Calling client not paired with Atag One """

class AtagInvalidResponse(Exception):
    """ Invalid response is received from Atag One """
    
class AtagStatusException(Exception):
    """ Status Exception for status other then 2 """
    
class AtagConnectException(Exception):
    """ Atag Connection Exception """
