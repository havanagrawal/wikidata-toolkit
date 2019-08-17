"""General constraints applicable to base types"""

from typing import Iterable

from pywikibot import Claim

import model.api
import properties.wikidata_properties as wp
from constraints.api import Constraint
from utils import copy_delayed


def has_property(prop: wp.WikidataProperty) -> Constraint:
    """Constraint for 'item has a certain property'"""

    def check(item: model.api.BaseType) -> bool:
        return prop.pid in item.claims

    return Constraint(validator=check, name=f"has_property({prop.name})")


def inherits_property(prop: wp.WikidataProperty) -> Constraint:
    """Constraint for 'item inherits property from parent item'

        The definition of a "parent" depends on the item itself. For example,
        the parent item of an Episode is a Season, and the episode is
        expected to inherit properties such as country of origin (P495)
    """

    def check(item: model.api.Heirarchical) -> bool:
        # If this constraint exists on an item, we expect it to have a parent
        # So not having a parent is equivalent of failing this constraint
        if item.parent is None:
            return False

        item_claims = item.claims
        parent_claims = item.parent.claims

        if prop.pid not in item_claims or prop.pid not in parent_claims:
            return False

        item_targets = [claim.getTarget() for claim in item_claims[prop.pid]]
        parent_targets = [claim.getTarget() for claim in parent_claims[prop.pid]]

        item_titles = {t.title() for t in item_targets}
        parent_titles = {t.title() for t in parent_targets}

        return item_titles == parent_titles

    def fix(item: model.api.Heirarchical) -> Iterable:
        if item.parent is None or prop.pid not in item.parent.claims:
            return []

        return copy_delayed(item.parent.itempage, item.itempage, [prop])

    return Constraint(check, fixer=fix, name=f"inherits_property({prop.name})")


def follows_something() -> Constraint:
    """Alias for has_property(wp.FOLLOWS), but with an autofix"""

    def check(item: model.api.Chainable) -> bool:
        return wp.FOLLOWS.pid in item.claims

    def fix(item: model.api.Chainable) -> Iterable:
        follows = item.previous

        if follows is None:
            print(f"autofix for follows_something({item.qid}) failed")
            return []

        new_claim = Claim(item.repo, wp.FOLLOWS.pid)
        new_claim.setTarget(follows.itempage)
        summary = f"Setting {wp.FOLLOWS.pid} ({wp.FOLLOWS.name})"
        return [(new_claim, summary, item.itempage)]

    return Constraint(check, fixer=fix, name=f"follows_something()")


def is_followed_by_something() -> Constraint:
    """Alias for has_property(wp.FOLLOWED_BY), but with an autofix"""

    def check(item: model.api.Chainable) -> bool:
        return wp.FOLLOWED_BY.pid in item.claims

    def fix(item: model.api.Chainable) -> Iterable:
        is_followed_by = item.next

        if is_followed_by is None:
            print(f"autofix for is_followed_by({item.qid}) failed")
            return []

        new_claim = Claim(item.repo, wp.FOLLOWED_BY.pid)
        new_claim.setTarget(is_followed_by.itempage)
        summary = f"Setting {wp.FOLLOWED_BY.pid} ({wp.FOLLOWED_BY.name})"
        return [(new_claim, summary, item.itempage)]

    return Constraint(check, fixer=fix, name=f"is_followed_by_something()")
