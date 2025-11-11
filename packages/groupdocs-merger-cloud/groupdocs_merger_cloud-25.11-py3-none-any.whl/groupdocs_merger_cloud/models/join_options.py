# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="JoinOptions.py">
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

class JoinOptions(object):
    """
    Defines options for documents Join method
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'join_items': 'list[JoinItem]',
        'output_path': 'str'
    }

    attribute_map = {
        'join_items': 'JoinItems',
        'output_path': 'OutputPath'
    }

    def __init__(self, join_items=None, output_path=None, **kwargs):  # noqa: E501
        """Initializes new instance of JoinOptions"""  # noqa: E501

        self._join_items = None
        self._output_path = None

        if join_items is not None:
            self.join_items = join_items
        if output_path is not None:
            self.output_path = output_path
    
    @property
    def join_items(self):
        """
        Gets the join_items.  # noqa: E501

        Documents descriptions for Join operation  # noqa: E501

        :return: The join_items.  # noqa: E501
        :rtype: list[JoinItem]
        """
        return self._join_items

    @join_items.setter
    def join_items(self, join_items):
        """
        Sets the join_items.

        Documents descriptions for Join operation  # noqa: E501

        :param join_items: The join_items.  # noqa: E501
        :type: list[JoinItem]
        """
        self._join_items = join_items
    
    @property
    def output_path(self):
        """
        Gets the output_path.  # noqa: E501

        The output path  # noqa: E501

        :return: The output_path.  # noqa: E501
        :rtype: str
        """
        return self._output_path

    @output_path.setter
    def output_path(self, output_path):
        """
        Sets the output_path.

        The output path  # noqa: E501

        :param output_path: The output_path.  # noqa: E501
        :type: str
        """
        self._output_path = output_path

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
        if not isinstance(other, JoinOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
