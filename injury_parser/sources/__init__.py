# Sources package for injury parsers
from .football_injuries import FootballInjuriesParser
from .transfermarkt_injuries import TransfermarktInjuriesParser
from .espn_injuries import EspnInjuriesParser
from .bbc_sport_injuries import BbcSportInjuriesParser

__all__ = [
    "FootballInjuriesParser",
    "TransfermarktInjuriesParser", 
    "EspnInjuriesParser",
    "BbcSportInjuriesParser"
]
