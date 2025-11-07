from typing import Optional
from equos.utils.async_http_utils import AsyncHttpUtils

from equos.models.error_models import EquosException

from equos.models.session_models import (
    CreateEquosSessionRequest,
    CreateEquosSessionResponse,
    EquosSession,
    ListEquosSessionsResponse,
)


class EquosSessionAsyncApi:
    def __init__(self, async_http: AsyncHttpUtils):
        self.async_http = async_http

    async def create(
        self, *, data: CreateEquosSessionRequest
    ) -> CreateEquosSessionResponse:
        res = await self.async_http.post(
            "/sessions", data.model_dump_json(exclude_none=True)
        )

        if res is None:
            raise EquosException("Create session response is None")

        return CreateEquosSessionResponse.model_validate(res)

    async def list(
        self, *, skip: int = 0, take: int = 10, client: Optional[str] = None
    ) -> ListEquosSessionsResponse:
        path = f"/sessions?skip={skip}&take={take}"

        if client:
            path += f"&client={client}"

        res = await self.async_http.get(path)

        if res is None:
            raise EquosException("List sessions response is None")

        return ListEquosSessionsResponse.model_validate(res)

    async def get(self, *, id: str) -> Optional[EquosSession]:
        res = await self.async_http.get(f"/sessions/{id}")

        if res is None:
            return None

        return EquosSession.model_validate(res)

    async def stop(self, *, id: str) -> Optional[EquosSession]:
        res = await self.async_http.patch(f"/sessions/{id}/stop")

        if res is None:
            return None

        return EquosSession.model_validate(res)
