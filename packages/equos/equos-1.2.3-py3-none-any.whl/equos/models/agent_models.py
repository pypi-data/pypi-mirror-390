from enum import Enum
from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class OpenaiRealtimeModels(Enum):
    gpt_4o_realtime = "gpt-4o-realtime-preview"
    gpt_realtime = "gpt-realtime"


class OpenaiRealtimeVoices(Enum):
    alloy = "alloy"
    marin = "marin"
    cedar = "cedar"
    ash = "ash"
    ballad = "ballad"
    coral = "coral"
    echo = "echo"
    sage = "sage"
    shimmer = "shimmer"
    verse = "verse"


class GeminiRealtimeModels(Enum):
    gemini_2_5_flash_native_audio_09_2025 = (
        "gemini-2.5-flash-native-audio-preview-09-2025"
    )


class GeminiRealtimeVoices(Enum):
    Puck = "Puck"
    Charon = "Charon"
    Kore = "Kore"
    Fenrir = "Fenrir"
    Aoede = "Aoede"
    Leda = "Leda"
    Orus = "Orus"
    Zephyr = "Zephyr"
    Sulafat = "Sulafat"
    Sadachbia = "Sadachbia"
    Sadaltager = "Sadaltager"
    Vindemiatrix = "Vindemiatrix"
    Zubenelgenubi = "Zubenelgenubi"
    Achird = "Achird"
    Pulcherrima = "Pulcherrima"
    Gacrux = "Gacrux"
    Schedar = "Schedar"
    Alnilam = "Alnilam"
    Achernar = "Achernar"
    Laomedeia = "Laomedeia"
    Rasalgethi = "Rasalgethi"
    Algenib = "Algenib"
    Erinome = "Erinome"
    Despina = "Despina"
    Algieba = "Algieba"
    Umbriel = "Umbriel"
    Iapetus = "Iapetus"
    Enceladus = "Enceladus"
    Autonoe = "Autonoe"
    Callirrhoe = "Callirrhoe"


class AgentProvider(Enum):
    openai = "openai"
    gemini = "gemini"
    elevenlabs = "elevenlabs"


class CreateEquosAgentRequest(BaseModel):
    provider: AgentProvider
    name: Optional[str] = None
    client: Optional[str] = None

    model: Optional[GeminiRealtimeModels] = None
    voice: Optional[GeminiRealtimeVoices] = None
    instructions: Optional[str] = None
    remoteId: Optional[str] = None

    search: bool = False
    emotions: bool = False
    memory: bool = False


class UpdateEquosAgentRequest(CreateEquosAgentRequest):
    id: str
    organizationId: str


class EquosAgent(BaseModel):
    id: str
    organizationId: str
    provider: AgentProvider
    name: Optional[str] = None
    client: Optional[str] = None

    model: Optional[GeminiRealtimeModels] = None
    voice: Optional[GeminiRealtimeVoices] = None
    instructions: Optional[str] = None
    remoteId: Optional[str] = None

    search: bool = False
    emotions: bool = False
    memory: bool = False
    createdAt: datetime
    updatedAt: datetime


class ListEquosAgentsResponse(BaseModel):
    skip: int
    take: int
    total: int
    agents: list[EquosAgent]
