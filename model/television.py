"""Wrapper classes for high-level concepts relating to TV series"""

from pywikibot import ItemPage, Site
from pywikibot.pagegenerators import WikidataSPARQLPageGenerator

from constraints import *
import properties.wikidata_properties as wp
from sparql.query_builder import generate_sparql_query
import sparql.queries as Q

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
    def title(self):
        return self._itempage.title()

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

    def refresh(self):
        self._itempage.get()

    def __str__(self):
        return f"{self.__class__.__name__}({self.title} ({self.label}))"

    def __repr__(self):
        return self.__str__()

class Episode(BaseType):
    """Encapsulates an item of instance 'television series episode'"""
    @property
    def constraints(self):
        return self._property_constraints() + self._inheritance_constraints()

    @property
    def parent(self):
        """Return the Season/Series of this Episode"""
        if self.season_itempage is None:
            if self.series_itempage is None:
                return None
            return Series(self.series_itempage)
        return Season(self.season_itempage)

    @property
    def next(self):
        """Return the next episode, if any"""
        # Check if it has the FOLLOWED_BY field set
        if wp.FOLLOWED_BY.pid in self.claims:
            next_episode_itempage = self.claims[wp.FOLLOWED_BY.pid][0].getTarget()
            return Episode(next_episode_itempage)

        # Find the item that has the FOLLOWS field set to this item
        query = generate_sparql_query({wp.FOLLOWS.pid: self.title})
        gen = WikidataSPARQLPageGenerator(query)
        is_followed_by = next(gen, None)

        if is_followed_by is not None:
            return Episode(is_followed_by)

        # Find the item whose ordinal is one higher for this series
        if self.ordinal_in_series is not None:
            return self.next_in_series

        # Find the item whose ordinal is one higher for this season
        if self.ordinal_in_season is not None:
            return self.next_in_season

        return None

    @property
    def previous(self):
        """Return the previous episode, if any"""
        # Check if it has the FOLLOWS field set
        if wp.FOLLOWS.pid in self.claims:
            previous_episode_itempage = self.claims[wp.FOLLOWS.pid][0].getTarget()
            return Episode(previous_episode_itempage)

        # Find the item that has the FOLLOWED_BY field set to this item
        query = generate_sparql_query({wp.FOLLOWED_BY.pid: self.title})
        gen = WikidataSPARQLPageGenerator(query)
        follows = next(gen, None)

        if follows is not None:
            return Episode(follows)

        # Find the item whose ordinal is one lower for this series
        if self.ordinal_in_series is not None:
            return self.previous_in_series

        # Find the item whose ordinal is one lower for this season
        if self.ordinal_in_season is not None:
            return self.previous_in_season

        return None

    @property
    def previous_in_season(self):
        if self.ordinal_in_season is None:
            return None
        query = f"""SELECT ?item WHERE {{
            ?item wdt:{wp.INSTANCE_OF.pid} wd:{wp.TELEVISION_SERIES_EPISODE}.
            ?item wdt:{wp.PART_OF_THE_SERIES.pid} wd:{self.part_of_the_series}.
            ?item wdt:{wp.SEASON.pid} wd:{self.season}.
            ?item p:{wp.SEASON.pid}/pq:{wp.SERIES_ORDINAL.pid} "{self.ordinal_in_season - 1}"
            }}
        """
        gen = WikidataSPARQLPageGenerator(query)
        previous_episode_itempage = next(gen, None)
        if previous_episode_itempage is None:
            return None

        return Episode(previous_episode_itempage)

    @property
    def next_in_season(self):
        """Return the next Episode from the same season"""
        if self.ordinal_in_season is None:
            return None
        query = f"""SELECT ?item WHERE {{
            ?item wdt:{wp.INSTANCE_OF.pid} wd:{wp.TELEVISION_SERIES_EPISODE}.
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
    def previous_in_series(self):
        """Return the next Episode from the same series"""
        if self.ordinal_in_series is None:
            return None
        query = f"""SELECT ?item WHERE {{
            ?item wdt:{wp.INSTANCE_OF.pid} wd:{wp.TELEVISION_SERIES_EPISODE}.
            ?item wdt:{wp.PART_OF_THE_SERIES.pid} wd:{self.part_of_the_series}.
            ?item p:{wp.PART_OF_THE_SERIES.pid}/pq:{wp.SERIES_ORDINAL.pid} "{self.ordinal_in_series - 1}"
            }}
        """
        gen = WikidataSPARQLPageGenerator(query)
        previous_episode_itempage = next(gen, None)
        if previous_episode_itempage is None:
            return None

        return Episode(previous_episode_itempage)

    @property
    def next_in_series(self):
        """Return the next Episode from the same series"""
        if self.ordinal_in_series is None:
            return None
        query = f"""SELECT ?item WHERE {{
            ?item wdt:{wp.INSTANCE_OF.pid} wd:{wp.TELEVISION_SERIES_EPISODE}.
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
    def series_itempage(self):
        if wp.PART_OF_THE_SERIES.pid not in self.claims:
            return None
        series_itempage = self.claims[wp.PART_OF_THE_SERIES.pid][0].getTarget()
        if series_itempage is None:
            return None
        series_itempage.get()
        return series_itempage

    @property
    def part_of_the_series(self):
        """The ID of the series of which this episode is a part"""
        if self.series_itempage is None:
            return None
        return self.series_itempage.title()

    @property
    def season_itempage(self):
        """The itempage of the season of which this episode is a part"""
        if wp.SEASON.pid not in self.claims:
            return None
        season_itempage = self.claims[wp.SEASON.pid][0].getTarget()
        if season_itempage is None:
            return None
        season_itempage.get()
        return season_itempage

    @property
    def season(self):
        """The ID of the season of which this episode is a part"""
        if self.season_itempage is None:
            return None
        return self.season_itempage.title()

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
            wp.PART_OF_THE_SERIES,
        )]

