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

class TestDocumentApi(TestContext):
    """MergerApi unit tests"""

    def test_split_pages(self):
        test_file = TestFile.four_pages_docx()
        options = SplitOptions()
        options.file_info = test_file.ToFileInfo()
        options.output_path = self.output_path + test_file.file_name
        options.pages = [2, 4]
        options.mode = "Pages"
        result = self.document_api.split(SplitRequest(options))
        self.assertEqual(2, len(result.documents))

    def test_split_pages_protected(self):
        test_file = TestFile.password_protected_docx()
        options = SplitOptions()
        options.file_info = test_file.ToFileInfo()
        options.output_path = self.output_path + test_file.file_name
        options.pages = [2, 4]
        options.mode = "Pages"
        result = self.document_api.split(SplitRequest(options))
        self.assertEqual(2, len(result.documents))

    def test_preview(self):
        test_file = TestFile.four_pages_docx()
        options = PreviewOptions()
        options.file_info = test_file.ToFileInfo()
        options.output_path = self.output_path + test_file.file_name
        options.pages = [2, 4]
        options.width = 600
        options.height = 900
        options.format = "Png"
        result = self.document_api.preview(PreviewRequest(options))
        self.assertEqual(2, len(result.documents))

    def test_preview_protected(self):
        test_file = TestFile.password_protected_docx()
        options = PreviewOptions()
        options.file_info = test_file.ToFileInfo()
        options.output_path = self.output_path + test_file.file_name
        options.pages = [2, 4]
        options.width = 600
        options.height = 900
        options.format = "Png"
        result = self.document_api.preview(PreviewRequest(options))
        self.assertEqual(2, len(result.documents))

    def test_join(self):
        item1 = JoinItem()
        item1.file_info = TestFile.password_protected_docx().ToFileInfo()
        item2 = JoinItem()
        item2.file_info = TestFile.four_pages_docx().ToFileInfo()        
        options = JoinOptions()
        options.join_items = [item1, item2]
        options.output_path = self.output_path + "joined.docx"
        result = self.document_api.join(JoinRequest(options))
        self.assertEqual(options.output_path, result.path)

    def test_join_cross_format(self):
        item1 = JoinItem()
        item1.file_info = TestFile.one_page_protected_pdf().ToFileInfo()
        item2 = JoinItem()
        item2.file_info = TestFile.four_pages_docx().ToFileInfo()        
        options = JoinOptions()
        options.join_items = [item1, item2]
        options.output_path = self.output_path + "joined.pdf"
        result = self.document_api.join(JoinRequest(options))
        self.assertEqual(options.output_path, result.path)     

    def test_import(self):
        options = ImportOptions()
        options.file_info = TestFile.one_page_protected_pdf().ToFileInfo()
        options.attachments = [TestFile.document_txt().ToFileInfo().file_path]
        options.output_path = self.output_path + "with-attachment.pdf"
        result = self.document_api.call_import(CallImportRequest(options))
        self.assertEqual(options.output_path, result.path)              

if __name__ == '__main__':
    unittest.main()
