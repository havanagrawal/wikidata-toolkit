from typing import List

import click
from pywikibot import Site

from model import Factory, BaseType
from constraints import Constraint

class WikidataItemId(click.ParamType):
    name = "WikidataItemId"

    def convert(self, value, param, ctx):
        if len(value) == 0:
            self.fail(f"Expected non-empty item ID", param, ctx)
        fail_msg = f'Expected item ID of format Q......, got {value}'
        if value[0].upper() != 'Q':
            self.fail(fail_msg, param, ctx)
        if len(value[1:]) == 0:
            self.fail(fail_msg, param, ctx)
        try:
            code = int(value[1:])
        except TypeError:
            self.fail(fail_msg, param, ctx)
        return value

WIKIDATA_ITEM_ID_TYPE = WikidataItemId()

def validate_constraints_for_item(typed_item: BaseType, factory: Factory, autofix=False):
    satisfied = []
    not_satisfied = []
    for constraint in typed_item.constraints:
        is_constraint_satisfied = constraint.validate(typed_item)
        if is_constraint_satisfied:
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


@click.command()
@click.argument('item_ids', type=WIKIDATA_ITEM_ID_TYPE, nargs=-1)
@click.option('--print-failures-only/--print-all', default=True)
@click.option('--autofix', is_flag=True, default=False)
def validate_constraints(item_ids, print_failures_only=True, autofix=False):
    repo = Site('wikidata', 'wikidata').data_repository()
    factory = Factory(repo)

    total_failures = 0
    total = 0

    for item_id in item_ids:
        typed_item = factory.get_typed_item(item_id)
        satisfied, not_satisfied = validate_constraints_for_item(typed_item, factory)
        total_failures += len(not_satisfied)
        total += len(satisfied) + len(not_satisfied)

        print_failures(typed_item, not_satisfied)
        if autofix:
            for failed_constraint in not_satisfied:
                failed_constraint.fix(typed_item)

        if print_failures_only:
            continue
        print_successes(typed_item, satisfied)

    print(f"Found {total_failures}/{total} constraint failures")

if __name__ == "__main__":
    validate_constraints()
