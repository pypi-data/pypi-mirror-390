from typing import Optional, Union
from datetime import datetime

from pydantic import BaseModel

from equos.models.agent_models import CreateEquosAgentRequest, EquosAgent
from equos.models.avatar_models import CreateEquosAvatarRequest, EquosAvatar


class EquosParticipantIdentity(BaseModel):
    identity: str
    name: str


class EquosResourceId(BaseModel):
    id: str


class EquosServerUrl(BaseModel):
    serverUrl: str


class EquosSessionHost(EquosServerUrl):
    accessToken: str


class CreateEquosSessionRequest(BaseModel):
    name: str
    client: Optional[str] = None
    host: Optional[EquosSessionHost] = None
    agent: Optional[Union[EquosResourceId, CreateEquosAgentRequest]] = None
    avatar: Union[EquosResourceId, CreateEquosAvatarRequest]
    remoteAgentConnectingIdentity: Optional[EquosParticipantIdentity] = None
    consumerIdentity: Optional[EquosParticipantIdentity] = None
    maxDuration: Optional[int] = None


class EquosSession(BaseModel):
    id: str
    organizationId: str
    freemium: bool
    name: str
    provider: str
    client: Optional[str] = None

    status: str

    host: EquosServerUrl

    additionalCtx: Optional[str] = None
    templateVars: Optional[dict[str, str]] = None

    remoteAgentIdentity: Optional[str] = None

    maxDuration: Optional[int] = None

    avatarId: str
    avatar: EquosAvatar

    agentId: Optional[str] = None
    agent: Optional[EquosAgent] = None

    startedAt: datetime
    endedAt: Optional[datetime] = None

    createdAt: datetime
    updatedAt: datetime


class CreateEquosSessionResponse(BaseModel):
    session: EquosSession
    consumerAccessToken: Optional[str] = None
    remoteAgentAccessToken: Optional[str] = None


class ListEquosSessionsResponse(BaseModel):
    skip: int
    take: int
    total: int
    sessions: list[EquosSession]
