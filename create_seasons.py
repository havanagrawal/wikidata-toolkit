import click
import csv

from pywikibot import Claim, ItemPage, Site
from pywikibot.data.api import Request

import properties.wikidata_properties as wp
from utils import RepoUtils

from click_utils import validate_item_id

def create_season_quickstatements(series_id, label, descr, ordinal):
    print("CREATE")
    print(f'LAST|Len|"{label}"')
    print(f'LAST|Den|"{descr}"')
    print(f"LAST|{wp.INSTANCE_OF.pid}|{wp.TELEVISION_SERIES_SEASON}")
    print(f'LAST|{wp.PART_OF_THE_SERIES.pid}|{series_id}|{wp.SERIES_ORDINAL.pid}|"{ordinal}"')

def create_seasons_quickstatements(series_id, series_title, number_of_seasons):
    for i in range(1, number_of_seasons + 1):
        label = f"{series_title}, season {i}"
        descr = f"season {i} of {series_title}"
        create_season_quickstatements(series_id, label, descr, i)

@click.command()
@click.argument("series_id", callback=validate_item_id)
@click.argument("number_of_seasons", type=int)
@click.option("--quickstatements", is_flag=True, default=False)
def create_seasons(series_id, number_of_seasons, quickstatements=False):
    series_title = ItemPage(Site().data_repository(), series_id)
    series_title.get(force=True)
    if quickstatements:
        create_seasons_quickstatements(series_id, series_title.labels['en'], number_of_seasons)
    else:
        raise ValueError("Non-quickstatements creation not permitted. Please use the --quickstatements option")


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    create_seasons()