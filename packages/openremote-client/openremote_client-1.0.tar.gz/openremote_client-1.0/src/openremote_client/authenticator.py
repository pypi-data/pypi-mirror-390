from datetime import datetime, timedelta

import httpx

from .url_builder import UrlBuilder


class Authenticator:
    __url_builder: UrlBuilder
    __client_id: str
    __client_secret: str
    access_token: str | None = None
    expires_on: datetime | None = None

    def __init__(self, url_builder: UrlBuilder, client_id: str, client_secret: str, verify_SSL: bool = True):
        self.__url_builder = url_builder
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__verify_SSL = verify_SSL

    async def __authenticate(self):
        async with httpx.AsyncClient(verify=self.__verify_SSL) as client:
            response = await client.post(
                self.__url_builder.build_base('/auth/realms/master/protocol/openid-connect/token'),
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.__client_id,
                    "client_secret": self.__client_secret,
                    "scope": "profile"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()

            json = response.json()

            self.access_token = json["access_token"]
            self.expires_on = datetime.now() + timedelta(seconds=json["expires_in"] - 1)

    def is_authenticated(self) -> bool:
        if self.access_token is None or (self.expires_on and datetime.now() >= self.expires_on):
            return False
        return True

    async def get_token(self) -> str:
        if not self.is_authenticated():
            await self.__authenticate()
        return self.access_token