class Season(BaseType):
    """Encapsulates an item of instance 'television series season'"""
    def __init__(self, itempage, repo=None):
        super(Season, self).__init__(itempage, repo)
        if wp.INSTANCE_OF.pid not in itempage.claims:
            raise ValueError(f"'instance of' unset. Must be set to 'television series season' for {itempage.title()}")
        instance_of = itempage.claims[wp.INSTANCE_OF.pid][0].getTarget().title()
        if instance_of != wp.TELEVISION_SERIES_SEASON:
            raise ValueError(f"expected 'instance of' to be set to 'television series season' for {itempage.title()}, found {instance_of}")

    @property
    def parent(self):
        series_itempage = self.claims[wp.PART_OF_THE_SERIES.pid][0].getTarget()
        return Series(series_itempage)

    @property
    def part_of_the_series(self):
        """The ID of the series of which this episode is a part"""
        if wp.PART_OF_THE_SERIES.pid not in self.claims:
            return None
        return self.claims[wp.PART_OF_THE_SERIES.pid][0].getTarget().title()

    @property
    def ordinal_in_series(self):
        if not wp.PART_OF_THE_SERIES.pid in self.claims:
            return None
        series_claim = self.claims[wp.PART_OF_THE_SERIES.pid][0]
        if wp.SERIES_ORDINAL.pid not in series_claim.qualifiers:
            return None

        return int(series_claim.qualifiers[wp.SERIES_ORDINAL.pid][0].getTarget())

    @property
    def next_in_series(self):
        """Return the next season from the same series"""
        if self.ordinal_in_series is None:
            return None
        query = f"""SELECT ?item WHERE {{
            ?item wdt:{wp.INSTANCE_OF.pid} wd:{wp.TELEVISION_SERIES_SEASON}.
            ?item wdt:{wp.PART_OF_THE_SERIES.pid} wd:{self.part_of_the_series}.
            ?item p:{wp.PART_OF_THE_SERIES.pid}/pq:{wp.SERIES_ORDINAL.pid} "{self.ordinal_in_series + 1}"
            }}
        """
        gen = WikidataSPARQLPageGenerator(query)
        next_season_itempage = next(gen, None)
        if next_season_itempage is None:
            return None

        return Season(next_season_itempage)

    @property
    def previous_in_series(self):
        """Return the previous season from the same series"""
        if self.ordinal_in_series is None:
            return None
        query = f"""SELECT ?item WHERE {{
            ?item wdt:{wp.INSTANCE_OF.pid} wd:{wp.TELEVISION_SERIES_SEASON}.
            ?item wdt:{wp.PART_OF_THE_SERIES.pid} wd:{self.part_of_the_series}.
            ?item p:{wp.PART_OF_THE_SERIES.pid}/pq:{wp.SERIES_ORDINAL.pid} "{self.ordinal_in_series - 1}"
            }}
        """
        gen = WikidataSPARQLPageGenerator(query)
        previous_season_itempage = next(gen, None)
        if previous_season_itempage is None:
            return None

        return Season(previous_season_itempage)

    @property
    def next(self):
        """Return the next season, if any"""
        # Check if it has the FOLLOWED_BY field set
        if wp.FOLLOWED_BY.pid in self.claims:
            next_season_itempage = self.claims[wp.FOLLOWED_BY.pid][0].getTarget()
            return Season(next_season_itempage)

        # Find the item that has the FOLLOWS field set to this item
        query = generate_sparql_query({wp.FOLLOWS.pid: self.title})
        gen = WikidataSPARQLPageGenerator(query)
        is_followed_by = next(gen, None)

        if is_followed_by is not None:
            return Season(is_followed_by)

        # Find the item whose ordinal is one higher for this series
        if self.ordinal_in_series is not None:
            return self.next_in_series

        return None

    @property
    def previous(self):
        """Return the previous season, if any"""
        # Check if it has the FOLLOWS field set
        if wp.FOLLOWS.pid in self.claims:
            previous_season_itempage = self.claims[wp.FOLLOWS.pid][0].getTarget()
            return Season(previous_season_itempage)

        # Find the item that has the FOLLOWED_BY field set to this item
        query = generate_sparql_query({wp.FOLLOWED_BY.pid: self.title})
        gen = WikidataSPARQLPageGenerator(query)
        follows = next(gen, None)

        if follows is not None:
            return Season(follows)

        # Find the item whose ordinal is one lower for this series
        if self.ordinal_in_series is not None:
            return self.previous_in_series

        return None

    @property
    def parts(self):
        for ordinal, episode_id, _ in sorted(Q.episodes(self.title)):
            yield ordinal, Episode(ItemPage(self.repo, episode_id))

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
            wp.HAS_PART,
            wp.NUMBER_OF_EPISODES,
            wp.FOLLOWS,
            wp.FOLLOWED_BY,
        )] + [
            season_has_no_of_episodes_as_count_of_parts(),
            season_has_parts(),
        ]

    def _inheritance_constraints(self):
        return [inherits_property(prop) for prop in (
            wp.ORIGINAL_NETWORK,
            wp.COUNTRY_OF_ORIGIN,
            wp.ORIGNAL_LANGUAGE_OF_FILM_OR_TV_SHOW,
            wp.PRODUCTION_COMPANY,
        )]

class Series(BaseType):
    """Encapsulates an item of instance 'television series'"""
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
