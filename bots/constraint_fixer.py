from typing import List

import pywikibot.logging as botlogging
from pywikibot.bot import WikidataBot

from model import Factory, BaseType
from constraints import Constraint


class ConstraintCheckerBot(WikidataBot):
    """A WikidataBot that checks constraints on items

        The generator must generate instances of ItemPage
    """
    use_from_page = False

    def __init__(self, generator, factory=Factory(), **kwargs):
        super().__init__(generator=generator, **kwargs)
        self.factory = factory

    def print_failures(self, typed_item: BaseType, failed_constraints: List[Constraint]):
        for constraint in failed_constraints:
            botlogging.error(f"{constraint} failed for {typed_item}")

    def print_successes(self, typed_item: BaseType, passed_constraints: List[Constraint]):
        for constraint in passed_constraints:
            botlogging.output(f"{constraint} passed for {typed_item}")

    #override
    def treat_page_and_item(self, unused_page, item):
        """Print out constraint failures

            unused_page is always None since use_from_page is False.
            See https://doc.wikimedia.org/pywikibot/master/api_ref/pywikibot.html#pywikibot.WikidataBot
        """
        item.get()
        typed_item = self.factory.get_typed_item(item.title())
        botlogging.output(f"Checking constraints for {typed_item}")
        satisfied = []
        not_satisfied = []
        for constraint in typed_item.constraints:
            if constraint.validate(typed_item):
                satisfied.append(constraint)
            else:
                not_satisfied.append(constraint)

        self.print_failures(typed_item, not_satisfied)
        self.print_successes(typed_item, satisfied)

        total = len(typed_item.constraints)
        failures = len(not_satisfied)

        botlogging.output(f"Found {failures}/{total} constraint failures")

        return satisfied, not_satisfied


class ConstraintFixerBot(ConstraintCheckerBot):
    #override
    def treat_page_and_item(self, unused_page, item):
        """Fix items that have constraint failures

            unused_page is always None since use_from_page is False.
            See https://doc.wikimedia.org/pywikibot/master/api_ref/pywikibot.html#pywikibot.WikidataBot
        """
        _, not_satisfied = super().treat_page_and_item(unused_page, item)
        typed_item = self.factory.get_typed_item(item.title())

        fixes = [fix for constraint in not_satisfied for fix in constraint.fix(typed_item)]
        fixed = 0
        for claim, summary, itempage in fixes:
            success = self.user_add_claim(itempage, claim, summary=summary)
            fixed += success
        total = len(not_satisfied)
        botlogging.output(f"Fixed {fixed}/{total} constraint failures")

class AccumulatingConstraintFixerBot(ConstraintCheckerBot):
    """Accumulates all fixes, and then fixes them only when fixall is called"""
    def __init__(self, generator, factory=Factory(), **kwargs):
        super().__init__(generator, factory, **kwargs)
        self.fixes = []

    #override
    def treat_page_and_item(self, unused_page, item):
        """Fix items that have constraint failures

            unused_page is always None since use_from_page is False.
            See https://doc.wikimedia.org/pywikibot/master/api_ref/pywikibot.html#pywikibot.WikidataBot
        """
        _, not_satisfied = super().treat_page_and_item(unused_page, item)
        typed_item = self.factory.get_typed_item(item.title())

        fixes = [fix for constraint in not_satisfied for fix in constraint.fix(typed_item)]
        self.fixes.extend(fixes)

    def fixall(self):
        for _, summary, _ in self.fixes:
            print(summary)

        fixed = 0
        for claim, summary, itempage in self.fixes:
            success = self.user_add_claim(itempage, claim, summary=summary)
            fixed += success
        total = len(self.fixes)
        botlogging.output(f"Fixed {fixed}/{total} constraint failures")

    #override
    def run(self):
        super().run()
        self.fixall()
