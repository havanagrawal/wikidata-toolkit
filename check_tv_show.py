"""Check constraints for season/episodes of a TV show"""
import click
from pywikibot import Site
from pywikibot.pagegenerators import WikidataSPARQLPageGenerator

from bots import getbot
from sparql.query_builder import generate_sparql_query
import properties.wikidata_properties as wp
from click_utils import WIKIDATA_ITEM_ID_TYPE

@click.command()
@click.argument("tvshow_id", type=WIKIDATA_ITEM_ID_TYPE)
@click.option("--child_type", type=click.Choice(["episode", "season", "all"]))
@click.option("--autofix", is_flag=True, default=False, help="Fix constraint violations")
@click.option("--accumulate", is_flag=True, default=False, help="Accumulate all fixes before applying them")
@click.option("--filter", default="", help="Comma separated property names/tags to filter")
def check_tv_show(tvshow_id, child_type="episode", autofix=False, accumulate=False, filter=""):
    """Check constraints for season/episodes of this TV show

    TVSHOW_ID is the ID of the television series, in the format Q######. 
    """
    if child_type == "episode":
        instance_types = [wp.TELEVISION_SERIES_EPISODE]
    elif child_type == "season":
        instance_types = [wp.TELEVISION_SERIES_SEASON]
    elif child_type == "all":
        instance_types = [wp.TELEVISION_SERIES_SEASON, wp.TELEVISION_SERIES_EPISODE]

    for instance_of_type in instance_types:
        key_val_pairs = {
            wp.PART_OF_THE_SERIES.pid : tvshow_id,
            wp.INSTANCE_OF.pid : instance_of_type
        }
        query = generate_sparql_query(key_val_pairs)
        gen = WikidataSPARQLPageGenerator(query)
        bot = getbot(gen, autofix=autofix, accumulate=accumulate, always=False, filter=filter)
        bot.run()


if __name__ == "__main__":
    check_tv_show()
