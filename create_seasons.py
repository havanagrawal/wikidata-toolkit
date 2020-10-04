import click
from pywikibot import Site

import commands
import properties.wikidata_properties as wp
from click_utils import validate_item_id
from utils import RepoUtils


@click.command()
@click.argument("series_id", callback=validate_item_id)
@click.argument("number_of_seasons", type=int)
@click.option("--quickstatements", help="Print out QuickStatements for creating the items, instead of creating the items directly on Wikidata.", is_flag=True, default=False)
@click.option("--dry", help="Enable dry run mode. Does not create any items on Wikidata.", is_flag=True, default=False)
def create_seasons(series_id, number_of_seasons, quickstatements=False, dry=False):
    Site().login()
    commands.create_seasons(series_id, number_of_seasons, quickstatements, dry)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    create_seasons()
