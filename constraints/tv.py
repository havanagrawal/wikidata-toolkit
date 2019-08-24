"""Constraint abstract definition and implementations"""
from __future__ import annotations

from typing import Iterable

from pywikibot import Claim, WbMonolingualText

import constraints.api as api
import model.television
import properties.wikidata_properties as wp
from utils import imdb_title, tv_com_title


def season_has_no_of_episodes_as_count_of_parts() -> api.Constraint:
    def check(item: model.television.Season) -> bool:
        return (
            wp.HAS_PART.pid in item.claims
            and wp.NUMBER_OF_EPISODES.pid in item.claims
            and len(item.claims[wp.HAS_PART.pid])
            == int(item.first_claim(wp.NUMBER_OF_EPISODES.pid).amount)
        )

    return api.Constraint(check, name=f"season_has_no_of_episodes_as_count_of_parts()")


def season_has_parts() -> api.Constraint:
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
    """Check if an item has an English label

        This fix cannot be accumulated.
    """

    def check(item: model.television.TvBase) -> bool:
        return item.label is not None

    def fix(item: model.television.TvBase) -> Iterable:
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
