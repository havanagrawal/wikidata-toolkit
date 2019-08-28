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
        ordinal = int(result["seasonOrdinal"])
        episode_id = result["episode"].split("/")[-1]
        title = result["episodeTitle"]
        yield ordinal, episode_id, title


def episodes_with_titles_and_missing_labels():
    """Find English show episodes with missing labels, but with a title

        Missing labels are identified by checking if the label is equal to
        the QID

        Returns an iterable of (episode QID, title, series label)
    """
    query = f"""
    SELECT ?episode ?episodeLabel ?seriesLabel ?title WHERE {{
        ?episode wdt:{wp.INSTANCE_OF.pid} wd:{wp.TELEVISION_SERIES_EPISODE};
            wdt:{wp.ORIGNAL_LANGUAGE_OF_FILM_OR_TV_SHOW.pid} wd:{wp.ENGLISH}.
        OPTIONAL {{ ?episode wdt:{wp.TITLE.pid} ?title. }}
        OPTIONAL {{ ?episode wdt:{wp.PART_OF_THE_SERIES.pid} ?series. }}
        # Skip "http://www.wikidata.org/entity/" (31 characters)
        FILTER(REGEX(?episodeLabel, SUBSTR(STR(?episode), 32)))
        FILTER((LANG(?title)) = "en")
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
        episode_id = result["episode"].split("/")[-1]
        title = result["title"]
        series_label = result["seriesLabel"]
        yield episode_id, title, series_label


def movies_with_missing_labels_with_title():
    """Find English movies with missing labels, but with a title

        Missing labels are identified by checking if the label is equal to
        the QID

        Returns an iterable of (movie QID, title)
    """
    query = f"""SELECT ?movieLabel ?title ?imdbId WHERE {{
      ?movie wdt:{wp.INSTANCE_OF.pid} wd:Q11424;
        wdt:{wp.ORIGNAL_LANGUAGE_OF_FILM_OR_TV_SHOW.pid} wd:{wp.ENGLISH};
        wdt:{wp.TITLE.pid} ?title;
        wdt:{wp.IMDB_ID.pid}  ?imdbId.
      # Skip "http://www.wikidata.org/entity/" (31 characters)
      FILTER((REGEX(?movieLabel, SUBSTR(STR(?movie), 32 ))))
      FILTER((LANG(?title)) = "en")
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "en".
        ?movie rdfs:label ?movieLabel.
      }}
    }}
    ORDER BY (?title)
    """
    print(query)
    results = SparqlQuery(repo=Site().data_repository()).select(query)
    for result in results:
        movie_label = result["movieLabel"]
        title = result["title"]
        yield movie_label, title


def movies_with_missing_titles():
    """find English movies with missing titles, but with label

        Returns an iterable of (movie QID, movie label)
    """
    query = f"""
    SELECT ?movie ?movieLabel WHERE {{
      ?movie wdt:{wp.INSTANCE_OF.pid} wd:Q11424;
        wdt:{wp.ORIGNAL_LANGUAGE_OF_FILM_OR_TV_SHOW.pid} wd:{wp.ENGLISH}.
      OPTIONAL {{ ?movie wdt:{wp.TITLE.pid} ?title. }}
      OPTIONAL {{ ?movie wdt:P345  ?imdbId. }}
      FILTER(!(BOUND(?title)))
      FILTER((BOUND(?imdbId)))
      # Skip "http://www.wikidata.org/entity/" (31 characters)
      FILTER(!(REGEX(?movieLabel, SUBSTR(STR(?movie), 32 ))))
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "en".
        ?movie rdfs:label ?movieLabel.
      }}
    }}
    ORDER BY (?movieLabel)
    """
    print(query)
    results = SparqlQuery(repo=Site().data_repository()).select(query)
    for result in results:
        movie_id = result["movie"].split("/")[-1]
        movie_label = result["movieLabel"]
        yield movie_id, movie_label


def books_with_missing_labels_with_title():
    """Find English books with missing labels, but with a title

      Missing labels are identified by checking if the label is equal to
      the QID

      Returns an iterable of (book QID, title)
  """
    query = f"""
  SELECT ?book ?bookLabel ?title WHERE {{
    ?book wdt:{wp.INSTANCE_OF.pid} wd:{wp.BOOK};
      wdt:{wp.LANGUAGE_OF_WORK_OR_NAME.pid} wd:{wp.ENGLISH};
      wdt:{wp.TITLE.pid} ?title;
    FILTER(REGEX(?bookLabel, SUBSTR(STR(?book), 32 )))
    FILTER((LANG(?title)) = "en")
    SERVICE wikibase:label {{
      bd:serviceParam wikibase:language "en".
      ?book rdfs:label ?bookLabel.
    }}
  }}
  ORDER BY (?title)
  """
    print(query)
    results = SparqlQuery(repo=Site().data_repository()).select(query)
    for result in results:
        book_label = result["bookLabel"]
        title = result["title"]
        yield book_label, title


def items_with_missing_labels_with_title():
    """Find items with missing labels, but with a title

      Missing labels are identified by checking if the label is equal to
      the QID

      Returns an iterable of (item, item QID, title)
  """
    query = f"""
  SELECT DISTINCT ?item ?itemId ?title WHERE {{
    ?item wdt:{wp.INSTANCE_OF.pid} ?itemType;
      wdt:{wp.TITLE.pid} ?title.
    VALUES ?itemType {{
      wd:{wp.TELEVISION_SERIES.ljust(10, " ")} # television series
      wd:{wp.TELEVISION_SERIES_EPISODE.ljust(10, " ")} # television series episode
      wd:{wp.BOOK.ljust(10, " ")} # book
      wd:{wp.FILM.ljust(10, " ")} # film
      wd:{wp.SILENT_FILM.ljust(10, " ")} # silent film
      wd:{wp.LITERARY_WORK.ljust(10, " ")} # literary work
    }}
    # Skip "http://www.wikidata.org/entity/" (31 characters)
    BIND(SUBSTR(STR(?item), 32 ) AS ?itemId)

    # Only look for titles that are in English, since we add the English label
    FILTER((LANG(?title)) = "en")

    # The label will be the same as the QID if the label is missing
    FILTER(REGEX(?itemLabel, ?itemId))

    SERVICE wikibase:label {{
      bd:serviceParam wikibase:language "en".
      ?item rdfs:label ?itemLabel.
    }}
  }}
  """
    print(query)
    results = SparqlQuery(repo=Site().data_repository()).select(query)
    for result in results:
        item_link = result["item"]
        item_id = result["itemId"]
        title = result["title"]
        yield item_link, item_id, title
