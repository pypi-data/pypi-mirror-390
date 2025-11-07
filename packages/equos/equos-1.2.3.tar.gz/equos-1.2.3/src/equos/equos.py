from typing import Optional
from dataclasses import dataclass

from equos.utils.constants_utils import ConstantUtils
from equos.utils.http_utils import HttpUtils
from equos.utils.async_http_utils import AsyncHttpUtils

from equos.apis.agent_api import EquosAgentApi
from equos.apis.avatar_api import EquosAvatarApi
from equos.apis.session_api import EquosSessionApi

from equos.apis.agent_async_api import EquosAgentAsyncApi
from equos.apis.avatar_async_api import EquosAvatarAsyncApi
from equos.apis.session_async_api import EquosSessionAsyncApi


@dataclass
class EquosOptions:
    version: str = ConstantUtils.API_VERSION
    endpoint: str = ConstantUtils.DEFAULT_BASE_URL


class Equos:
    _endpoint: str
    _version: str

    _http: HttpUtils
    _async_http: AsyncHttpUtils

    agents: EquosAgentApi
    avatars: EquosAvatarApi
    sessions: EquosSessionApi

    async_agents: EquosAgentAsyncApi
    async_avatars: EquosAvatarAsyncApi
    async_sessions: EquosSessionAsyncApi

    def __init__(self, api_key: str, opts: Optional[EquosOptions] = None):
        self._endpoint = opts.endpoint if opts else ConstantUtils.DEFAULT_BASE_URL
        self._version = opts.version if opts else ConstantUtils.API_VERSION

        self._http = HttpUtils(
            api_key=api_key, base_url=self._endpoint, version=self._version
        )
        self._async_http = AsyncHttpUtils(
            api_key=api_key, base_url=self._endpoint, version=self._version
        )

        self.agents = EquosAgentApi(self._http)
        self.avatars = EquosAvatarApi(self._http)
        self.sessions = EquosSessionApi(self._http)

        self.async_agents = EquosAgentAsyncApi(self._async_http)
        self.async_avatars = EquosAvatarAsyncApi(self._async_http)
        self.async_sessions = EquosSessionAsyncApi(self._async_http)
