# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="MixPagesItem.py">
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

import pprint
import re  # noqa: F401

import six

class MixPagesItem(object):
    """
    Defines item options for documents MixPages method
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'file_index': 'int',
        'pages': 'list[int]'
    }

    attribute_map = {
        'file_index': 'FileIndex',
        'pages': 'Pages'
    }

    def __init__(self, file_index=None, pages=None, **kwargs):  # noqa: E501
        """Initializes new instance of MixPagesItem"""  # noqa: E501

        self._file_index = None
        self._pages = None

        if file_index is not None:
            self.file_index = file_index
        if pages is not None:
            self.pages = pages
    
    @property
    def file_index(self):
        """
        Gets the file_index.  # noqa: E501

        Index of the file from MixPagesOptions.Files collection.  # noqa: E501

        :return: The file_index.  # noqa: E501
        :rtype: int
        """
        return self._file_index

    @file_index.setter
    def file_index(self, file_index):
        """
        Sets the file_index.

        Index of the file from MixPagesOptions.Files collection.  # noqa: E501

        :param file_index: The file_index.  # noqa: E501
        :type: int
        """
        if file_index is None:
            raise ValueError("Invalid value for `file_index`, must not be `None`")  # noqa: E501
        self._file_index = file_index
    
    @property
    def pages(self):
        """
        Gets the pages.  # noqa: E501

        List of page numbers to use in a MixPages operation. NOTE: page numbering starts from 1.  # noqa: E501

        :return: The pages.  # noqa: E501
        :rtype: list[int]
        """
        return self._pages

    @pages.setter
    def pages(self, pages):
        """
        Sets the pages.

        List of page numbers to use in a MixPages operation. NOTE: page numbering starts from 1.  # noqa: E501

        :param pages: The pages.  # noqa: E501
        :type: list[int]
        """
        self._pages = pages

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, MixPagesItem):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
