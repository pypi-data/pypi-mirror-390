# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd">
#   Copyright (c) Aspose Pty Ltd
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# -----------------------------------------------------------------------------------

from __future__ import absolute_import

import unittest
import datetime
from groupdocs_merger_cloud import *
from test.test_context import TestContext
from test.test_file import TestFile

class TestSecurityApi(TestContext):
    """MergerApi unit tests"""

    def test_check_password(self):
        test_file = TestFile.four_pages_docx()
        result = self.security_api.check_password(CheckPasswordRequest(test_file.folder + test_file.file_name))
        self.assertEqual(False, result.is_password_set) 

    def test_check_password_protected(self):
        test_file = TestFile.password_protected_docx()
        result = self.security_api.check_password(CheckPasswordRequest(test_file.folder + test_file.file_name))
        self.assertEqual(True, result.is_password_set)         

    def test_remove_password(self):
        test_file = TestFile.password_protected_docx()
        options = Options()
        options.file_info = test_file.ToFileInfo()
        options.output_path = self.output_path + test_file.file_name
        result = self.security_api.remove_password(RemovePasswordRequest(options))
        self.assertEqual(options.output_path, result.path)

    def test_add_password(self):
        test_file = TestFile.four_pages_docx()
        options = Options()
        options.file_info = test_file.ToFileInfo()
        options.file_info.password = "NewPassword"
        options.output_path = self.output_path + test_file.file_name
        result = self.security_api.add_password(AddPasswordRequest(options))
        self.assertEqual(options.output_path, result.path)  

    def test_update_password(self):
        test_file = TestFile.password_protected_docx()
        options = UpdatePasswordOptions()
        options.file_info = test_file.ToFileInfo()
        options.output_path = self.output_path + test_file.file_name
        options.new_password = "NewPassword"
        result = self.security_api.update_password(UpdatePasswordRequest(options))
        self.assertEqual(options.output_path, result.path)                 

if __name__ == '__main__':
    unittest.main()
