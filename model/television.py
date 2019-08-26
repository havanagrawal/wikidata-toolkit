"""Wrapper classes for high-level concepts relating to TV series"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from pywikibot import ItemPage, WbMonolingualText
from pywikibot.pagegenerators import WikidataSPARQLPageGenerator

import constraints.general as gc
import constraints.tv as tvc
import model.api as api
import properties.wikidata_properties as wp
import sparql.queries as Q
from sparql.query_builder import generate_sparql_query


class TvBase(api.BaseType, ABC):
    """Superclass for all television related entities"""

    @property
    @abstractmethod
    def constraints(self):
        return []

    @property
    def title(self) -> Optional[str]:
        """The English (en) title (P1476) of this entity"""
        title_wb: WbMonolingualText = self.first_claim(wp.TITLE.pid)
        if title_wb is None or title_wb.language != 'en':
            return None
        return title_wb.text


class Episode(TvBase, api.Heirarchical, api.Chainable):
    """Encapsulates an item of instance 'television series episode'"""

    @property
    def constraints(self):
        return (
            [
                gc.has_property(prop)
                for prop in (
                    wp.INSTANCE_OF,
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
                )
            ]
            + [
                gc.follows_something(),
                gc.is_followed_by_something(),
                tvc.has_title(),
                tvc.has_english_label(),
                tvc.episode_has_english_description(),
            ]
            + [
                gc.inherits_property(prop)
                for prop in (
                    wp.COUNTRY_OF_ORIGIN,
                    wp.ORIGNAL_LANGUAGE_OF_FILM_OR_TV_SHOW,
                    wp.PART_OF_THE_SERIES,
                )
            ]
        )

    @property
    def parent(self):
        """The Season/Series of this Episode"""
        if self.season_itempage is not None:
            return self.season

        if self.series_itempage is not None:
            return self.series

        return None


    @property
    def next(self) -> Optional[Episode]:
        """The next episode, if any"""
        # Check if it has the FOLLOWED_BY field set
        next_episode_itempage = self.first_claim(wp.FOLLOWED_BY.pid)
        if next_episode_itempage is not None:
            return Episode(next_episode_itempage)

        # Find the item that has the FOLLOWS field set to this item
        query = generate_sparql_query({wp.FOLLOWS.pid: self.qid})
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
    def previous(self) -> Optional[Episode]:
        """The previous episode, if any"""
        # Check if it has the FOLLOWS field set
        previous_episode_itempage = self.first_claim(wp.FOLLOWS.pid)
        if previous_episode_itempage is not None:
            return Episode(previous_episode_itempage)

        # Find the item that has the FOLLOWED_BY field set to this item
        query = generate_sparql_query({wp.FOLLOWED_BY.pid: self.qid})
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
    def previous_in_season(self) -> Optional[Episode]:
        """The previous Episode from the same season"""
        if self.ordinal_in_season is None:
            return None
        query = f"""SELECT ?item WHERE {{
            ?item wdt:{wp.INSTANCE_OF.pid} wd:{wp.TELEVISION_SERIES_EPISODE}.
            ?item wdt:{wp.PART_OF_THE_SERIES.pid} wd:{self.series_qid}.
            ?item wdt:{wp.SEASON.pid} wd:{self.season_qid}.
            ?item p:{wp.SEASON.pid}/pq:{wp.SERIES_ORDINAL.pid} "{self.ordinal_in_season - 1}"
            }}
        """
        gen = WikidataSPARQLPageGenerator(query)
        previous_episode_itempage = next(gen, None)
        if previous_episode_itempage is None:
            return None

        return Episode(previous_episode_itempage)

    @property
    def next_in_season(self) -> Optional[Episode]:
        """The next Episode from the same season"""
        if self.ordinal_in_season is None:
            return None
        query = f"""SELECT ?item WHERE {{
            ?item wdt:{wp.INSTANCE_OF.pid} wd:{wp.TELEVISION_SERIES_EPISODE}.
            ?item wdt:{wp.PART_OF_THE_SERIES.pid} wd:{self.series_qid}.
            ?item wdt:{wp.SEASON.pid} wd:{self.season_qid}.
            ?item p:{wp.SEASON.pid}/pq:{wp.SERIES_ORDINAL.pid} "{self.ordinal_in_season + 1}"
            }}
        """
        gen = WikidataSPARQLPageGenerator(query)
        next_episode_itempage = next(gen, None)
        if next_episode_itempage is None:
            return None

        return Episode(next_episode_itempage)

    @property
    def previous_in_series(self) -> Optional[Episode]:
        """The previous Episode from the same series"""
        if self.ordinal_in_series is None:
            return None
        query = f"""SELECT ?item WHERE {{
            ?item wdt:{wp.INSTANCE_OF.pid} wd:{wp.TELEVISION_SERIES_EPISODE}.
            ?item wdt:{wp.PART_OF_THE_SERIES.pid} wd:{self.series_qid}.
            ?item p:{wp.PART_OF_THE_SERIES.pid}/pq:{wp.SERIES_ORDINAL.pid} "{self.ordinal_in_series - 1}"
            }}
        """
        gen = WikidataSPARQLPageGenerator(query)
        previous_episode_itempage = next(gen, None)
        if previous_episode_itempage is None:
            return None

        return Episode(previous_episode_itempage)

    @property
    def next_in_series(self) -> Optional[Episode]:
        """The next Episode from the same series"""
        if self.ordinal_in_series is None:
            return None
        query = f"""SELECT ?item WHERE {{
            ?item wdt:{wp.INSTANCE_OF.pid} wd:{wp.TELEVISION_SERIES_EPISODE}.
            ?item wdt:{wp.PART_OF_THE_SERIES.pid} wd:{self.series_qid}.
            ?item p:{wp.PART_OF_THE_SERIES.pid}/pq:{wp.SERIES_ORDINAL.pid} "{self.ordinal_in_series + 1}"
            }}
        """
        gen = WikidataSPARQLPageGenerator(query)
        next_episode_itempage = next(gen, None)
        if next_episode_itempage is None:
            return None

        return Episode(next_episode_itempage)

    @property
    def series_itempage(self) -> Optional[ItemPage]:
        """The itempage of the series of which this episode is a part"""
        series_itempage = self.first_claim(wp.PART_OF_THE_SERIES.pid)
        if series_itempage is None:
            return None
        series_itempage.get()
        return series_itempage

    @property
    def series(self) -> Optional[Series]:
        if self.series_itempage is None:
            return None
        return Series(self.series_itempage, self._repo)

    @property
    def series_qid(self) -> Optional[str]:
        """The ID of the series of which this episode is a part"""
        if self.series_itempage is None:
            return None
        return self.series_itempage.title()

    @property
    def season_itempage(self) -> Optional[ItemPage]:
        """The itempage of the season of which this episode is a part"""
        season_itempage = self.first_claim(wp.SEASON.pid)
        if season_itempage is None:
            return None
        season_itempage.get()
        return season_itempage

    @property
    def season(self) -> Optional[Season]:
        """The ID of the season of which this episode is a part"""
        if self.season_itempage is None:
            return None
        return Season(self.season_itempage, self._repo)

    @property
    def season_qid(self) -> Optional[str]:
        if self.season_itempage is None:
            return None
        return self.season_itempage.title()

    @property
    def ordinal_in_series(self) -> Optional[int]:
        """The series ordinal for this episode"""
        if not wp.PART_OF_THE_SERIES.pid in self.claims:
            return None
        series_claim = self.claims[wp.PART_OF_THE_SERIES.pid][0]
        if wp.SERIES_ORDINAL.pid not in series_claim.qualifiers:
            return None

        return int(series_claim.qualifiers[wp.SERIES_ORDINAL.pid][0].getTarget())

    @property
    def ordinal_in_season(self) -> Optional[int]:
        """The season ordinal for this episode"""
        if wp.SEASON.pid not in self.claims:
            return None
        series_claim = self.claims[wp.SEASON.pid][0]
        if wp.SERIES_ORDINAL.pid not in series_claim.qualifiers:
            return None

        return int(series_claim.qualifiers[wp.SERIES_ORDINAL.pid][0].getTarget())


class Season(TvBase, api.Heirarchical, api.Chainable):
    """Encapsulates an item of instance 'television series season'"""

    def __init__(self, itempage: ItemPage, repo=None):
        super(Season, self).__init__(itempage, repo)
        if wp.INSTANCE_OF.pid not in itempage.claims:
            raise ValueError(
                f"'instance of' unset. Must be set to 'television series season' for {itempage.title()}"
            )
        instance_of = itempage.claims[wp.INSTANCE_OF.pid][0].getTarget().title()
        if instance_of != wp.TELEVISION_SERIES_SEASON:
            raise ValueError(
                f"expected 'instance of' to be set to 'television series season' for {itempage.title()}, found {instance_of}"
            )

    @property
    def parent(self):
        """The Series of which this season is a part"""
        series_itempage = self.first_claim(wp.PART_OF_THE_SERIES.pid)
        return Series(series_itempage)

    @property
    def series_qid(self) -> Optional[str]:
        """The ID of the series of which this episode is a part"""
        series = self.first_claim(wp.PART_OF_THE_SERIES.pid)
        if series is not None:
            return series.title()
        return None

    @property
    def ordinal_in_series(self) -> Optional[int]:
        """The series ordinal for this season"""
        if wp.PART_OF_THE_SERIES.pid not in self.claims:
            return None
        series_claim = self.claims[wp.PART_OF_THE_SERIES.pid][0]
        if wp.SERIES_ORDINAL.pid not in series_claim.qualifiers:
            return None

        return int(series_claim.qualifiers[wp.SERIES_ORDINAL.pid][0].getTarget())

    @property
    def next_in_series(self) -> Optional[Season]:
        """The next season from the same series"""
        if self.ordinal_in_series is None:
            return None
        query = f"""SELECT ?item WHERE {{
            ?item wdt:{wp.INSTANCE_OF.pid} wd:{wp.TELEVISION_SERIES_SEASON}.
            ?item wdt:{wp.PART_OF_THE_SERIES.pid} wd:{self.series_qid}.
            ?item p:{wp.PART_OF_THE_SERIES.pid}/pq:{wp.SERIES_ORDINAL.pid} "{self.ordinal_in_series + 1}"
            }}
        """
        gen = WikidataSPARQLPageGenerator(query)
        next_season_itempage = next(gen, None)
        if next_season_itempage is None:
            return None

        return Season(next_season_itempage)

    @property
    def previous_in_series(self) -> Optional[Season]:
        """The previous season from the same series"""
        if self.ordinal_in_series is None:
            return None
        query = f"""SELECT ?item WHERE {{
            ?item wdt:{wp.INSTANCE_OF.pid} wd:{wp.TELEVISION_SERIES_SEASON}.
            ?item wdt:{wp.PART_OF_THE_SERIES.pid} wd:{self.series_qid}.
            ?item p:{wp.PART_OF_THE_SERIES.pid}/pq:{wp.SERIES_ORDINAL.pid} "{self.ordinal_in_series - 1}"
            }}
        """
        gen = WikidataSPARQLPageGenerator(query)
        previous_season_itempage = next(gen, None)
        if previous_season_itempage is None:
            return None

        return Season(previous_season_itempage)

    @property
    def next(self) -> Optional[Season]:
        """The next season, if any"""
        # Check if it has the FOLLOWED_BY field set
        next_season_itempage = self.first_claim(wp.FOLLOWED_BY.pid)
        if next_season_itempage is not None:
            return Season(next_season_itempage)

        # Find the item that has the FOLLOWS field set to this item
        query = generate_sparql_query({wp.FOLLOWS.pid: self.qid})
        gen = WikidataSPARQLPageGenerator(query)
        is_followed_by = next(gen, None)

        if is_followed_by is not None:
            return Season(is_followed_by)

        # Find the item whose ordinal is one higher for this series
        if self.ordinal_in_series is not None:
            return self.next_in_series

        return None

    @property
    def previous(self) -> Optional[Season]:
        """The previous season, if any"""
        # Check if it has the FOLLOWS field set
        previous_season_itempage = self.first_claim(wp.FOLLOWS.pid)
        if previous_season_itempage is not None:
            return Season(previous_season_itempage)

        # Find the item that has the FOLLOWED_BY field set to this item
        query = generate_sparql_query({wp.FOLLOWED_BY.pid: self.qid})
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
        """An iterable of (ordinal, Episode) that are parts of this season"""
        for ordinal, episode_id, _ in sorted(Q.episodes(self.qid)):
            yield ordinal, Episode(ItemPage(self.repo, episode_id))

    @property
    def constraints(self):
        return (
            [
                gc.has_property(prop)
                for prop in (
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
                )
            ]
            + [
                tvc.season_has_no_of_episodes_as_count_of_parts(),
                tvc.season_has_parts(),
            ]
            + [
                gc.inherits_property(prop)
                for prop in (
                    wp.COUNTRY_OF_ORIGIN,
                    wp.ORIGNAL_LANGUAGE_OF_FILM_OR_TV_SHOW,
                )
            ]
        )


class Series(TvBase, api.Heirarchical):
    """Encapsulates an item of instance 'television series'"""

    @property
    def constraints(self):
        return [
            gc.has_property(prop)
            for prop in (
                wp.INSTANCE_OF,
                wp.TITLE,
                wp.ORIGINAL_NETWORK,
                wp.COUNTRY_OF_ORIGIN,
                wp.ORIGNAL_LANGUAGE_OF_FILM_OR_TV_SHOW,
                wp.PRODUCTION_COMPANY,
                wp.IMDB_ID,
            )
        ]
