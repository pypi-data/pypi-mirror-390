from typing import Optional
from equos.utils.async_http_utils import AsyncHttpUtils

from equos.models.error_models import EquosException

from equos.models.avatar_models import (
    CreateEquosAvatarRequest,
    UpdateEquosAvatarRequest,
    EquosAvatar,
    ListEquosAvatarsResponse,
)


class EquosAvatarAsyncApi:
    def __init__(self, async_http: AsyncHttpUtils):
        self.async_http = async_http

    async def create(self, *, data: CreateEquosAvatarRequest) -> EquosAvatar:
        res = await self.async_http.post(
            "/avatars", data.model_dump_json(exclude_none=True)
        )

        if res is None:
            raise EquosException("Create avatar response is None")

        return EquosAvatar.model_validate(res)

    async def list(
        self, *, skip: int = 0, take: int = 10, client: Optional[str] = None
    ) -> ListEquosAvatarsResponse:
        path = f"/avatars?skip={skip}&take={take}"

        if client:
            path += f"&client={client}"

        res = await self.async_http.get(path)

        if res is None:
            raise EquosException("List avatars response is None")

        return ListEquosAvatarsResponse.model_validate(res)

    async def get(self, *, id: str) -> Optional[EquosAvatar]:
        res = await self.async_http.get(f"/avatars/{id}")

        if res is None:
            return None

        return EquosAvatar.model_validate(res)

    async def delete(self, *, id: str) -> Optional[EquosAvatar]:
        res = await self.async_http.delete(f"/avatars/{id}")

        if res is None:
            return None

        return EquosAvatar.model_validate(res)

    async def update(self, *, data: UpdateEquosAvatarRequest) -> EquosAvatar:
        res = await self.async_http.put(
            f"/avatars/{data.id}", data.model_dump_json(exclude_none=True)
        )

        if res is None:
            raise EquosException("Update avatar response is None")

        return EquosAvatar.model_validate(res)
