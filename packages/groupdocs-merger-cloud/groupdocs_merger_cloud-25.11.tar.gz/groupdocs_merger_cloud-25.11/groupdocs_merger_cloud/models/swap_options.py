# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="SwapOptions.py">
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

class SwapOptions(Options):
    """
    Describes options for document pages Swap operation
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'first_page_number': 'int',
        'second_page_number': 'int'
    }

    attribute_map = {
        'first_page_number': 'FirstPageNumber',
        'second_page_number': 'SecondPageNumber'
    }

    def __init__(self, first_page_number=None, second_page_number=None, **kwargs):  # noqa: E501
        """Initializes new instance of SwapOptions"""  # noqa: E501

        self._first_page_number = None
        self._second_page_number = None

        if first_page_number is not None:
            self.first_page_number = first_page_number
        if second_page_number is not None:
            self.second_page_number = second_page_number

        base = super(SwapOptions, self)
        base.__init__(**kwargs)

        self.swagger_types.update(base.swagger_types)
        self.attribute_map.update(base.attribute_map)
    
    @property
    def first_page_number(self):
        """
        Gets the first_page_number.  # noqa: E501

        First page number to exchange  # noqa: E501

        :return: The first_page_number.  # noqa: E501
        :rtype: int
        """
        return self._first_page_number

    @first_page_number.setter
    def first_page_number(self, first_page_number):
        """
        Sets the first_page_number.

        First page number to exchange  # noqa: E501

        :param first_page_number: The first_page_number.  # noqa: E501
        :type: int
        """
        if first_page_number is None:
            raise ValueError("Invalid value for `first_page_number`, must not be `None`")  # noqa: E501
        self._first_page_number = first_page_number
    
    @property
    def second_page_number(self):
        """
        Gets the second_page_number.  # noqa: E501

        Second page number to exchange  # noqa: E501

        :return: The second_page_number.  # noqa: E501
        :rtype: int
        """
        return self._second_page_number

    @second_page_number.setter
    def second_page_number(self, second_page_number):
        """
        Sets the second_page_number.

        Second page number to exchange  # noqa: E501

        :param second_page_number: The second_page_number.  # noqa: E501
        :type: int
        """
        if second_page_number is None:
            raise ValueError("Invalid value for `second_page_number`, must not be `None`")  # noqa: E501
        self._second_page_number = second_page_number

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
        if not isinstance(other, SwapOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
