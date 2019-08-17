"""Constraint abstract definition"""

from typing import Callable, Iterable


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

    def fix(self, item) -> Iterable:
        """Return a list of claims that, if implemented, will fix the constraint failure"""
        if self._fixer is None:
            print(f"No autofix available for {self._name}:{item}")
            return []
        return self._fixer(item)

    def __str__(self):
        return self._name

    def __repr__(self):
        return self.__str__()
