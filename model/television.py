"""Wrapper classes for high-level concepts relating to TV series"""

from functools import partial

from constraints import has_property, inherits_property
from constraints import follows_something, is_followed_by_something
import properties.wikidata_properties as wp

class BaseType():
    def __init__(self, itempage, repo):
        self._itempage = itempage
        self._itempage.get()
        self._repo = repo

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

    def __str__(self):
        return f"{self.__class__.__name__}({self._itempage.title()} ({self.label}))"

    def __repr__(self):
        return self.__str__()

class Episode(BaseType):
    def __init__(self, itempage, repo):
        super().__init__(itempage, repo)

    @property
    def constraints(self):
        return self._property_constraints() + self._inheritance_constraints()

    @property
    def parent(self):
        season_itempage = self._itempage.claims[wp.SEASON.pid][0].getTarget()
        return Season(season_itempage, self.repo)

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
    def __init__(self, itempage, repo):
        super().__init__(itempage, repo)

    @property
    def parent(self):
        series_itempage = self._itempage.claims[wp.PART_OF_THE_SERIES.pid][0].getTarget()
        return Series(series_itempage, self.repo)

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
    def __init__(self, itempage, repo):
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
