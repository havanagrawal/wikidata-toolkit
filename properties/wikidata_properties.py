"""High-level wrapper for Wikidata Properties

    Each instance of Wikidata Property has an ID which corresponds to the true
    Wikidata property ID, and a human-readable name.

    This module also exports some commonly used properties as constants.
"""
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class WikidataProperty:
    pid: str
    name: str

    def __post_init__(self):
        if not re.match(r"P\d{1,9}", self.pid):
            raise ValueError(f"Properties must be of the format P####, was '{self.pid}'")

    def __str__(self):
        return f'{self.pid} ({self.name})'

    def __repr__(self):
        return self.__str__()

INSTANCE_OF = WikidataProperty('P31', 'instance of')
TITLE = WikidataProperty('P1476', 'title')
PART_OF_THE_SERIES = WikidataProperty('P179', 'part of the series')
ORIGINAL_NETWORK = WikidataProperty('P449', 'original network')
COUNTRY_OF_ORIGIN = WikidataProperty('P495', 'country of origin')
ORIGNAL_LANGUAGE_OF_FILM_OR_TV_SHOW = WikidataProperty('P364', 'original language of film or tv show')
PRODUCTION_COMPANY = WikidataProperty('P272', 'production company')
PUBLICATION_DATE = WikidataProperty('P577', 'publication date')
DIRECTOR = WikidataProperty('P57', 'director')
SEASON = WikidataProperty('P4908', 'season')
NUMBER_OF_EPISODES = WikidataProperty('P1113', 'number of episodes')
HAS_PART = WikidataProperty('P527', 'has part')
DURATION = WikidataProperty('P2047', 'duration')
FOLLOWS = WikidataProperty('P155', 'follows')
FOLLOWED_BY = WikidataProperty('P156', 'followed by')
SERIES_ORDINAL = WikidataProperty('P1545', 'series ordinal')
LANGUAGE_OF_WORK_OR_NAME = WikidataProperty('P407', 'language of work or name')

# Identifiers
IMDB_ID = WikidataProperty('P345', 'IMDb ID')
TV_COM_ID = WikidataProperty('P2638', 'TV.com ID')

# 'instance of' values
TELEVISION_SERIES_EPISODE = 'Q21191270'
TELEVISION_SERIES_SEASON = 'Q3464665'
TELEVISION_SERIES = 'Q5398426'
ANIMATED_SERIES = 'Q581714'
MINISERIES = 'Q1259759'
BOOK = 'Q571'
FILM = 'Q11424'
SILENT_FILM = 'Q226730'
LITERARY_WORK = 'Q7725634'

# Languages
ENGLISH = 'Q1860'