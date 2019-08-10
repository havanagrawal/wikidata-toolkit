"""Module for various Wikidata bots"""
from typing import Iterable

from pywikibot import ItemPage
from pywikibot.bot import WikidataBot

from .constraint_fixer import ConstraintCheckerBot
from .constraint_fixer import ConstraintFixerBot
from .constraint_fixer import AccumulatingConstraintFixerBot

def getbot(
        generator: Iterable[ItemPage],
        autofix: bool,
        accumulate: bool,
        always: bool = False,
        filter: str = None
    ) -> WikidataBot:
    """Bot factory for returning an appropriate implementation of WikidataBot

        Arguments
        ---------
        generator: generator
            A generator/iterable of ItemPages

        autofix: bool
            If True, fix failing constraints that have a fix available

        accumulate: bool
            If True, accumulate (and log) all fixes before implementing them

        always: bool
            If True, don't prompt for confirmation on each fix, implement all

        filter: str
            A comma-separated list of properties. Only these properties will be fixed.
            Eg: "P1476"
            Eg: "title,country of origin"
            Eg: "P155,P156,title"
    """
    if autofix:
        if accumulate:
            return AccumulatingConstraintFixerBot(generator, always=always, filter=filter)
        return ConstraintFixerBot(generator, always=always, filter=filter)
    return ConstraintCheckerBot(generator, always=always)
