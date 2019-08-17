"""Base interfaces and mixins for model classes"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Iterable

from pywikibot import ItemPage, Site


class BaseType(ABC):
    """The base class for wrapper classes

        This is mostly instance-type agnostic. It should be extended
        by more specific implementations that encapsulate a concept.
    """

    def __init__(self, itempage: ItemPage, repo=None):
        self._itempage = itempage
        self._itempage.get()
        self._repo = Site().data_repository() if repo is None else repo

    @property
    def itempage(self) -> ItemPage:
        """The underlying ItemPage for this entity"""
        return self._itempage

    @property
    def label(self) -> Optional[str]:
        """The English (en) label of this entity"""
        return self._itempage.labels.get("en", None)

    @property
    def qid(self) -> str:
        """The QID of this entity, of the form Q####"""
        return self._itempage.title()

    @property
    def repo(self):
        """The underlying repo from where data for this item is fetched"""
        return self._repo

    @property
    def claims(self):
        """The claims of this item page

            This lifts the claims property so we don't have to
            violate Demeter's Law all the time
        """
        return self._itempage.claims

    def first_claim(self, key: str, default=None):
        """The first claim for this property key, or default"""
        if key not in self._itempage.claims:
            return default
        if not self._itempage.claims[key]:
            return default
        return self._itempage.claims[key][0].getTarget()

    @property
    @abstractmethod
    def constraints(self):
        """An iterable of Constraints that apply to this entity"""
        ...

    def refresh(self) -> None:
        """Fetch the latest data from Wikidata for this item"""
        self._itempage.get()

    def __str__(self):
        return f"{self.__class__.__name__}({self.qid} ({self.label}))"

    def __repr__(self):
        return str(self)

    @classmethod
    def from_id(cls, item_id: str, repo=None):
        """Create an instance of the class from the item ID (QID)

            Note: This does not check if the QID is the same type
            as the wrapper class. It is recommended that the user:
              1. uses Factory to instantiate this class, OR
              2. ensures that the item_id is in fact the same type as the class
        """
        repo = Site().data_repository() if repo is None else repo
        return cls(ItemPage(repo, item_id), repo)


class Heirarchical(BaseType):
    """A mixin to model an item that can appear in a tree-like structure

        Example:
          Series
           |- Season 1
               |- Episode 1
               |- Episode 2
           |- Season 2
               |- Episode 1
               |- Episode 2
               ...

        Expose two properties: parent and child
    """

    @property
    def parent(self) -> Optional[Heirarchical]:
        """The parent of the tree node that this item represents

            Example: A Season should have a Series as its parent
        """
        return None

    @property
    def children(self) -> Iterable[Heirarchical]:
        """The children of the tree node that this item represents

            Example: A Season should have an iterable of Episode as its children
        """
        return []


class Chainable(BaseType):
    """A mixin to model an item that can appear in a list-like structure

        Example:
            Season 1 <--> Season 2 <--> Season 3
    """

    @property
    def next(self) -> Optional[Chainable]:
        """The next item in this chain of items

            Example: Season 3 should have Season 4 as its next
        """
        return None

    @property
    def previous(self) -> Optional[Chainable]:
        """The previous item in this chain of items

            Example: Season 3 should have Season 2 as its previous
        """
        return None
