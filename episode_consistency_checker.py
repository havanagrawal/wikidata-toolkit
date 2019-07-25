import click

from pywikibot import Site
from pywikibot.pagegenerators import WikidataSPARQLPageGenerator

from sparql.query_builder import generate_sparql_query
import properties.wikidata_properties as wp
from check_constraints import validate_constraints
from click_utils import WIKIDATA_ITEM_ID_TYPE

@click.command()
@click.argument("tvshow_id", type=WIKIDATA_ITEM_ID_TYPE)
@click.option("--child_type", type=click.Choice(["episode", "season"]))
@click.option("--autofix", is_flag=True, default=False)
def bulk_check(tvshow_id, child_type="episode", autofix=False):
    if child_type == "episode":
        instance_of_type = wp.TELEVISION_SERIES_EPISODE
    elif child_type == "season":
        instance_of_type = wp.TELEVISION_SERIES_SEASON

    key_val_pairs = {
        wp.PART_OF_THE_SERIES.pid : tvshow_id,
        wp.INSTANCE_OF.pid : instance_of_type
    }
    query = generate_sparql_query(key_val_pairs)
    gen = WikidataSPARQLPageGenerator(query)
    episode_item_ids = (x.title() for x in gen)
    validate_constraints(episode_item_ids, autofix=autofix)

if __name__ == "__main__":
    bulk_check()
