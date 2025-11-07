from typing import Optional
from equos.utils.http_utils import HttpUtils

from equos.models.error_models import EquosException

from equos.models.avatar_models import (
    CreateEquosAvatarRequest,
    UpdateEquosAvatarRequest,
    EquosAvatar,
    ListEquosAvatarsResponse,
)


class EquosAvatarApi:
    def __init__(self, http: HttpUtils):
        self.http = http

    def create(self, *, data: CreateEquosAvatarRequest) -> EquosAvatar:
        res = self.http.post("/avatars", data.model_dump_json(exclude_none=True))

        if res is None:
            raise EquosException("Create avatar response is None")

        return EquosAvatar.model_validate(res)

    def list(
        self, *, skip: int = 0, take: int = 10, client: Optional[str] = None
    ) -> ListEquosAvatarsResponse:
        path = f"/avatars?skip={skip}&take={take}"

        if client:
            path += f"&client={client}"

        res = self.http.get(path)

        if res is None:
            raise EquosException("List avatars response is None")

        return ListEquosAvatarsResponse.model_validate(res)

    def get(self, *, id: str) -> Optional[EquosAvatar]:
        res = self.http.get(f"/avatars/{id}")

        if res is None:
            return None

        return EquosAvatar.model_validate(res)

    def delete(self, *, id: str) -> Optional[EquosAvatar]:
        res = self.http.delete(f"/avatars/{id}")

        if res is None:
            return None

        return EquosAvatar.model_validate(res)

    def update(self, *, data: UpdateEquosAvatarRequest) -> EquosAvatar:
        res = self.http.put(
            f"/avatars/{data.id}", data.model_dump_json(exclude_none=True)
        )

        if res is None:
            raise EquosException("Update avatar response is None")

        return EquosAvatar.model_validate(res)
