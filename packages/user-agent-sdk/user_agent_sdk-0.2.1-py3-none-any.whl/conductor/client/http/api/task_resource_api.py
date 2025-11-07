from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from conductor.client.http.api_client import ApiClient


class TaskResourceApi(object):

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def log(self, body, task_id, **kwargs):  # noqa: E501
        """Log Task Execution Details  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.log(body, task_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str body: (required)
        :param str task_id: (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.log_with_http_info(body, task_id, **kwargs)  # noqa: E501
        else:
            (data) = self.log_with_http_info(body, task_id, **kwargs)  # noqa: E501
            return data

    def log_with_http_info(self, body, task_id, **kwargs):  # noqa: E501
        """Log Task Execution Details  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.log_with_http_info(body, task_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str body: (required)
        :param str task_id: (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['body', 'task_id']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method log" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if ('body' not in params or
                params['body'] is None):
            raise ValueError("Missing the required parameter `body` when calling `log`")  # noqa: E501
        # verify the required parameter 'task_id' is set
        if ('task_id' not in params or
                params['task_id'] is None):
            raise ValueError("Missing the required parameter `task_id` when calling `log`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'task_id' in params:
            path_params['taskId'] = params['task_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = params['body']
        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/tasks/{taskId}/log', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def poll(self, tasktype, **kwargs):  # noqa: E501
        """Poll for a task of a certain type  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.poll(tasktype, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str tasktype: (required)
        :param str workerid:
        :param str domain:
        :return: Task
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.poll_with_http_info(tasktype, **kwargs)  # noqa: E501
        else:
            (data) = self.poll_with_http_info(tasktype, **kwargs)  # noqa: E501
            return data

    def poll_with_http_info(self, tasktype, **kwargs):  # noqa: E501
        """Poll for a task of a certain type  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.poll_with_http_info(tasktype, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str tasktype: (required)
        :param str workerid:
        :param str domain:
        :return: Task
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['tasktype', 'workerid', 'domain']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method poll" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'tasktype' is set
        if ('tasktype' not in params or
                params['tasktype'] is None):
            raise ValueError("Missing the required parameter `tasktype` when calling `poll`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'tasktype' in params:
            path_params['tasktype'] = params['tasktype']  # noqa: E501

        query_params = []
        if 'workerid' in params:
            query_params.append(('workerid', params['workerid']))  # noqa: E501
        if 'domain' in params:
            query_params.append(('domain', params['domain']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['*/*'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/tasks/external/poll/{tasktype}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Task',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def update_task(self, body, **kwargs):  # noqa: E501
        """Update a task  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.update_task(body, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param TaskResult body: (required)
        :return: str
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.update_task_with_http_info(body, **kwargs)  # noqa: E501
        else:
            (data) = self.update_task_with_http_info(body, **kwargs)  # noqa: E501
            return data

    def update_task_with_http_info(self, body, **kwargs):  # noqa: E501
        """Update a task  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.update_task_with_http_info(body, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param TaskResult body: (required)
        :return: str
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['body']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method update_task" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if ('body' not in params or
                params['body'] is None):
            raise ValueError("Missing the required parameter `body` when calling `update_task`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = params['body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['text/plain'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/tasks/external', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='str',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)
