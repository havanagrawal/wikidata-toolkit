"""Check constraints for season/episodes of a TV show"""

from pywikibot import ItemPage, Site
from pywikibot.pagegenerators import WikidataSPARQLPageGenerator

from bots import getbot
from sparql.query_builder import generate_sparql_query
import properties.wikidata_properties as wp

def check_tv_show(tvshow_id=None, child_type="all", autofix=False, accumulate=False, interactive=False, filter=""):
    """Check constraints for season/episodes of this TV show

    Arguments
    ---------
    tvshow_id: str
        the Wiki ID of the television series, in the format Q######.
    child_type: str
        one of "episode", "season", "series", or "all"
    autofix: bool
        whether or not to attempt auto-fixing constraint failures
    accumulate: bool
        whether or not to accumulate all fixes before applying them to WikiData
    interactive: bool
        whether or not to prompt for confirmation before making edits
    filter: str
        a comma-separated list of properties in the format P###.
        Only edits for these properties will be applied.
    """
    if child_type == "episode":
        instance_types = [wp.TELEVISION_SERIES_EPISODE]
    elif child_type == "season":
        instance_types = [wp.TELEVISION_SERIES_SEASON]
    elif child_type == "series":
        instance_types = [wp.TELEVISION_SERIES]
    elif child_type == "all":
        instance_types = [wp.TELEVISION_SERIES, wp.TELEVISION_SERIES_SEASON, wp.TELEVISION_SERIES_EPISODE]

    for instance_of_type in instance_types:
        key_val_pairs = {
            wp.PART_OF_THE_SERIES.pid : tvshow_id,
            wp.INSTANCE_OF.pid : instance_of_type
        }
        query = generate_sparql_query(key_val_pairs)
        gen = WikidataSPARQLPageGenerator(query)
        if instance_of_type == wp.TELEVISION_SERIES:
            gen = [ItemPage(Site().data_repository(), tvshow_id)]
        bot = getbot(gen, autofix=autofix, accumulate=accumulate, always=(not interactive), property_filter=filter)
        bot.run()
