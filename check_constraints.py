from typing import List

import click
from pywikibot import Site

from model import Factory, BaseType
from constraints import Constraint
from properties.wikidata_item import WikidataItemId

def validate_constraints_for_item(typed_item: BaseType, factory: Factory, autofix=False):
    satisfied = []
    not_satisfied = []
    for constraint in typed_item.constraints:
        if constraint.validate(typed_item):
            satisfied.append(constraint)
        else:
            not_satisfied.append(constraint)

    return satisfied, not_satisfied

def print_failures(typed_item: BaseType, failed_constraints: List[Constraint]):
    for constraint in failed_constraints:
        print(f"{constraint} failed for {typed_item}")

def print_successes(typed_item: BaseType, passed_constraints: List[Constraint]):
    for constraint in passed_constraints:
        print(f"{constraint} passed for {typed_item}")

def validate_constraints(item_ids, print_failures_only=True, autofix=False):
    repo = Site().data_repository()
    factory = Factory(repo)

    total_failures = 0
    total = 0
    total_fixed = 0

    for item_id in item_ids:
        typed_item = factory.get_typed_item(item_id)
        satisfied, not_satisfied = validate_constraints_for_item(typed_item, factory)
        total_failures += len(not_satisfied)
        total += len(satisfied) + len(not_satisfied)

        print_failures(typed_item, not_satisfied)
        if autofix:
            fixed = sum(
                failed_constraint.fix(typed_item)
                for failed_constraint in not_satisfied
            )
            total_fixed += fixed

        if print_failures_only:
            continue
        print_successes(typed_item, satisfied)

    print(f"Found {total_failures}/{total} constraint failures")
    print(f"Fixed {total_fixed}/{total_failures} constraint failures")

class WikidataItemIdType(click.ParamType):
    def convert(self, value, param, ctx):
        item_id = None
        try:
            return str(WikidataItemId(value))
        except ValueError as e:
            self.fail(str(e), param, ctx)

WIKIDATA_ITEM_ID_TYPE = WikidataItemIdType()

@click.command()
@click.argument('item_ids', type=WIKIDATA_ITEM_ID_TYPE, nargs=-1)
@click.option('--print-failures-only/--print-all', default=True)
@click.option('--autofix', is_flag=True, default=False)
def validate_constraints_click(item_ids, print_failures_only=True, autofix=False):
    validate_constraints(item_ids, print_failures_only, autofix)

if __name__ == "__main__":
    validate_constraints_click()
