"""Constraint abstract definition and implementations"""

from typing import Callable, Iterable
from pywikibot import Claim, WbMonolingualText
from pywikibot.pagegenerators import WikidataSPARQLPageGenerator

import properties.wikidata_properties as wp
from utils import RepoUtils, copy_delayed, imdb_title, tv_com_title
from sparql.query_builder import generate_sparql_query

class Constraint():
    """A constraint on data consistency/quality

        A constraint has two parts: a validator and a fixer
        The validator verifies if the constraint is satisfied or not,
        and the fixer can attempt to make the data satisfy the constraint.

        In principle, this is very similar to how Wikidata validates constraints,
        but allows for a simpler and more extensible programmatic model.

        Note: The fixer should only fix the item under consideration, and not
              any items referenced by it. This helps keep the script and the
              developer sane.
    """
    def __init__(self, validator: Callable[..., bool], fixer: Callable[..., Iterable]=None, name=None):
        self._validator = validator
        self._name = name
        self._fixer = fixer

    def validate(self, item):
        """Return True if the item satisfies the constraint, else False"""
        return self._validator(item)

    def fix(self, item):
        """Return a list of claims that, if implemented, will fix the constraint failure"""
        if self._fixer is None:
            print(f"No autofix available for {self._name}:{item}")
            return []
        return self._fixer(item)

    def __str__(self):
        return self._name

    def __repr__(self):
        return self.__str__()

def has_property(prop: wp.WikidataProperty):
    """Constraint for 'item has a certain property'"""
    def check(item):
        return prop.pid in item.claims

    return Constraint(validator=check, name=f"has_property({prop.name})")

def inherits_property(prop: wp.WikidataProperty):
    """Constraint for 'item inherits property from parent item'

        The definition of a "parent" depends on the item itself. For example,
        the parent item of an Episode is a Season, and the episode is
        expected to inherit properties such as country of origin (P495)
    """
    @item_has_parent
    def check(item):
        item_claims = item.claims
        parent_claims = item.parent.claims

        if prop.pid not in item_claims or prop.pid not in parent_claims:
            return False

        item_targets = [claim.getTarget() for claim in item_claims[prop.pid]]
        parent_targets = [claim.getTarget() for claim in parent_claims[prop.pid]]

        item_titles = {t.title() for t in item_targets}
        parent_titles = {t.title() for t in parent_targets}

        return item_titles == parent_titles

    @item_has_parent
    def fix(item):
        if prop.pid not in item.parent.claims:
            return []

        return copy_delayed(item.parent.itempage, item.itempage, [prop])

    return Constraint(
        check,
        fixer=fix,
        name=f"inherits_property({prop.name})"
    )

def item_has_parent(func):
    def wrapper(*args, **kwargs):
        item = args[0]
        has_parent = item.parent is not None
        if not has_parent:
            print(f"{item} has no concept of parent")
            return []

        return func(*args, **kwargs)

    return wrapper

def follows_something():
    """Alias for has_property(wp.FOLLOWS), but with an autofix"""
    def check(item):
        return wp.FOLLOWS.pid in item.claims

    def fix(item):
        follows = item.previous

        if follows is None:
            print(f"autofix for follows_something({item.title}) failed")
            return []

        new_claim = Claim(item.repo, wp.FOLLOWS.pid)
        new_claim.setTarget(follows.itempage)
        summary = f'Setting {wp.FOLLOWS.pid} ({wp.FOLLOWS.name})'
        return [(new_claim, summary, item.itempage)]

    return Constraint(
        check,
        fixer=fix,
        name=f"follows_something()"
    )

def is_followed_by_something():
    """Alias for has_property(wp.FOLLOWED_BY), but with an autofix"""
    def check(item):
        return wp.FOLLOWED_BY.pid in item.claims

    def fix(item):
        is_followed_by = item.next

        if is_followed_by is None:
            print(f"autofix for is_followed_by({item.title}) failed")
            return []

        new_claim = Claim(item.repo, wp.FOLLOWED_BY.pid)
        new_claim.setTarget(is_followed_by.itempage)
        summary = f'Setting {wp.FOLLOWED_BY.pid} ({wp.FOLLOWED_BY.name})'
        return [(new_claim, summary, item.itempage)]

    return Constraint(
        check,
        fixer=fix,
        name=f"is_followed_by_something()"
    )

def season_has_no_of_episodes_as_count_of_parts():
    def check(item):
        return (
            wp.HAS_PART.pid in item.claims and
            wp.NUMBER_OF_EPISODES.pid in item.claims and
            len(item.claims[wp.HAS_PART.pid]) == int(item.claims[wp.NUMBER_OF_EPISODES.pid][0].getTarget().amount)
        )

    return Constraint(
        check,
        name=f"season_has_no_of_episodes_as_count_of_parts()",
    )

def season_has_parts():
    def check(item):
        return wp.HAS_PART.pid in item.claims

    def fix(item):
        claim_fixes = []

        for ordinal, episode in item.parts:
            qualifier = Claim(item.repo, wp.SERIES_ORDINAL.pid)
            qualifier.setTarget(str(ordinal))

            new_claim = Claim(item.repo, wp.HAS_PART.pid)
            new_claim.setTarget(episode.itempage)
            new_claim.addQualifier(qualifier)
            summary = f'Adding {episode.title} to {wp.HAS_PART.pid}'
            claim_fixes.append((new_claim, summary, item.itempage))

        return claim_fixes

    return Constraint(
        check,
        fixer=fix,
        name=f"season_has_parts()",
    )

def has_title():
    """Alias for has_property(wp.TITLE), but with an autofix"""
    def check(item):
        return wp.TITLE.pid in item.claims

    def fix(item):
        title = item.itempage.labels.get('en', None)
        # Lookup IMDB
        if title is None:
            if wp.IMDB_ID.pid not in item.claims:
                return []
            imdb_id = item.claims[wp.IMDB_ID.pid][0].getTarget()
            title = imdb_title(imdb_id)
            print(f"Fetched title='{title}' from IMDB using {imdb_id}")
        # Lookup tv.com
        if title is None:
            if wp.TV_COM_ID.pid not in item.claims:
                return []
            tv_com_id = item.claims[wp.TV_COM_ID.pid][0].getTarget()
            title = tv_com_title(tv_com_id)
            print(f"Fetched title='{title}' from TV.com using {tv_com_id}")
        new_claim = Claim(item.repo, wp.TITLE.pid)
        new_claim.setTarget(WbMonolingualText(title, 'en'))
        summary = f'Setting {wp.TITLE} to {title}'
        return [(new_claim, summary, item.itempage)]

    return Constraint(
        check,
        fixer=fix,
        name="has_title()",
    )
