"""Constraint abstract definition and implementations"""

from typing import Callable
from pywikibot import Claim
from pywikibot.pagegenerators import WikidataSPARQLPageGenerator

import properties.wikidata_properties as wp
from utils import RepoUtils
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
    def __init__(self, validator: Callable[..., bool], fixer: Callable[..., None]=None, name=None):
        self._validator = validator
        self._name = name
        self._fixer = fixer

    def validate(self, item):
        return self._validator(item)

    def fix(self, item):
        if self._fixer is None:
            print(f"No autofix available for {self._name}:{item}")
            return False
        return self._fixer(item)

    def __str__(self):
        return self._name

    def __repr__(self):
        return self.__str__()

def has_property(prop: wp.WikidataProperty):
    """Constraint for 'item has a certain property'"""
    def inner(item):
        return prop.pid in item.claims

    return Constraint(validator=inner, name=f"has_property({prop.name})")

def inherits_property(prop: wp.WikidataProperty):
    """Constraint for 'item inherits property from parent item'

        The definition of a "parent" depends on the item itself. For example,
        the parent item of an Episode is a Season, and the episode is
        expected to inherit properties such as country of origin (P495)
    """
    @item_has_parent
    def inner_check(item):
        item_claims = item.claims
        parent_claims = item.parent.claims

        return (
            prop.pid in item_claims and
            prop.pid in parent_claims and
            item_claims[prop.pid] == parent_claims[prop.pid]
        )

    @item_has_parent
    def inner_fix(item):
        parent_claims = item.parent.claims

        if prop.pid not in parent_claims:
            return False

        RepoUtils().copy(item.parent.itempage, item.itempage, [prop])
        return True

    return Constraint(
        inner_check,
        name=f"inherits_property({prop.name})",
        fixer=inner_fix
    )

def item_has_parent(func):
    def wrapper(*args, **kwargs):
        item = args[0]
        has_parent = item.parent is not None
        if not has_parent:
            print(f"{item} has no concept of parent")
            return False

        return func(*args, **kwargs)

    return wrapper

def follows_something():
    """Alias for has_property(wp.FOLLOWS), but with an autofix"""
    def inner_check(item):
        return wp.FOLLOWS.pid in item.claims

    def inner_fix(item):
        # Find the item that has the FOLLOWED_BY field set to this item
        query = generate_sparql_query({wp.FOLLOWED_BY.pid: item.itempage.title()})
        gen = WikidataSPARQLPageGenerator(query)
        is_followed_by = next(gen, None)

        if is_followed_by is None:
            print(f"autofix for follows_something({item.title}) failed")
            return False

        new_claim = Claim(item.repo, wp.FOLLOWS.pid)
        new_claim.setTarget(is_followed_by)
        item.itempage.addClaim(new_claim, summary=f'Setting {wp.FOLLOWS.pid} ({wp.FOLLOWS.name})')
        return True

    return Constraint(
        inner_check,
        name=f"follows_something()",
        fixer=inner_fix
    )

def is_followed_by_something():
    """Alias for has_property(wp.FOLLOWED_BY), but with an autofix"""
    def inner_check(item):
        return wp.FOLLOWED_BY.pid in item.claims

    def inner_fix(item):
        is_followed_by = item.next

        if is_followed_by is None:
            print(f"autofix for is_followed_by({item.title}) failed")
            return False

        new_claim = Claim(item.repo, wp.FOLLOWED_BY.pid)
        new_claim.setTarget(is_followed_by.itempage)
        item.itempage.addClaim(new_claim, bot=True, summary=f'Setting {wp.FOLLOWED_BY.pid} ({wp.FOLLOWED_BY.name})')
        return True

    return Constraint(
        inner_check,
        name=f"is_followed_by_something()",
        fixer=inner_fix
    )
