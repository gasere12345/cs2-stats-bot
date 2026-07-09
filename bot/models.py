from dataclasses import dataclass, field
from typing import Any


@dataclass
class FaceitPlayer:
    player_id: str
    nickname: str
    country: str = ""
    steam_id: str = ""
    faceit_url: str = ""
    elo: int = 0
    skill_level: int = 0


@dataclass
class FaceitMatch:
    match_id: str
    map: str = ""
    status: str = ""
    score: dict[str, int] = field(default_factory=dict)
    region: str = ""
    faceit_url: str = ""


@dataclass
class PlayerMatchStats:
    nickname: str
    player_id: str
    team: str = ""
    stats: dict[str, Any] = field(default_factory=dict)


@dataclass
class LifetimeStats:
    matches: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    kd: float = 0.0
    adr: float = 0.0
    hs_pct: float = 0.0
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    mvps: int = 0
    kr: float = 0.0
    longest_win_streak: int = 0
    raw: dict[str, Any] = field(default_factory=dict)
    segments: list[dict[str, Any]] = field(default_factory=list)
