# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="test_file.py">
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

from groupdocs_merger_cloud import FileInfo

class TestFile:
    """Test file"""

    @classmethod
    def not_exist(cls):
        f = TestFile()
        f.file_name = "not-exist.docx"
        f.folder = "somefolder/"
        return f

    @classmethod
    def one_page_docx(cls):
        f = TestFile()
        f.file_name = "one-page.docx"
        f.folder = "WordProcessing/"
        return f

    @classmethod
    def four_pages_docx(cls):
        f = TestFile()
        f.file_name = "four-pages.docx"
        f.folder = "WordProcessing/"
        return f

    @classmethod
    def password_protected_docx(cls):
        f = TestFile()
        f.file_name = "password-protected.docx"
        f.folder = "WordProcessing/"
        f.password = "password"
        return f

    @classmethod
    def four_sheets_xlsx(cls):
        f = TestFile()
        f.file_name = "four-sheets.xlsx"
        f.folder = "Spreadsheet/"
        return f

    @classmethod
    def password_protected_xlsx(cls):
        f = TestFile()
        f.file_name = "four-sheets-protected.xlsx"
        f.folder = "Spreadsheet/"
        f.password = "password"
        return f

    @classmethod
    def document_txt(cls):
        f = TestFile()
        f.file_name = "document.txt"
        f.folder = "Text/"
        return f

    @classmethod
    def ten_pages_pdf(cls):
        f = TestFile()
        f.file_name = "ten-pages.pdf"
        f.folder = "Pdf/"
        return f

    @classmethod
    def one_page_protected_pdf(cls):
        f = TestFile()
        f.file_name = "one-page-password.pdf"
        f.folder = "Pdf/"
        f.password = "password"
        return f                                

    @classmethod
    def get_test_files(cls):
        return [
            cls.one_page_docx(),
            cls.four_pages_docx(),
            cls.password_protected_docx(),
            cls.four_sheets_xlsx(),
            cls.password_protected_xlsx(),
            cls.document_txt(),
            cls.ten_pages_pdf(),
            cls.one_page_protected_pdf()
        ]

    def ToFileInfo(self):
        f = FileInfo()
        f.file_path = self.folder + self.file_name
        if hasattr(self, 'password'):
            f.password = self.password
        return f
