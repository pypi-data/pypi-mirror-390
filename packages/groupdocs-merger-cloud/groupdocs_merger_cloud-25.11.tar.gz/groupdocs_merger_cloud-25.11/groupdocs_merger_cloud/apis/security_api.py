# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="merger_api.py">
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

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from groupdocs_merger_cloud.auth import Auth
from groupdocs_merger_cloud.api_client import ApiClient
from groupdocs_merger_cloud.api_exception import ApiException
from groupdocs_merger_cloud.configuration import Configuration

class SecurityApi(object):
    """
    GroupDocs.Merger Cloud API

    :param configuration: API configuration
    """

    def __init__(self, configuration):
        api_client = ApiClient(configuration)

        self.auth = Auth(configuration, api_client)
        self.api_client = api_client
        self.configuration = configuration

    def close(self):  # noqa: E501
        """
        Closes thread pool. This method should be called when 
        methods are executed asynchronously (is_async=True is passed as parameter)
        and this instance of SecurityApi is not going to be used any more.
        """
        if self.api_client is not None:
            if(self.api_client.pool is not None):
                self.api_client.pool.close()
                self.api_client.pool.join()
                self.api_client.pool = None

    @classmethod
    def from_keys(cls, app_sid, app_key):
        """
        Initializes new instance of SecurityApi with API keys

        :param app_sid Application identifier (App SID)
        :param app_key Application private key (App Key)
        """
        configuration = Configuration(app_sid, app_key)
        return SecurityApi(configuration)

    @classmethod
    def from_config(cls, configuration):
        """
        Initializes new instance of SecurityApi with configuration options

        :param configuration API configuration
        """
        return SecurityApi(configuration)

    def add_password(self, request,**kwargs):  # noqa: E501
        """Add document password protection  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True

        :param is_async bool
        :param Options options: Options to specify document name and new password (required)
        :return: DocumentResult
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True

        if kwargs.get('is_async'):
            return self._add_password_with_http_info(request, **kwargs)  # noqa: E501
        
        (data) = self._add_password_with_http_info(request, **kwargs)  # noqa: E501
        return data

    def _add_password_with_http_info(self, request, **kwargs):  # noqa: E501
        """Add document password protection  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True

        :param is_async bool
        :param AddPasswordRequest request object with parameters
        :return: DocumentResult
                 If the method is called asynchronously,
                 returns the request thread.
        """
        params = locals()
        params['is_async'] = ''
        params['_return_http_data_only'] = False
        params['_preload_content'] = True
        params['_request_timeout'] = ''
        for key, val in six.iteritems(params['kwargs']):
            if key not in params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method add_password" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'options' is set
        if request.options is None:
            raise ValueError("Missing the required parameter `options` when calling `add_password`")  # noqa: E501

        collection_formats = {}
        path = '/merger/password'
        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = []

        body_params = None
        if request.options is not None:
            body_params = request.options
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        call_kwargs = {
            'resource_path':path, 
            'method':'PUT',
            'path_params':path_params,
            'query_params':query_params,
            'header_params':header_params,
            'body':body_params,
            'post_params':form_params,
            'files':local_var_files,
            'response_type':'DocumentResult',  # noqa: E501
            'auth_settings':self.auth.get_auth_settings(),
            'is_async':params.get('is_async'),
            '_return_http_data_only':params.get('_return_http_data_only'),
            '_preload_content':params.get('_preload_content', True),
            '_request_timeout':params.get('_request_timeout'),
            'collection_formats':collection_formats
        }

        return self.api_client.call_api(**call_kwargs)  # noqa: E501

    def check_password(self, request,**kwargs):  # noqa: E501
        """Checks whether document is password protected  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True

        :param is_async bool
        :param str file_path: File path (required)
        :param str storage_name: Storage name
        :param str version_id: Version Id
        :return: PasswordResult
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True

        if kwargs.get('is_async'):
            return self._check_password_with_http_info(request, **kwargs)  # noqa: E501
        
        (data) = self._check_password_with_http_info(request, **kwargs)  # noqa: E501
        return data

    def _check_password_with_http_info(self, request, **kwargs):  # noqa: E501
        """Checks whether document is password protected  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True

        :param is_async bool
        :param CheckPasswordRequest request object with parameters
        :return: PasswordResult
                 If the method is called asynchronously,
                 returns the request thread.
        """
        params = locals()
        params['is_async'] = ''
        params['_return_http_data_only'] = False
        params['_preload_content'] = True
        params['_request_timeout'] = ''
        for key, val in six.iteritems(params['kwargs']):
            if key not in params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method check_password" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'file_path' is set
        if request.file_path is None:
            raise ValueError("Missing the required parameter `file_path` when calling `check_password`")  # noqa: E501

        collection_formats = {}
        path = '/merger/password'
        path_params = {}

        query_params = []
        if self.__downcase_first_letter('filePath') in path:
            path = path.replace('{' + self.__downcase_first_letter('filePath' + '}'), request.file_path if request.file_path is not None else '')
        else:
            if request.file_path is not None:
                query_params.append((self.__downcase_first_letter('filePath'), request.file_path))  # noqa: E501
        if self.__downcase_first_letter('storageName') in path:
            path = path.replace('{' + self.__downcase_first_letter('storageName' + '}'), request.storage_name if request.storage_name is not None else '')
        else:
            if request.storage_name is not None:
                query_params.append((self.__downcase_first_letter('storageName'), request.storage_name))  # noqa: E501
        if self.__downcase_first_letter('versionId') in path:
            path = path.replace('{' + self.__downcase_first_letter('versionId' + '}'), request.version_id if request.version_id is not None else '')
        else:
            if request.version_id is not None:
                query_params.append((self.__downcase_first_letter('versionId'), request.version_id))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = []

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        call_kwargs = {
            'resource_path':path, 
            'method':'GET',
            'path_params':path_params,
            'query_params':query_params,
            'header_params':header_params,
            'body':body_params,
            'post_params':form_params,
            'files':local_var_files,
            'response_type':'PasswordResult',  # noqa: E501
            'auth_settings':self.auth.get_auth_settings(),
            'is_async':params.get('is_async'),
            '_return_http_data_only':params.get('_return_http_data_only'),
            '_preload_content':params.get('_preload_content', True),
            '_request_timeout':params.get('_request_timeout'),
            'collection_formats':collection_formats
        }

        return self.api_client.call_api(**call_kwargs)  # noqa: E501

    def remove_password(self, request,**kwargs):  # noqa: E501
        """Remove document password protection  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True

        :param is_async bool
        :param Options options: Options to specify document name and current password (required)
        :return: DocumentResult
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True

        if kwargs.get('is_async'):
            return self._remove_password_with_http_info(request, **kwargs)  # noqa: E501
        
        (data) = self._remove_password_with_http_info(request, **kwargs)  # noqa: E501
        return data

    def _remove_password_with_http_info(self, request, **kwargs):  # noqa: E501
        """Remove document password protection  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True

        :param is_async bool
        :param RemovePasswordRequest request object with parameters
        :return: DocumentResult
                 If the method is called asynchronously,
                 returns the request thread.
        """
        params = locals()
        params['is_async'] = ''
        params['_return_http_data_only'] = False
        params['_preload_content'] = True
        params['_request_timeout'] = ''
        for key, val in six.iteritems(params['kwargs']):
            if key not in params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method remove_password" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'options' is set
        if request.options is None:
            raise ValueError("Missing the required parameter `options` when calling `remove_password`")  # noqa: E501

        collection_formats = {}
        path = '/merger/password'
        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = []

        body_params = None
        if request.options is not None:
            body_params = request.options
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        call_kwargs = {
            'resource_path':path, 
            'method':'DELETE',
            'path_params':path_params,
            'query_params':query_params,
            'header_params':header_params,
            'body':body_params,
            'post_params':form_params,
            'files':local_var_files,
            'response_type':'DocumentResult',  # noqa: E501
            'auth_settings':self.auth.get_auth_settings(),
            'is_async':params.get('is_async'),
            '_return_http_data_only':params.get('_return_http_data_only'),
            '_preload_content':params.get('_preload_content', True),
            '_request_timeout':params.get('_request_timeout'),
            'collection_formats':collection_formats
        }

        return self.api_client.call_api(**call_kwargs)  # noqa: E501

    def update_password(self, request,**kwargs):  # noqa: E501
        """Update document password  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True

        :param is_async bool
        :param UpdatePasswordOptions options: Options to specify document name, current and new password (required)
        :return: DocumentResult
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True

        if kwargs.get('is_async'):
            return self._update_password_with_http_info(request, **kwargs)  # noqa: E501
        
        (data) = self._update_password_with_http_info(request, **kwargs)  # noqa: E501
        return data

    def _update_password_with_http_info(self, request, **kwargs):  # noqa: E501
        """Update document password  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True

        :param is_async bool
        :param UpdatePasswordRequest request object with parameters
        :return: DocumentResult
                 If the method is called asynchronously,
                 returns the request thread.
        """
        params = locals()
        params['is_async'] = ''
        params['_return_http_data_only'] = False
        params['_preload_content'] = True
        params['_request_timeout'] = ''
        for key, val in six.iteritems(params['kwargs']):
            if key not in params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method update_password" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'options' is set
        if request.options is None:
            raise ValueError("Missing the required parameter `options` when calling `update_password`")  # noqa: E501

        collection_formats = {}
        path = '/merger/password'
        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = []

        body_params = None
        if request.options is not None:
            body_params = request.options
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        call_kwargs = {
            'resource_path':path, 
            'method':'POST',
            'path_params':path_params,
            'query_params':query_params,
            'header_params':header_params,
            'body':body_params,
            'post_params':form_params,
            'files':local_var_files,
            'response_type':'DocumentResult',  # noqa: E501
            'auth_settings':self.auth.get_auth_settings(),
            'is_async':params.get('is_async'),
            '_return_http_data_only':params.get('_return_http_data_only'),
            '_preload_content':params.get('_preload_content', True),
            '_request_timeout':params.get('_request_timeout'),
            'collection_formats':collection_formats
        }

        return self.api_client.call_api(**call_kwargs)  # noqa: E501

    def __downcase_first_letter(self, s):
        if len(s) == 0:
            return str
        else:
            return s[0].lower() + s[1:]

