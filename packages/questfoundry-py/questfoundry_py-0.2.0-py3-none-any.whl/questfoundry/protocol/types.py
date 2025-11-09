"""Type definitions for protocol models"""

from enum import Enum


class HotCold(str, Enum):
    """Hot/Cold workspace designation"""

    HOT = "hot"
    COLD = "cold"


class SpoilerPolicy(str, Enum):
    """Spoiler content policy"""

    ALLOWED = "allowed"
    FORBIDDEN = "forbidden"


class RoleName(str, Enum):
    """QuestFoundry role names (Layer 5)"""

    # Core roles
    SHOWRUNNER = "SR"
    GATEKEEPER = "GK"
    PLOTWRIGHT = "PW"
    SCENE_SMITH = "SS"
    STYLE_LEAD = "ST"
    LORE_WEAVER = "LW"
    CODEX_CURATOR = "CC"
    ART_DIRECTOR = "AD"
    ILLUSTRATOR = "IL"
    AUDIO_DIRECTOR = "AuD"
    AUDIO_PRODUCER = "AuP"
    TRANSLATOR = "TR"
    BOOK_BINDER = "BB"
    PLAYER_NARRATOR = "PN"
    RESEARCHER = "RS"
