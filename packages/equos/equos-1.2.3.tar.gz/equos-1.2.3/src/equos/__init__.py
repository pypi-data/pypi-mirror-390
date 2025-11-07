# src/equos/__init__.py
from .equos import Equos, EquosOptions
from .models.agent_models import (
    AgentProvider,
    EquosAgent,
    GeminiAgentConfig,
    GeminiRealtimeModels,
    GeminiRealtimeVoices,
    OpenaiAgentConfig,
    OpenaiRealtimeModels,
    OpenaiRealtimeVoices,
    CreateEquosAgentRequest,
    ListEquosAgentsResponse,
)

from .models.avatar_models import (
    EquosAvatar,
    CreateEquosAvatarRequest,
    ListEquosAvatarsResponse,
)
from .models.session_models import (
    CreateEquosSessionRequest,
    CreateEquosSessionResponse,
    EquosParticipantIdentity,
    EquosResourceId,
    EquosServerUrl,
    EquosSession,
    EquosSessionHost,
    ListEquosSessionsResponse,
)

__all__ = [
    "Equos",
    "EquosOptions",
    "EquosAgent",
    "AgentProvider",
    "GeminiAgentConfig",
    "GeminiRealtimeModels",
    "GeminiRealtimeVoices",
    "OpenaiAgentConfig",
    "OpenaiRealtimeModels",
    "OpenaiRealtimeVoices",
    "CreateEquosAgentRequest",
    "ListEquosAgentsResponse",
    "EquosAvatar",
    "CreateEquosAvatarRequest",
    "ListEquosAvatarsResponse",
    "CreateEquosSessionRequest",
    "CreateEquosSessionResponse",
    "EquosParticipantIdentity",
    "EquosResourceId",
    "EquosServerUrl",
    "EquosSession",
    "EquosSessionHost",
    "ListEquosSessionsResponse",
]
