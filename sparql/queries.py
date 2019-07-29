from pywikibot import Site
from pywikibot.data.sparql import SparqlQuery

from properties import wikidata_properties as wp

def episodes(season_id):
    query = f"""
    SELECT ?seasonOrdinal ?episode ?episodeTitle WHERE {{
      ?episode wdt:{wp.INSTANCE_OF.pid} wd:{wp.TELEVISION_SERIES_EPISODE};
               wdt:{wp.SEASON.pid} wd:{season_id};
               wdt:{wp.TITLE.pid} ?episodeTitle;
               (p:{wp.SEASON.pid}/pq:{wp.SERIES_ORDINAL.pid}) ?seasonOrdinal .
    }}
    ORDER BY (?seasonOrdinal)
    """
    results = SparqlQuery(repo=Site().data_repository()).select(query)
    for result in results:
        ordinal = int(result['seasonOrdinal'])
        episode_id = result['episode'].split("/")[-1]
        title = result['episodeTitle']
        yield ordinal, episode_id, title
