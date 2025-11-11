# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="JoinItem.py">
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

class JoinItem(object):
    """
    Describes document for join operation.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'file_info': 'FileInfo',
        'pages': 'list[int]',
        'start_page_number': 'int',
        'end_page_number': 'int',
        'range_mode': 'str',
        'word_join_mode': 'str',
        'word_join_compliance': 'str',
        'image_join_mode': 'str'
    }

    attribute_map = {
        'file_info': 'FileInfo',
        'pages': 'Pages',
        'start_page_number': 'StartPageNumber',
        'end_page_number': 'EndPageNumber',
        'range_mode': 'RangeMode',
        'word_join_mode': 'WordJoinMode',
        'word_join_compliance': 'WordJoinCompliance',
        'image_join_mode': 'ImageJoinMode'
    }

    def __init__(self, file_info=None, pages=None, start_page_number=None, end_page_number=None, range_mode=None, word_join_mode=None, word_join_compliance=None, image_join_mode=None, **kwargs):  # noqa: E501
        """Initializes new instance of JoinItem"""  # noqa: E501

        self._file_info = None
        self._pages = None
        self._start_page_number = None
        self._end_page_number = None
        self._range_mode = None
        self._word_join_mode = None
        self._word_join_compliance = None
        self._image_join_mode = None

        if file_info is not None:
            self.file_info = file_info
        if pages is not None:
            self.pages = pages
        if start_page_number is not None:
            self.start_page_number = start_page_number
        if end_page_number is not None:
            self.end_page_number = end_page_number
        if range_mode is not None:
            self.range_mode = range_mode
        if word_join_mode is not None:
            self.word_join_mode = word_join_mode
        if word_join_compliance is not None:
            self.word_join_compliance = word_join_compliance
        if image_join_mode is not None:
            self.image_join_mode = image_join_mode
    
    @property
    def file_info(self):
        """
        Gets the file_info.  # noqa: E501

        File info.  # noqa: E501

        :return: The file_info.  # noqa: E501
        :rtype: FileInfo
        """
        return self._file_info

    @file_info.setter
    def file_info(self, file_info):
        """
        Sets the file_info.

        File info.  # noqa: E501

        :param file_info: The file_info.  # noqa: E501
        :type: FileInfo
        """
        self._file_info = file_info
    
    @property
    def pages(self):
        """
        Gets the pages.  # noqa: E501

        List of page numbers to use in a Join operation. NOTE: page numbering starts from 1.  # noqa: E501

        :return: The pages.  # noqa: E501
        :rtype: list[int]
        """
        return self._pages

    @pages.setter
    def pages(self, pages):
        """
        Sets the pages.

        List of page numbers to use in a Join operation. NOTE: page numbering starts from 1.  # noqa: E501

        :param pages: The pages.  # noqa: E501
        :type: list[int]
        """
        self._pages = pages
    
    @property
    def start_page_number(self):
        """
        Gets the start_page_number.  # noqa: E501

        Start page number. Ignored if Pages collection is not empty.  # noqa: E501

        :return: The start_page_number.  # noqa: E501
        :rtype: int
        """
        return self._start_page_number

    @start_page_number.setter
    def start_page_number(self, start_page_number):
        """
        Sets the start_page_number.

        Start page number. Ignored if Pages collection is not empty.  # noqa: E501

        :param start_page_number: The start_page_number.  # noqa: E501
        :type: int
        """
        if start_page_number is None:
            raise ValueError("Invalid value for `start_page_number`, must not be `None`")  # noqa: E501
        self._start_page_number = start_page_number
    
    @property
    def end_page_number(self):
        """
        Gets the end_page_number.  # noqa: E501

        End page number. Ignored if Pages collection is not empty.  # noqa: E501

        :return: The end_page_number.  # noqa: E501
        :rtype: int
        """
        return self._end_page_number

    @end_page_number.setter
    def end_page_number(self, end_page_number):
        """
        Sets the end_page_number.

        End page number. Ignored if Pages collection is not empty.  # noqa: E501

        :param end_page_number: The end_page_number.  # noqa: E501
        :type: int
        """
        if end_page_number is None:
            raise ValueError("Invalid value for `end_page_number`, must not be `None`")  # noqa: E501
        self._end_page_number = end_page_number
    
    @property
    def range_mode(self):
        """
        Gets the range_mode.  # noqa: E501

        Range mode. Ignored if Pages collection is not empty. Default value is AllPages.  # noqa: E501

        :return: The range_mode.  # noqa: E501
        :rtype: str
        """
        return self._range_mode

    @range_mode.setter
    def range_mode(self, range_mode):
        """
        Sets the range_mode.

        Range mode. Ignored if Pages collection is not empty. Default value is AllPages.  # noqa: E501

        :param range_mode: The range_mode.  # noqa: E501
        :type: str
        """
        if range_mode is None:
            raise ValueError("Invalid value for `range_mode`, must not be `None`")  # noqa: E501
        allowed_values = ["AllPages", "OddPages", "EvenPages"]  # noqa: E501
        if not range_mode.isdigit():	
            if range_mode not in allowed_values:
                raise ValueError(
                    "Invalid value for `range_mode` ({0}), must be one of {1}"  # noqa: E501
                    .format(range_mode, allowed_values))
            self._range_mode = range_mode
        else:
            self._range_mode = allowed_values[int(range_mode) if six.PY3 else long(range_mode)]
    
    @property
    def word_join_mode(self):
        """
        Gets the word_join_mode.  # noqa: E501

        Allows to join word documents without empty space between documents.  # noqa: E501

        :return: The word_join_mode.  # noqa: E501
        :rtype: str
        """
        return self._word_join_mode

    @word_join_mode.setter
    def word_join_mode(self, word_join_mode):
        """
        Sets the word_join_mode.

        Allows to join word documents without empty space between documents.  # noqa: E501

        :param word_join_mode: The word_join_mode.  # noqa: E501
        :type: str
        """
        if word_join_mode is None:
            raise ValueError("Invalid value for `word_join_mode`, must not be `None`")  # noqa: E501
        allowed_values = ["Default", "Continuous"]  # noqa: E501
        if not word_join_mode.isdigit():	
            if word_join_mode not in allowed_values:
                raise ValueError(
                    "Invalid value for `word_join_mode` ({0}), must be one of {1}"  # noqa: E501
                    .format(word_join_mode, allowed_values))
            self._word_join_mode = word_join_mode
        else:
            self._word_join_mode = allowed_values[int(word_join_mode) if six.PY3 else long(word_join_mode)]
    
    @property
    def word_join_compliance(self):
        """
        Gets the word_join_compliance.  # noqa: E501

        Compliance mode for the Word Ooxml format  # noqa: E501

        :return: The word_join_compliance.  # noqa: E501
        :rtype: str
        """
        return self._word_join_compliance

    @word_join_compliance.setter
    def word_join_compliance(self, word_join_compliance):
        """
        Sets the word_join_compliance.

        Compliance mode for the Word Ooxml format  # noqa: E501

        :param word_join_compliance: The word_join_compliance.  # noqa: E501
        :type: str
        """
        if word_join_compliance is None:
            raise ValueError("Invalid value for `word_join_compliance`, must not be `None`")  # noqa: E501
        allowed_values = ["Ecma376_2006", "Iso29500_2008_Transitional", "Iso29500_2008_Strict", "Auto"]  # noqa: E501
        if not word_join_compliance.isdigit():	
            if word_join_compliance not in allowed_values:
                raise ValueError(
                    "Invalid value for `word_join_compliance` ({0}), must be one of {1}"  # noqa: E501
                    .format(word_join_compliance, allowed_values))
            self._word_join_compliance = word_join_compliance
        else:
            self._word_join_compliance = allowed_values[int(word_join_compliance) if six.PY3 else long(word_join_compliance)]
    
    @property
    def image_join_mode(self):
        """
        Gets the image_join_mode.  # noqa: E501

        Possible modes for the image joining.  # noqa: E501

        :return: The image_join_mode.  # noqa: E501
        :rtype: str
        """
        return self._image_join_mode

    @image_join_mode.setter
    def image_join_mode(self, image_join_mode):
        """
        Sets the image_join_mode.

        Possible modes for the image joining.  # noqa: E501

        :param image_join_mode: The image_join_mode.  # noqa: E501
        :type: str
        """
        if image_join_mode is None:
            raise ValueError("Invalid value for `image_join_mode`, must not be `None`")  # noqa: E501
        allowed_values = ["Horizontal", "Vertical"]  # noqa: E501
        if not image_join_mode.isdigit():	
            if image_join_mode not in allowed_values:
                raise ValueError(
                    "Invalid value for `image_join_mode` ({0}), must be one of {1}"  # noqa: E501
                    .format(image_join_mode, allowed_values))
            self._image_join_mode = image_join_mode
        else:
            self._image_join_mode = allowed_values[int(image_join_mode) if six.PY3 else long(image_join_mode)]

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
        if not isinstance(other, JoinItem):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
