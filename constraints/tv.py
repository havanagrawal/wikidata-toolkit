"""Constraint abstract definition and implementations"""
from __future__ import annotations

from typing import Iterable

from pywikibot import Claim, WbMonolingualText, WbQuantity

import constraints.api as api
import model.television
import properties.wikidata_properties as wp
from utils import imdb_title, tv_com_title, no_of_episodes


def season_has_no_of_episodes_as_count_of_parts() -> api.Constraint:
    """Check if a season has its 'no of episodes' (P1113) set to the number of parts

        Eg: If a season (S1) has 8 values in its 'has part' field,
        it should have 8 as its 'no of episodes' field
    """

    def check(item: model.television.Season) -> bool:
        return (
            wp.HAS_PART.pid in item.claims
            and wp.NUMBER_OF_EPISODES.pid in item.claims
            and len(item.claims[wp.HAS_PART.pid])
            == int(item.first_claim(wp.NUMBER_OF_EPISODES.pid).amount)
        )

    return api.Constraint(check, name=f"season_has_no_of_episodes_as_count_of_parts()")


def season_has_parts() -> api.Constraint:
    """Check if a season has its episodes listed as its parts

        Eg: A season with 10 episodes (S1 E1 to S1 E10) must have all 10 episodes in its 'has part' property
    """

    def check(item: model.television.Season) -> bool:
        return wp.HAS_PART.pid in item.claims

    def fix(item: model.television.Season) -> Iterable[api.Fix]:
        claim_fixes = []

        for ordinal, episode in item.parts:
            qualifier = Claim(item.repo, wp.SERIES_ORDINAL.pid)
            qualifier.setTarget(str(ordinal))

            new_claim = Claim(item.repo, wp.HAS_PART.pid)
            new_claim.setTarget(episode.itempage)
            new_claim.addQualifier(qualifier)
            summary = f"Adding {episode.qid} to {wp.HAS_PART.pid} ({wp.HAS_PART.name})"
            claim_fixes.append(api.ClaimFix(new_claim, summary, item.itempage))

        return claim_fixes

    return api.Constraint(check, fixer=fix, name=f"season_has_parts()")


def has_title() -> api.Constraint:
    """Alias for has_property(wp.TITLE), but with an autofix"""

    def check(item: model.television.TvBase) -> bool:
        return wp.TITLE.pid in item.claims

    def fix(item: model.television.TvBase) -> Iterable[api.Fix]:
        title = None
        # For logging only
        _src, _src_key = None, None
        # Lookup IMDB
        if title is None:
            imdb_id = item.first_claim(wp.IMDB_ID.pid)
            title = imdb_title(imdb_id)
            _src, _src_key = "IMDB", imdb_id
        # Lookup tv.com
        if title is None:
            tv_com_id = item.first_claim(wp.TV_COM_ID.pid)
            title = tv_com_title(tv_com_id)
            _src, _src_key = "TV.com", tv_com_id
        # Lookup label
        if title is None:
            title = item.label
            _src, _src_key = "label", "en"
        # Did not find a title from any source
        if title is None:
            return []
        print(f"Fetched title='{title}' from {_src} using {_src_key}")
        new_claim = Claim(item.repo, wp.TITLE.pid)
        new_claim.setTarget(WbMonolingualText(title, "en"))
        summary = f"Setting {wp.TITLE} to {title}"
        return [api.ClaimFix(new_claim, summary, item.itempage)]

    return api.Constraint(check, fixer=fix, name="has_title()")


def has_english_label() -> api.Constraint:
    """Check if an item has an English label"""

    def check(item: model.television.TvBase) -> bool:
        return item.label is not None

    def fix(item: model.television.TvBase) -> Iterable[api.LabelFix]:
        item.refresh()
        _src, _src_key = "Title", "en"
        label = item.label
        # Lookup IMDB
        if label is None:
            imdb_id = item.first_claim(wp.IMDB_ID.pid)
            label = imdb_title(imdb_id)
            _src, _src_key = "IMDB", imdb_id
        # Lookup tv.com
        if label is None:
            tv_com_id = item.first_claim(wp.TV_COM_ID.pid)
            label = tv_com_title(tv_com_id)
            _src, _src_key = "TV.com", tv_com_id
        if label is not None:
            return [api.LabelFix(label, "en", item.itempage)]
        return []

    return api.Constraint(check, fixer=fix, name="has_english_label()")


def episode_has_english_description() -> api.Constraint:
    """Check if an episode has an English description

        The fix is to use (in decreasing order of preference)
            1. 'episode of <series> (S<season_no> E<episode_no>)'
            2. 'episode of <series> (S<season_no>)'
            3. 'episode of <series>'
    """

    def check(item: model.television.Episode) -> bool:
        return item.description is not None

    def fix(item: model.television.Episode) -> Iterable[api.DescriptionFix]:
        def _description(item: model.television.Episode):
            if item.series is None or item.series.title is None:
                return None

            series_name = item.series.title
            if item.season is None or item.season.ordinal_in_series is None:
                return f"episode of {series_name}"

            season_no = str(item.season.ordinal_in_series).rjust(2, "0")
            if item.ordinal_in_season is None:
                return f"episode of {series_name} (S{season_no})"

            episode_no = str(item.ordinal_in_season).rjust(2, "0")
            return f"episode of {series_name} (S{season_no} E{episode_no})"

        description = _description(item)
        if description is None:
            return []
        return [api.DescriptionFix(description, lang="en", itempage=item.itempage)]

    return api.Constraint(check, fixer=fix, name="episode_has_english_description()")


def series_has_no_of_episodes():
    def check(item: model.television.Series) -> bool:
        return wp.NUMBER_OF_EPISODES.pid in item.claims

    def fix(item: model.television.Series) -> Iterable[api.ClaimFix]:
        if wp.IMDB_ID.pid not in item.claims:
            return []

        number_of_episodes = no_of_episodes(item.first_claim(wp.IMDB_ID.pid))
        if number_of_episodes is None:
            return []

        claim = Claim(item.repo, wp.NUMBER_OF_EPISODES.pid)
        claim.setTarget(WbQuantity(number_of_episodes, site=item.repo))
        summary = f"Setting {wp.NUMBER_OF_EPISODES} to {number_of_episodes}"

        return [api.ClaimFix(claim, summary=summary, itempage=item.itempage)]

    return api.Constraint(check, fixer=fix, name=f"series_has_no_of_episodes()")
