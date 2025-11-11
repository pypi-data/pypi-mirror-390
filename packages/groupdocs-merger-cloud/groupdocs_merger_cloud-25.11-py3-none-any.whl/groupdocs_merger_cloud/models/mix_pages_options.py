# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="MixPagesOptions.py">
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

class MixPagesOptions(object):
    """
    Defines options for documents JoinPages method
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'files': 'list[FileInfo]',
        'files_pages': 'list[MixPagesItem]',
        'output_path': 'str',
        'word_join_mode': 'str',
        'word_join_compliance': 'str',
        'image_join_mode': 'str'
    }

    attribute_map = {
        'files': 'Files',
        'files_pages': 'FilesPages',
        'output_path': 'OutputPath',
        'word_join_mode': 'WordJoinMode',
        'word_join_compliance': 'WordJoinCompliance',
        'image_join_mode': 'ImageJoinMode'
    }

    def __init__(self, files=None, files_pages=None, output_path=None, word_join_mode=None, word_join_compliance=None, image_join_mode=None, **kwargs):  # noqa: E501
        """Initializes new instance of MixPagesOptions"""  # noqa: E501

        self._files = None
        self._files_pages = None
        self._output_path = None
        self._word_join_mode = None
        self._word_join_compliance = None
        self._image_join_mode = None

        if files is not None:
            self.files = files
        if files_pages is not None:
            self.files_pages = files_pages
        if output_path is not None:
            self.output_path = output_path
        if word_join_mode is not None:
            self.word_join_mode = word_join_mode
        if word_join_compliance is not None:
            self.word_join_compliance = word_join_compliance
        if image_join_mode is not None:
            self.image_join_mode = image_join_mode
    
    @property
    def files(self):
        """
        Gets the files.  # noqa: E501

        Source documents for JoinPages operation  # noqa: E501

        :return: The files.  # noqa: E501
        :rtype: list[FileInfo]
        """
        return self._files

    @files.setter
    def files(self, files):
        """
        Sets the files.

        Source documents for JoinPages operation  # noqa: E501

        :param files: The files.  # noqa: E501
        :type: list[FileInfo]
        """
        self._files = files
    
    @property
    def files_pages(self):
        """
        Gets the files_pages.  # noqa: E501

        Page numbers for document indicies in Files collection.  # noqa: E501

        :return: The files_pages.  # noqa: E501
        :rtype: list[MixPagesItem]
        """
        return self._files_pages

    @files_pages.setter
    def files_pages(self, files_pages):
        """
        Sets the files_pages.

        Page numbers for document indicies in Files collection.  # noqa: E501

        :param files_pages: The files_pages.  # noqa: E501
        :type: list[MixPagesItem]
        """
        self._files_pages = files_pages
    
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
        if not isinstance(other, MixPagesOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
