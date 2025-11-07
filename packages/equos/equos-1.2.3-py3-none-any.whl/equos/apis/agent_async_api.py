from typing import Optional
from equos.utils.async_http_utils import AsyncHttpUtils

from equos.models.error_models import EquosException

from equos.models.agent_models import (
    CreateEquosAgentRequest,
    UpdateEquosAgentRequest,
    EquosAgent,
    ListEquosAgentsResponse,
)


class EquosAgentAsyncApi:
    def __init__(self, async_http: AsyncHttpUtils):
        self.async_http = async_http

    async def create(self, *, data: CreateEquosAgentRequest) -> EquosAgent:
        res = await self.async_http.post(
            "/agents", data.model_dump_json(exclude_none=True)
        )

        if res is None:
            raise EquosException("Create agent response is None")

        return EquosAgent.model_validate(res)

    async def list(
        self, *, skip: int = 0, take: int = 10, client: Optional[str] = None
    ) -> ListEquosAgentsResponse:
        path = f"/agents?skip={skip}&take={take}"

        if client:
            path += f"&client={client}"

        res = await self.async_http.get(path)

        if res is None:
            raise EquosException("List agents response is None")

        return ListEquosAgentsResponse.model_validate(res)

    async def get(self, *, id: str) -> Optional[EquosAgent]:
        res = await self.async_http.get(f"/agents/{id}")

        if res is None:
            return None

        return EquosAgent.model_validate(res)

    async def delete(self, *, id: str) -> Optional[EquosAgent]:
        res = await self.async_http.delete(f"/agents/{id}")

        if res is None:
            return None

        return EquosAgent.model_validate(res)

    async def update(self, *, data: UpdateEquosAgentRequest) -> EquosAgent:
        res = await self.async_http.put(
            f"/agents/{data.id}", data.model_dump_json(exclude_none=True)
        )

        if res is None:
            raise EquosException("Update agent response is None")

        return EquosAgent.model_validate(res)
