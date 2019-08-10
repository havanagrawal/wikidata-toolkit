import pywikibot.logging as botlogging
from pywikibot.bot import WikidataBot

from model import Factory, BaseType


class ConstraintCheckerBot(WikidataBot):
    """A WikidataBot that checks constraints on items

        The generator must generate instances of ItemPage
    """
    use_from_page = False

    def __init__(self, generator, factory=Factory(), **kwargs):
        super().__init__(generator=generator, **kwargs)
        self.factory = factory

    def print_failures(self, typed_item: BaseType, failed_constraints):
        for constraint in failed_constraints:
            botlogging.error(f"{constraint} failed for {typed_item}")

    def print_successes(self, typed_item: BaseType, passed_constraints):
        for constraint in passed_constraints:
            botlogging.output(f"{constraint} passed for {typed_item}", toStdout=True)

    #override
    def treat_page_and_item(self, unused_page, item):
        """Print out constraint failures

            unused_page is always None since use_from_page is False.
            See https://doc.wikimedia.org/pywikibot/master/api_ref/pywikibot.html#pywikibot.WikidataBot
        """
        item.get()
        typed_item = self.factory.get_typed_item(item.title())
        botlogging.output(f"Checking constraints for {typed_item}", toStdout=True)
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

        botlogging.output(f"Found {failures}/{total} constraint failures", toStdout=True)

        return satisfied, not_satisfied


class ConstraintFixerBot(ConstraintCheckerBot):
    def __init__(self, generator, factory=Factory(), filter=None, **kwargs):
        super().__init__(generator=generator, factory=factory, **kwargs)
        if filter is None:
            filter = ""
        self._filters = set(filter.split(","))

    #override
    def treat_page_and_item(self, unused_page, item):
        """Fix items that have constraint failures

            unused_page is always None since use_from_page is False.
            See https://doc.wikimedia.org/pywikibot/master/api_ref/pywikibot.html#pywikibot.WikidataBot
        """
        item.get()
        _, not_satisfied = super().treat_page_and_item(unused_page, item)
        typed_item = self.factory.get_typed_item(item.title())

        fixes = [fix for constraint in not_satisfied for fix in constraint.fix(typed_item)]
        fixed = 0
        for claim, summary, itempage in fixes:
            if not should_fix(summary, self._filters):
                continue
            success = self.user_add_claim(itempage, claim, summary=summary)
            fixed += success
        total = len(not_satisfied)
        botlogging.output(f"Fixed {fixed}/{total} constraint failures")

class AccumulatingConstraintFixerBot(ConstraintCheckerBot):
    """Accumulates all fixes, and then fixes them only when fixall is called"""
    def __init__(self, generator, factory=Factory(), filter=None, sort=True, **kwargs):
        super().__init__(generator, factory, **kwargs)
        self.fixes = []
        self.sort = sort
        if filter is None:
            filter = ""
        self._filters = set(filter.split(","))

    #override
    def treat_page_and_item(self, unused_page, item):
        """Fix items that have constraint failures

            unused_page is always None since use_from_page is False.
            See https://doc.wikimedia.org/pywikibot/master/api_ref/pywikibot.html#pywikibot.WikidataBot
        """
        item.get()
        _, not_satisfied = super().treat_page_and_item(unused_page, item)
        typed_item = self.factory.get_typed_item(item.title())

        fixes = [fix for constraint in not_satisfied for fix in constraint.fix(typed_item)]
        self.fixes.extend(fixes)

    def fixall(self):
        if self.sort:
            self.fixes = list(sorted(self.fixes, key=lambda f: f[1]))

        if self._filters:
            self.fixes = [fix for fix in self.fixes if should_fix(fix[1], self._filters)]

        for _, summary, _ in self.fixes:
            print(summary)

        fixed = 0
        for claim, summary, itempage in self.fixes:
            success = self.user_add_claim(itempage, claim, summary=summary)
            fixed += int(success)
        total = len(self.fixes)
        botlogging.output(f"Fixed {fixed}/{total} constraint failures", toStdout=True)

    #override
    def run(self):
        super().run()
        self.fixall()

def should_fix(summary, filters):
    return any(filter in summary for filter in filters)