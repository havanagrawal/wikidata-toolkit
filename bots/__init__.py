"""Module for various Wikidata bots"""

from .constraint_fixer import ConstraintCheckerBot
from .constraint_fixer import ConstraintFixerBot
from .constraint_fixer import AccumulatingConstraintFixerBot

def getbot(generator, autofix, accumulate, always):
    if autofix:
        if accumulate:
            return AccumulatingConstraintFixerBot(generator, always=always)
        return ConstraintFixerBot(generator, always=always)
    return ConstraintCheckerBot(generator, always=always)
