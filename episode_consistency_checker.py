import click

from pywikibot import Site
from pywikibot.pagegenerators import WikidataSPARQLPageGenerator

from sparql.query_builder import generate_sparql_query
import properties.wikidata_properties as wp
from check_constraints import validate_constraints

@click.command()
@click.argument("tvshow_id")
@click.option("--autofix", is_flag=True, default=False)
def bulk_check(tvshow_id, autofix=False):
    key_val_pairs = {
        wp.PART_OF_THE_SERIES.pid : tvshow_id,
        wp.INSTANCE_OF.pid : wp.TELEVISION_SERIES_EPISODE
    }
    query = generate_sparql_query(key_val_pairs)
    print(query)
    gen = WikidataSPARQLPageGenerator(query)
    episode_item_ids = (x.title() for x in gen)
    validate_constraints(episode_item_ids, autofix=autofix)

if __name__ == "__main__":
    bulk_check()