# coding: utf-8

# --------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="add_password_request.py">
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
# --------------------------------------------------------------------------------

class AddPasswordRequest(object):
    """
    Request model for add_password operation.
    :param options Options to specify document name and new password
    """

    def __init__(self, options):
        """Initializes new instance of AddPasswordRequest."""  # noqa: E501
        self.options = options
# coding: utf-8

# --------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="check_password_request.py">
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
# --------------------------------------------------------------------------------

class CheckPasswordRequest(object):
    """
    Request model for check_password operation.
    :param file_path File path
    :param storage_name Storage name
    :param version_id Version Id
    """

    def __init__(self, file_path, storage_name=None, version_id=None):
        """Initializes new instance of CheckPasswordRequest."""  # noqa: E501
        self.file_path = file_path
        self.storage_name = storage_name
        self.version_id = version_id
# coding: utf-8

# --------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="remove_password_request.py">
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
# --------------------------------------------------------------------------------

class RemovePasswordRequest(object):
    """
    Request model for remove_password operation.
    :param options Options to specify document name and current password
    """

    def __init__(self, options):
        """Initializes new instance of RemovePasswordRequest."""  # noqa: E501
        self.options = options
# coding: utf-8

# --------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="update_password_request.py">
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
# --------------------------------------------------------------------------------

class UpdatePasswordRequest(object):
    """
    Request model for update_password operation.
    :param options Options to specify document name, current and new password
    """

    def __init__(self, options):
        """Initializes new instance of UpdatePasswordRequest."""  # noqa: E501
        self.options = options
