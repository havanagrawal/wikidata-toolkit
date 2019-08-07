"""Module for various Wikidata bots"""

from .constraint_fixer import ConstraintCheckerBot
from .constraint_fixer import ConstraintFixerBot
from .constraint_fixer import AccumulatingConstraintFixerBot

def getbot(generator, autofix, accumulate, always=False, filter=""):
    if autofix:
        if accumulate:
            return AccumulatingConstraintFixerBot(generator, always=always, filter=filter)
        return ConstraintFixerBot(generator, always=always, filter=filter)
    return ConstraintCheckerBot(generator, always=always)
