"""Constraint abstract definition"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Iterable

from pywikibot import Claim, ItemPage


class Constraint:
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

    def __init__(
        self,
        validator: Callable[..., bool],
        fixer: Callable[..., Iterable] = None,
        name=None,
    ):
        self._validator = validator
        self._name = name
        self._fixer = fixer

    def validate(self, item) -> bool:
        """Return True if the item satisfies the constraint, else False"""
        return self._validator(item)

    def fix(self, item) -> Iterable[Fix]:
        """Return a list of claims that, if implemented, will fix the constraint failure"""
        if self._fixer is None:
            print(f"No autofix available for {self._name}:{item}")
            return []
        return self._fixer(item)

    def __str__(self):
        return self._name

    def __repr__(self):
        return self.__str__()


class Fix(ABC):
    """A Fix represents a command that can be executed to fix a constraint failure

        It has 3 subclasses: ClaimFix, LabelFix and DescriptionFix.

        In order to apply the fix, the user must call "apply" on an instance of this class.
    """
    @abstractmethod
    def apply(self, *args, **kwargs):
        """Apply this fix, i.e. update the item on Wikidata"""
        pass


class ClaimFix(Fix):
    """A Fix to update the item by adding a Claim"""
    def __init__(self, claim: Claim, summary: str, itempage: ItemPage):
        self.claim = claim
        self.summary = summary
        self.itempage = itempage

    def apply(self, func, *args, **kwargs):
        return func(item=self.itempage, claim=self.claim, summary=self.summary)


class LabelFix(Fix):
    """A Fix to update the item by adding a label"""
    def __init__(self, label: str, lang: str, itempage: ItemPage):
        self.label = label
        self.lang = lang
        self.itempage = itempage
        self.summary = f"Adding {lang} label: '{label}' to {itempage.title()}"

    def apply(self, *args, **kwargs):
        try:
            change = input(f"Add label='{self.label}' for {self.itempage} (y/N)? ")
            if change.lower() == "y":
                self.itempage.editLabels({self.lang: self.label})
        except:
            return False
        return True


class DescriptionFix(Fix):
    """A Fix to update the item by adding a description"""
    def __init__(self, description: str, lang: str, itempage: ItemPage):
        self.description = description
        self.lang = lang
        self.itempage = itempage
        self.summary = f"Adding {lang} description: '{description}' to {itempage.title()}"

    def apply(self, *args, **kwargs):
        try:
            change = input(f"Add description='{self.description}' for {self.itempage} (y/N)? ")
            if change.lower() == "y":
                self.itempage.editDescriptions({self.lang: self.description})
        except:
            return False
        return True
