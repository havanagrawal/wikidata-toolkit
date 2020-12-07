"""Basic checking and fixing bot implementations

    These bots need to be provided with a generator of ItemPages in order to run

    Current implementations provided are:
        1. ConstraintCheckerBot
           Performs checks on items, but does not fix them

        2. ConstraintFixerBot
           Performs checks on items, and fixes them if there are available fixes

        3. AccumulatingConstraintFixerBot
           Performs checks on items, and accumulates the fixes into a list.
           Logs out the fixes, and then implements them once all items have been checked.
"""

import pywikibot.logging as botlogging
from pywikibot.bot import WikidataBot

from model import BaseType, Factory


class ConstraintCheckerBot(WikidataBot):
    """A WikidataBot that checks constraints on items

        The generator must generate instances of ItemPage
    """

    use_from_page = False

    def __init__(self, generator, factory=Factory(), verbose=False, **kwargs):
        super().__init__(generator=generator, **kwargs)
        self.factory = factory
        self.verbose = verbose

    def print_failures(self, typed_item: BaseType, failed_constraints):
        """Print failed constraints"""
        for constraint in failed_constraints:
            botlogging.output(f"{constraint} failed for {typed_item}", toStdout=True)

    def print_successes(self, typed_item: BaseType, passed_constraints):
        """Print passed constraints"""
        for constraint in passed_constraints:
            botlogging.output(f"{constraint} passed for {typed_item}", toStdout=True)

    # override
    def treat_page_and_item(self, unused_page, item):
        """Print out constraint failures

            unused_page is always None since use_from_page is False.
            See https://doc.wikimedia.org/pywikibot/master/api_ref/pywikibot.html#pywikibot.WikidataBot
        """
        item.get(force=True)
        typed_item = self.factory.get_typed_item(item.title())
        botlogging.output(f"Checking constraints for {typed_item}", toStdout=True)
        satisfied = []
        not_satisfied = []
        for constraint in typed_item.constraints:
            if constraint.validate(typed_item):
                satisfied.append(constraint)
            else:
                not_satisfied.append(constraint)

        if self.verbose:
            self.print_failures(typed_item, not_satisfied)
            self.print_successes(typed_item, satisfied)

        total = len(typed_item.constraints)
        failures = len(not_satisfied)

        botlogging.output(
            f"Found {failures}/{total} constraint failures", toStdout=True
        )

        return satisfied, not_satisfied


class ConstraintFixerBot(ConstraintCheckerBot):
    def __init__(self, generator, factory=Factory(), property_filter=None, **kwargs):
        super().__init__(generator=generator, factory=factory, **kwargs)
        if property_filter is None:
            property_filter = ""
        self._filters = set(property_filter.split(","))

    # override
    def treat_page_and_item(self, unused_page, item):
        """Fix items that have constraint failures

            unused_page is always None since use_from_page is False.
            See https://doc.wikimedia.org/pywikibot/master/api_ref/pywikibot.html#pywikibot.WikidataBot
        """
        item.get(force=True)
        _, not_satisfied = super().treat_page_and_item(unused_page, item)
        typed_item = self.factory.get_typed_item(item.title())

        fixes = [
            fix for constraint in not_satisfied for fix in constraint.fix(typed_item)
        ]
        fixed = 0
        for fix in fixes:
            skip_fix = not should_fix(fix, self._filters)
            if self._filters and skip_fix:
                continue
            success = fix.apply(self.user_add_claim)
            fixed += success
        total = len(not_satisfied)
        botlogging.output(f"Fixed {fixed}/{total} constraint failures", toStdout=True)


class AccumulatingConstraintFixerBot(ConstraintCheckerBot):
    """Accumulates all fixes, and then fixes them only when fixall is called"""

    def __init__(
        self, generator, factory=Factory(), property_filter=None, sort=True, **kwargs
    ):
        super().__init__(generator, factory, **kwargs)
        self.fixes = []
        self.sort = sort
        if property_filter is None:
            property_filter = ""
        self._filters = set(property_filter.split(","))

    # override
    def treat_page_and_item(self, unused_page, item):
        """Fix items that have constraint failures

            unused_page is always None since use_from_page is False.
            See https://doc.wikimedia.org/pywikibot/master/api_ref/pywikibot.html#pywikibot.WikidataBot
        """
        item.get(force=True)
        _, not_satisfied = super().treat_page_and_item(unused_page, item)
        typed_item = self.factory.get_typed_item(item.title())

        fixes = [
            fix for constraint in not_satisfied for fix in constraint.fix(typed_item)
        ]
        self.fixes.extend(fixes)

    def fixall(self):
        if self.sort:
            self.fixes = list(sorted(self.fixes, key=lambda f: f.summary))

        if self._filters:
            self.fixes = [
                fix for fix in self.fixes if should_fix(fix, self._filters)
            ]

        for fix in self.fixes:
            print(fix.summary)

        fixed = 0
        for fix in self.fixes:
            success = fix.apply(self.user_add_claim)
            fixed += int(success)
        total = len(self.fixes)
        botlogging.output(f"Fixed {fixed}/{total} constraint failures", toStdout=True)

    # override
    def run(self):
        super().run()
        self.fixall()


def should_fix(fix, filters):
    return any(filter in fix.summary for filter in filters)
