import httpx

from equos.utils.constants_utils import ConstantUtils
from equos.models.error_models import EquosException


class AsyncHttpUtils:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = ConstantUtils.DEFAULT_BASE_URL,
        version: str = ConstantUtils.API_VERSION,
    ):
        self.base_url = base_url
        self.version = version
        self.api_key = api_key
        self._client = httpx.AsyncClient(
            headers={"x-api-key": self.api_key, "Content-Type": "application/json"},
            timeout=30.0,
        )

    def __get_path(self, path: str) -> str:
        return f"{self.base_url}/{self.version}{path}"

    async def get(self, path: str) -> object:
        try:
            response = await self._client.get(self.__get_path(path))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise EquosException(f"EquosError: {e}")

    async def post(self, path: str, body: str) -> object:
        try:
            response = await self._client.post(self.__get_path(path), content=body)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise EquosException(f"EquosError: {e}")

    async def put(self, path: str, body: str) -> object:
        try:
            response = await self._client.put(self.__get_path(path), content=body)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise EquosException(f"EquosError: {e}")

    async def patch(self, path: str) -> object:
        try:
            response = await self._client.patch(self.__get_path(path), json={})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise EquosException(f"EquosError: {e}")

    async def delete(self, path: str) -> object:
        try:
            response = await self._client.delete(self.__get_path(path))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise EquosException(f"EquosError: {e}")
