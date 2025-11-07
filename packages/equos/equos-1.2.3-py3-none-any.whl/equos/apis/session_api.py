from typing import Optional
from equos.utils.http_utils import HttpUtils

from equos.models.error_models import EquosException

from equos.models.session_models import (
    CreateEquosSessionRequest,
    CreateEquosSessionResponse,
    EquosSession,
    ListEquosSessionsResponse,
)


class EquosSessionApi:
    def __init__(self, http: HttpUtils):
        self.http = http

    def create(self, *, data: CreateEquosSessionRequest) -> CreateEquosSessionResponse:
        res = self.http.post("/sessions", data.model_dump_json(exclude_none=True))

        if res is None:
            raise EquosException("Create session response is None")

        return CreateEquosSessionResponse.model_validate(res)

    def list(
        self, *, skip: int = 0, take: int = 10, client: Optional[str] = None
    ) -> ListEquosSessionsResponse:
        path = f"/sessions?skip={skip}&take={take}"

        if client:
            path += f"&client={client}"

        res = self.http.get(path)

        if res is None:
            raise EquosException("List sessions response is None")

        return ListEquosSessionsResponse.model_validate(res)

    def get(self, *, id: str) -> Optional[EquosSession]:
        res = self.http.get(f"/sessions/{id}")

        if res is None:
            return None

        return EquosSession.model_validate(res)

    def stop(self, *, id: str) -> Optional[EquosSession]:
        res = self.http.patch(f"/sessions/{id}/stop")

        if res is None:
            return None

        return EquosSession.model_validate(res)
