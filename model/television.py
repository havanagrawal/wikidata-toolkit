"""Wrapper classes for high-level concepts relating to TV series"""

from functools import partial

from pywikibot import ItemPage, Site
from pywikibot.pagegenerators import WikidataSPARQLPageGenerator

from constraints import has_property, inherits_property
from constraints import follows_something, is_followed_by_something
import properties.wikidata_properties as wp
from sparql.query_builder import generate_sparql_query

class BaseType():
    def __init__(self, itempage, repo=None):
        self._itempage = itempage
        self._itempage.get()
        self._repo = Site().data_repository() if repo is None else repo

    @property
    def itempage(self):
        return self._itempage

    @property
    def label(self):
        return self._itempage.labels['en']

    @property
    def parent(self):
        return None

    @property
    def repo(self):
        return self._repo

    @classmethod
    def from_id(cls, item_id, repo=None):
        repo = Site().data_repository() if repo is None else repo
        return cls(ItemPage(repo, item_id), repo)

    @property
    def claims(self):
        return self._itempage.claims

    def __str__(self):
        return f"{self.__class__.__name__}({self._itempage.title()} ({self.label}))"

    def __repr__(self):
        return self.__str__()

class Episode(BaseType):
    def __init__(self, itempage, repo=None):
        super().__init__(itempage, repo)

    @property
    def constraints(self):
        return self._property_constraints() + self._inheritance_constraints()

    @property
    def parent(self):
        season_itempage = self.claims[wp.SEASON.pid][0].getTarget()
        return Season(season_itempage)

    @property
    def next(self):
        """Return the next episode, if any"""
        if wp.FOLLOWED_BY.pid in self.claims:
            next_episode_itempage = self.claims[wp.FOLLOWED_BY.pid][0].getTarget()
            return Episode(next_episode_itempage)

        ordinal = self.ordinal_in_series
        if self.ordinal_in_series is not None:
            return self.next_in_series

        if self.ordinal_in_season is not None:
            return self.next_in_season

    @property
    def next_in_season(self):
        if self.ordinal_in_season is None:
            return None
        query = f"""SELECT ?item WHERE {{
            ?item wdt:{wp.PART_OF_THE_SERIES.pid} wd:{self.part_of_the_series}.
            ?item wdt:{wp.SEASON.pid} wd:{self.season}.
            ?item p:{wp.SEASON.pid}/pq:{wp.SERIES_ORDINAL.pid} "{self.ordinal_in_season + 1}"
            }}
        """
        gen = WikidataSPARQLPageGenerator(query)
        next_episode_itempage = next(gen, None)
        if next_episode_itempage is None:
            return None

        return Episode(next_episode_itempage)

    @property
    def next_in_series(self):
        if self.ordinal_in_series is None:
            return None
        query = f"""SELECT ?item WHERE {{
            ?item wdt:{wp.PART_OF_THE_SERIES.pid} wd:{self.part_of_the_series}.
            ?item p:{wp.PART_OF_THE_SERIES.pid}/pq:{wp.SERIES_ORDINAL.pid} "{self.ordinal_in_series + 1}"
            }}
        """
        gen = WikidataSPARQLPageGenerator(query)
        next_episode_itempage = next(gen, None)
        if next_episode_itempage is None:
            return None

        return Episode(next_episode_itempage)

    @property
    def part_of_the_series(self):
        if wp.PART_OF_THE_SERIES.pid not in self.claims:
            return None
        return self.claims[wp.PART_OF_THE_SERIES.pid][0].getTarget().title()

    @property
    def season(self):
        if wp.SEASON.pid not in self.claims:
            return None
        return self.claims[wp.SEASON.pid][0].getTarget().title()

    @property
    def ordinal_in_series(self):
        if not wp.PART_OF_THE_SERIES.pid in self.claims:
            return None
        series_claim = self.claims[wp.PART_OF_THE_SERIES.pid][0]
        if wp.SERIES_ORDINAL.pid not in series_claim.qualifiers:
            return None

        return int(series_claim.qualifiers[wp.SERIES_ORDINAL.pid][0].getTarget())

    @property
    def ordinal_in_season(self):
        if not wp.SEASON.pid in self.claims:
            return None
        series_claim = self.claims[wp.SEASON.pid][0]
        if wp.SERIES_ORDINAL.pid not in series_claim.qualifiers:
            return None

        return int(series_claim.qualifiers[wp.SERIES_ORDINAL.pid][0].getTarget())


    def _property_constraints(self):
        return [has_property(prop) for prop in (
            wp.INSTANCE_OF,
            wp.TITLE,
            wp.PART_OF_THE_SERIES,
            wp.SEASON,
            wp.ORIGINAL_NETWORK,
            wp.COUNTRY_OF_ORIGIN,
            wp.ORIGNAL_LANGUAGE_OF_FILM_OR_TV_SHOW,
            wp.PRODUCTION_COMPANY,
            wp.PUBLICATION_DATE,
            wp.DIRECTOR,
            wp.FOLLOWED_BY,
            wp.DURATION,
            wp.IMDB_ID,
        )] + [
            follows_something(),
            is_followed_by_something(),
        ]

    def _inheritance_constraints(self):
        return [inherits_property(prop) for prop in (
            wp.ORIGINAL_NETWORK,
            wp.COUNTRY_OF_ORIGIN,
            wp.ORIGNAL_LANGUAGE_OF_FILM_OR_TV_SHOW,
            wp.PRODUCTION_COMPANY,
        )]

class Season(BaseType):
    def __init__(self, itempage, repo=None):
        super().__init__(itempage, repo)

    @property
    def parent(self):
        series_itempage = self.claims[wp.PART_OF_THE_SERIES.pid][0].getTarget()
        return Series(series_itempage)

    @property
    def constraints(self):
        return self._property_constraints() + self._inheritance_constraints()

    def _property_constraints(self):
        return [has_property(prop) for prop in (
            wp.INSTANCE_OF,
            wp.PART_OF_THE_SERIES,
            wp.ORIGINAL_NETWORK,
            wp.COUNTRY_OF_ORIGIN,
            wp.ORIGNAL_LANGUAGE_OF_FILM_OR_TV_SHOW,
            wp.PRODUCTION_COMPANY,
            wp.FOLLOWS,
            wp.FOLLOWED_BY,
            wp.HAS_PART,
            wp.NUMBER_OF_EPISODES,
        )]

    def _inheritance_constraints(self):
        return [inherits_property(prop) for prop in (
            wp.ORIGINAL_NETWORK,
            wp.COUNTRY_OF_ORIGIN,
            wp.ORIGNAL_LANGUAGE_OF_FILM_OR_TV_SHOW,
            wp.PRODUCTION_COMPANY,
        )]

class Series(BaseType):
    def __init__(self, itempage, repo=None):
        super().__init__(itempage, repo)

    @property
    def constraints(self):
        return self._property_constraints()

    def _property_constraints(self):
        return [has_property(prop) for prop in (
            wp.INSTANCE_OF,
            wp.TITLE,
            wp.ORIGINAL_NETWORK,
            wp.COUNTRY_OF_ORIGIN,
            wp.ORIGNAL_LANGUAGE_OF_FILM_OR_TV_SHOW,
            wp.PRODUCTION_COMPANY,
            wp.IMDB_ID,
        )]
