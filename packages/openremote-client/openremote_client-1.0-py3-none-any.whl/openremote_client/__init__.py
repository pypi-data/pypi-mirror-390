from pydantic import HttpUrl

from .authenticator import Authenticator
from .http import HttpClient
from .url_builder import UrlBuilder

from .api import Agent, Alarm, Configuration, UiApps, AssetModel, Asset, Console, Dashboard, AssetDatapoint, AssetPredictedDatapoint, Gateway, Map, Notification, Provisioning, Rule, Flow, Realm, User, Services, Syslog, Status


class OpenRemoteClient:
    __authenticator: Authenticator
    __url_builder: UrlBuilder
    __http_client: HttpClient

    agent: Agent
    alarm: Alarm
    configuration: Configuration
    ui_apps: UiApps
    asset_model: AssetModel
    asset: Asset
    console: Console
    dashboard: Dashboard
    asset_datapoint: AssetDatapoint
    asset_predicted_datapoint: AssetPredictedDatapoint
    gateway: Gateway
    map: Map
    notification: Notification
    provisioning: Provisioning
    rule: Rule
    flow: Flow
    realm: Realm
    user: User
    services: Services
    syslog: Syslog
    status: Status

    def __init__(self, host: HttpUrl | str, client_id: str, client_secret: str, realm: str = 'master', verify_SSL: bool = True):
        self.__url_builder = UrlBuilder(host)
        self.__authenticator = Authenticator(self.__url_builder, client_id, client_secret, verify_SSL)
        self.__http_client = HttpClient(self.__url_builder, self.__authenticator, realm, verify_SSL)

        # Init API endpoints
        self.agent = Agent(self.__http_client)
        self.alarm = Alarm(self.__http_client)
        self.configuration = Configuration(self.__http_client)
        self.ui_apps = UiApps(self.__http_client)
        self.asset_model = AssetModel(self.__http_client)
        self.asset = Asset(self.__http_client)
        self.console = Console(self.__http_client)
        self.dashboard = Dashboard(self.__http_client)
        self.asset_datapoint = AssetDatapoint(self.__http_client)
        self.asset_predicted_datapoint = AssetPredictedDatapoint(self.__http_client)
        self.gateway = Gateway(self.__http_client)
        self.map = Map(self.__http_client)
        self.notification = Notification(self.__http_client)
        self.provisioning = Provisioning(self.__http_client)
        self.rule = Rule(self.__http_client)
        self.flow = Flow(self.__http_client)
        self.realm = Realm(self.__http_client)
        self.user = User(self.__http_client)
        self.services = Services(self.__http_client)
        self.syslog = Syslog(self.__http_client)
        self.status = Status(self.__http_client)

        # Init HTTPX Generic method
        self.get = self.__http_client.get
        self.post = self.__http_client.post
        self.put = self.__http_client.put
        self.delete = self.__http_client.delete

    def set_realm(self, realm: str):
        self.__http_client.set_realm(realm)
