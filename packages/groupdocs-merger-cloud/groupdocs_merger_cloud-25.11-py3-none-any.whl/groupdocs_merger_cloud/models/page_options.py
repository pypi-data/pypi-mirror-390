# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="PageOptions.py">
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

from groupdocs_merger_cloud.models import Options

class PageOptions(Options):
    """
    Describes options for specifying page or pages range
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'pages': 'list[int]',
        'start_page_number': 'int',
        'end_page_number': 'int',
        'range_mode': 'str'
    }

    attribute_map = {
        'pages': 'Pages',
        'start_page_number': 'StartPageNumber',
        'end_page_number': 'EndPageNumber',
        'range_mode': 'RangeMode'
    }

    def __init__(self, pages=None, start_page_number=None, end_page_number=None, range_mode=None, **kwargs):  # noqa: E501
        """Initializes new instance of PageOptions"""  # noqa: E501

        self._pages = None
        self._start_page_number = None
        self._end_page_number = None
        self._range_mode = None

        if pages is not None:
            self.pages = pages
        if start_page_number is not None:
            self.start_page_number = start_page_number
        if end_page_number is not None:
            self.end_page_number = end_page_number
        if range_mode is not None:
            self.range_mode = range_mode

        base = super(PageOptions, self)
        base.__init__(**kwargs)

        self.swagger_types.update(base.swagger_types)
        self.attribute_map.update(base.attribute_map)
    
    @property
    def pages(self):
        """
        Gets the pages.  # noqa: E501

        List of page numbers to use in a specific API method. NOTE: page numbering starts from 1.  # noqa: E501

        :return: The pages.  # noqa: E501
        :rtype: list[int]
        """
        return self._pages

    @pages.setter
    def pages(self, pages):
        """
        Sets the pages.

        List of page numbers to use in a specific API method. NOTE: page numbering starts from 1.  # noqa: E501

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
        if not isinstance(other, PageOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
