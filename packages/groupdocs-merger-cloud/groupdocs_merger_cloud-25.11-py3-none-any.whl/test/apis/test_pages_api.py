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

class TestPagesApi(TestContext):
    """MergerApi unit tests"""

    def test_move(self):
        test_file = TestFile.four_pages_docx()
        options = MoveOptions()
        options.file_info = test_file.ToFileInfo()
        options.output_path = self.output_path + test_file.file_name
        options.page_number = 1
        options.new_page_number = 2
        result = self.pages_api.move(MoveRequest(options))
        self.assertEqual(options.output_path, result.path)

    def test_move_protected(self):
        test_file = TestFile.password_protected_docx()
        options = MoveOptions()
        options.file_info = test_file.ToFileInfo()
        options.output_path = self.output_path + test_file.file_name
        options.page_number = 1
        options.new_page_number = 2
        result = self.pages_api.move(MoveRequest(options))
        self.assertEqual(options.output_path, result.path)

    def test_remove(self):
        test_file = TestFile.four_sheets_xlsx()
        options = RemoveOptions()
        options.file_info = test_file.ToFileInfo()
        options.output_path = self.output_path + test_file.file_name
        options.pages = [2, 4]        
        result = self.pages_api.remove(RemoveRequest(options))
        self.assertEqual(options.output_path, result.path)

    def test_remove_protected(self):
        test_file = TestFile.password_protected_xlsx()
        options = RemoveOptions()
        options.file_info = test_file.ToFileInfo()
        options.output_path = self.output_path + test_file.file_name
        options.pages = [2, 4]        
        result = self.pages_api.remove(RemoveRequest(options))
        self.assertEqual(options.output_path, result.path)

    def test_rotate(self):
        test_file = TestFile.ten_pages_pdf()
        options = RotateOptions()
        options.file_info = test_file.ToFileInfo()
        options.output_path = self.output_path + test_file.file_name
        options.pages = [2, 4]     
        options.mode = "Rotate90"   
        result = self.pages_api.rotate(RotateRequest(options))
        self.assertEqual(options.output_path, result.path)

    def test_rotate_protected(self):
        test_file = TestFile.one_page_protected_pdf()
        options = RotateOptions()
        options.file_info = test_file.ToFileInfo()
        options.output_path = self.output_path + test_file.file_name
        options.pages = [1]     
        options.mode = "Rotate90"   
        result = self.pages_api.rotate(RotateRequest(options))
        self.assertEqual(options.output_path, result.path)

    def test_swap(self):
        test_file = TestFile.four_pages_docx()
        options = SwapOptions()
        options.file_info = test_file.ToFileInfo()
        options.output_path = self.output_path + test_file.file_name
        options.first_page_number = 2   
        options.second_page_number = 4
        result = self.pages_api.swap(SwapRequest(options))
        self.assertEqual(options.output_path, result.path)

    def test_swap_protected(self):
        test_file = TestFile.password_protected_docx()
        options = SwapOptions()
        options.file_info = test_file.ToFileInfo()
        options.output_path = self.output_path + test_file.file_name
        options.first_page_number = 2   
        options.second_page_number = 4
        result = self.pages_api.swap(SwapRequest(options))
        self.assertEqual(options.output_path, result.path)

    def test_extract(self):
        test_file = TestFile.four_pages_docx()
        options = ExtractOptions()
        options.file_info = test_file.ToFileInfo()
        options.output_path = self.output_path + test_file.file_name
        options.pages = [2, 4]
        result = self.pages_api.extract(ExtractRequest(options))
        self.assertEqual(options.output_path, result.path)

    def test_extract_protected(self):
        test_file = TestFile.password_protected_docx()
        options = ExtractOptions()
        options.file_info = test_file.ToFileInfo()
        options.output_path = self.output_path + test_file.file_name
        options.pages = [2, 4]
        result = self.pages_api.extract(ExtractRequest(options))
        self.assertEqual(options.output_path, result.path)

    def test_orientation(self):
        test_file = TestFile.four_pages_docx()
        options = OrientationOptions()
        options.file_info = test_file.ToFileInfo()
        options.output_path = self.output_path + test_file.file_name
        options.pages = [2, 4]
        options.mode = "Landscape"
        result = self.pages_api.orientation(OrientationRequest(options))
        self.assertEqual(options.output_path, result.path)

    def test_orientation_protected(self):
        test_file = TestFile.password_protected_docx()
        options = OrientationOptions()
        options.file_info = test_file.ToFileInfo()
        options.output_path = self.output_path + test_file.file_name
        options.pages = [2, 4]
        options.mode = "Landscape"
        result = self.pages_api.orientation(OrientationRequest(options))
        self.assertEqual(options.output_path, result.path)        

if __name__ == '__main__':
    unittest.main()
