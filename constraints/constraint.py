"""Constraint abstract definition and implementations"""

from typing import Callable
from properties.wikidata_properties import WikidataProperty
from utils import RepoUtils

class Constraint():
    """A constraint on data consistency/quality

        A constraint has two parts: a validator and a fixer
        The validator verifies if the constraint is satisfied or not,
        and the fixer can attempt to make the data satisfy the constraint.

        In principle, this is very similar to how Wikidata validates constraints,
        but allows for a simpler and more extensible programmatic model.
    """
    def __init__(self, validator:Callable[..., bool], fixer:Callable[..., None]=None, name=None):
        self._validator = validator
        self._name = name
        self._fixer = fixer

    def validate(self, item):
        return self._validator(item)

    def fix(self, item):
        if self._fixer is None:
            print(f"No autofix available for {self._name}:{item}")
            return
        self._fixer(item)

    def __str__(self):
        return self._name

    def __repr__(self):
        return self.__str__()

def has_property(property: WikidataProperty):
    """Constraint for 'item has a certain property'"""
    def inner(item):
        return property.pid in item.itempage.claims

    return Constraint(validator=inner, name=f"has_property({property.name})")

def inherits_property(property: WikidataProperty):
    """Constraint for 'item inherits property from parent item'

        The definition of a "parent" depends on the item itself. For example,
        the parent item of an Episode is a Season, and the episode is
        expected to inherit properties such as country of origin (P495)
    """
    @item_has_parent
    def inner_check(item):
        item_claims = item.itempage.claims
        parent_claims = item.parent.itempage.claims

        return (
            property.pid in item_claims and
            property.pid in parent_claims and
            item_claims[property.pid] == parent_claims[property.pid]
        )

    @item_has_parent
    def inner_fix(item):
        RepoUtils(item.repo).copy(item.parent.itempage, item.itempage, [property])

    return Constraint(
        inner_check,
        name=f"inherits_property({property.name})",
        fixer=inner_fix
    )

def item_has_parent(func):
    def wrapper(*args, **kwargs):
        item = args[0]
        item_has_parent = item.parent is not None
        if not item_has_parent:
            print(f"{item} has no concept of parent")
            return noop
        else:
            return func(*args, **kwargs)

    return wrapper
