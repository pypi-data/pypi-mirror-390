import requests

from equos.utils.constants_utils import ConstantUtils
from equos.models.error_models import EquosException


class HttpUtils:
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

    def __get_path(self, path: str) -> str:
        return f"{self.base_url}/{self.version}{path}"

    def get(self, path: str) -> object:
        try:
            return requests.get(
                self.__get_path(path),
                headers={"x-api-key": self.api_key, "Content-Type": "application/json"},
            ).json()

        except Exception as e:
            raise EquosException(f"EquosError: {e}")

    def post(self, path: str, body: str) -> object:
        try:
            return requests.post(
                self.__get_path(path),
                headers={"x-api-key": self.api_key, "Content-Type": "application/json"},
                data=body,
            ).json()

        except Exception as e:
            raise EquosException(f"EquosError: {e}")

    def put(self, path: str, body: str) -> object:
        try:
            return requests.put(
                self.__get_path(path),
                headers={"x-api-key": self.api_key, "Content-Type": "application/json"},
                data=body,
            ).json()

        except Exception as e:
            raise EquosException(f"EquosError: {e}")

    def patch(self, path: str):
        try:
            return requests.patch(
                self.__get_path(path),
                headers={"x-api-key": self.api_key, "Content-Type": "application/json"},
                json={},
            ).json()

        except Exception as e:
            raise EquosException(f"EquosError: {e}")

    def delete(self, path: str) -> object:
        try:
            return requests.delete(
                self.__get_path(path),
                headers={"x-api-key": self.api_key, "Content-Type": "application/json"},
            ).json()

        except Exception as e:
            raise EquosException(f"EquosError: {e}")
