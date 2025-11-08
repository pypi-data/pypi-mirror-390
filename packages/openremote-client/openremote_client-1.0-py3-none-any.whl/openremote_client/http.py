from typing import Optional, Union, Any, TypeVar

import httpx
from httpx import Response
from httpx._client import UseClientDefault, USE_CLIENT_DEFAULT
from httpx._types import QueryParamTypes, HeaderTypes, CookieTypes, AuthTypes, TimeoutTypes, RequestExtensions, \
    RequestContent, RequestData, RequestFiles

from .authenticator import Authenticator
from .url_builder import UrlBuilder

T = TypeVar('T')


class HttpClient:
    def __init__(self, url_builder: UrlBuilder, authenticator: Authenticator, realm: str = 'master', verify_SSL: bool = True):
        self.__url_builder = url_builder
        self.__authenticator = authenticator
        self.__realm = realm
        self.__verify_SSL = verify_SSL

    def set_realm(self, realm: str):
        self.__realm = realm

    async def get(
            self,
            path: str,
            params: Optional[QueryParamTypes] = None,
            headers: Optional[HeaderTypes] = None,
            cookies: Optional[CookieTypes] = None,
            auth: Union[AuthTypes, UseClientDefault, None] = USE_CLIENT_DEFAULT,
            follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
            timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
            extensions: Optional[RequestExtensions] = None,
    ) -> Response:
        if headers is None:
            headers = {}

        headers['Authorization'] = f'Bearer {await self.__authenticator.get_token()}'

        async with httpx.AsyncClient(verify=self.__verify_SSL) as client:
            return await client.get(
                url=self.__url_builder.build(path, realm=self.__realm),
                params=params,
                headers=headers,
                cookies=cookies,
                auth=auth,
                follow_redirects=follow_redirects,
                timeout=timeout,
                extensions=extensions,
            )

    async def post(
            self,
            path: str,
            content: Optional[RequestContent] = None,
            data: Optional[RequestData] = None,
            files: Optional[RequestFiles] = None,
            json: Optional[Any] = None,
            params: Optional[QueryParamTypes] = None,
            headers: Optional[HeaderTypes] = None,
            cookies: Optional[CookieTypes] = None,
            auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
            follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
            timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
            extensions: Optional[RequestExtensions] = None,
    ) -> Response:
        if headers is None:
            headers = {}

        headers['Authorization'] = f'Bearer {await self.__authenticator.get_token()}'

        async with httpx.AsyncClient(verify=self.__verify_SSL) as client:
            return await client.post(
                url=self.__url_builder.build(path, realm=self.__realm),
                content=content,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=headers,
                cookies=cookies,
                auth=auth,
                follow_redirects=follow_redirects,
                timeout=timeout,
                extensions=extensions,
            )

    async def put(
            self,
            path: str,
            content: Optional[RequestContent] = None,
            data: Optional[RequestData] = None,
            files: Optional[RequestFiles] = None,
            json: Optional[Any] = None,
            params: Optional[QueryParamTypes] = None,
            headers: Optional[HeaderTypes] = None,
            cookies: Optional[CookieTypes] = None,
            auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
            follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
            timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
            extensions: Optional[RequestExtensions] = None,
    ) -> Response:
        if headers is None:
            headers = {}

        headers['Authorization'] = f'Bearer {await self.__authenticator.get_token()}'

        async with httpx.AsyncClient(verify=self.__verify_SSL) as client:
            return await client.put(
                url=self.__url_builder.build(path, realm=self.__realm),
                content=content,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=headers,
                cookies=cookies,
                auth=auth,
                follow_redirects=follow_redirects,
                timeout=timeout,
                extensions=extensions,
            )

    async def delete(
            self,
            path: str,
            content: Optional[RequestContent] = None,
            data: Optional[RequestData] = None,
            files: Optional[RequestFiles] = None,
            json: Optional[Any] = None,
            params: Optional[QueryParamTypes] = None,
            headers: Optional[HeaderTypes] = None,
            cookies: Optional[CookieTypes] = None,
            auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
            follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
            timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
            extensions: Optional[RequestExtensions] = None,
    ) -> Response:
        if headers is None:
            headers = {}

        headers['Authorization'] = f'Bearer {await self.__authenticator.get_token()}'

        async with httpx.AsyncClient(verify=self.__verify_SSL) as client:
            return await client.delete(
                url=self.__url_builder.build(path, realm=self.__realm),
                params=params,
                headers=headers,
                cookies=cookies,
                auth=auth,
                follow_redirects=follow_redirects,
                timeout=timeout,
                extensions=extensions,
            )
