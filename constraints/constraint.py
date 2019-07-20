from typing import Callable
from model.wikidata_properties import WikidataProperty
from utils import RepoUtils

class Constraint():
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
    def inner(item):
        return property.pid in item.itempage.claims

    return Constraint(validator=inner, name=f"has_property({property.name})")

def inherits_property(property: WikidataProperty):
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
