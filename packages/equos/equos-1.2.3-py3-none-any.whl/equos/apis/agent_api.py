from typing import Optional

from equos.utils.http_utils import HttpUtils

from equos.models.error_models import EquosException

from equos.models.agent_models import (
    CreateEquosAgentRequest,
    UpdateEquosAgentRequest,
    EquosAgent,
    ListEquosAgentsResponse,
)


class EquosAgentApi:
    def __init__(self, http: HttpUtils):
        self.http = http

    def create(self, *, data: CreateEquosAgentRequest) -> EquosAgent:
        res = self.http.post("/agents", data.model_dump_json(exclude_none=True))

        if res is None:
            raise EquosException("Create agent response is None")

        return EquosAgent.model_validate(res)

    def list(
        self, *, skip: int = 0, take: int = 10, client: Optional[str] = None
    ) -> ListEquosAgentsResponse:
        path = f"/agents?skip={skip}&take={take}"

        if client:
            path += f"&client={client}"

        res = self.http.get(path)

        if res is None:
            raise EquosException("List agents response is None")

        return ListEquosAgentsResponse.model_validate(res)

    def get(self, *, id: str) -> Optional[EquosAgent]:
        res = self.http.get(f"/agents/{id}")

        if res is None:
            return None

        return EquosAgent.model_validate(res)

    def delete(self, *, id: str) -> Optional[EquosAgent]:
        res = self.http.delete(f"/agents/{id}")

        if res is None:
            return None

        return EquosAgent.model_validate(res)

    def update(self, *, data: UpdateEquosAgentRequest) -> EquosAgent:
        res = self.http.put(
            f"/agents/{data.id}", data.model_dump_json(exclude_none=True)
        )

        if res is None:
            raise EquosException("Update agent response is None")

        return EquosAgent.model_validate(res)
