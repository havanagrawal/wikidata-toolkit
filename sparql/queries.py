from pywikibot import Site
from pywikibot.data.sparql import SparqlQuery

from properties import wikidata_properties as wp

def episodes(season_id):
    """Find episodes for a given season (specified by QID)
    
        Returns an iterable of (season ordinal, episode QID, episode title)
    """
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

def episodes_with_titles_and_missing_labels():
    """Find English show episodes with missing labels, but with a title
    
        Returns an iterable of (episode QID, title, series label)
    """
    query = f"""
    SELECT ?episode ?episodeLabel ?seriesLabel ?title WHERE {{
        ?episode wdt:{wp.INSTANCE_OF.pid} wd:{wp.TELEVISION_SERIES_EPISODE};
            wdt:{wp.ORIGNAL_LANGUAGE_OF_FILM_OR_TV_SHOW.pid} wd:Q1860.
        OPTIONAL {{ ?episode wdt:{wp.TITLE.pid} ?title. }}
        OPTIONAL {{ ?episode wdt:{wp.PART_OF_THE_SERIES.pid} ?series. }}
        FILTER(BOUND(?title))
        FILTER(REGEX(?episodeLabel, "Q\\\\d{{1,9}}"))
        SERVICE wikibase:label {{
            bd:serviceParam wikibase:language "en".
            ?episode rdfs:label ?episodeLabel.
            ?series rdfs:label ?seriesLabel.
        }}
    }}
    ORDER BY (?seriesLabel) (?title)
    """
    print(query)
    results = SparqlQuery(repo=Site().data_repository()).select(query)
    for result in results:
        episode_id = result['episode'].split("/")[-1]
        title = result['title']
        series_label = result['seriesLabel']
        yield episode_id, title, series_label