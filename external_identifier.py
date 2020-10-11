import requests
import re
from bs4 import BeautifulSoup


def imdb_id(title):
    """IMDB identifier
    >>> imdb_id("Inception")
    'tt1375666'
    >>> imdb_id("Interstellar")
    'tt0816692'
    """
    web_text = requests.get(f"https://www.imdb.com/find?q={title}").text
    soup = BeautifulSoup(web_text, "html.parser")
    candidates = soup.find("table", attrs={"class": "findList"})
    identifier = candidates.find("a", href=True)["href"]
    return identifier.rstrip("/").split("/")[-1]


def tv_tropes_id(title):
    """TVTropes identifier

    >>> tv_tropes_id("Harry Potter and the Philosopher's Stone")
    "Film/HarryPotterAndThePhilosophersStone"
    >>> tv_tropes_id("Inception")
    "Film/Inception"
    >>> tv_tropes_id("Interstellar")
    "Film/Interstellar"
    """
    pass


def eidr_identifier(title):
    """Entertainment Identifier Registry identifer

    E.g. Inception: https://ui.eidr.org/view/content?id=10.5240/0EF3-54F9-2642-0B49-6829-R

    >>> eidr_identifier("Inception")
    "10.5240/0EF3-54F9-2642-0B49-6829-R"
    >>> eidr_identifier("Interstellar")
    "10.5240/7F93-54BB-49EF-CD69-2C90-R"
    """
    pass


def fandom_wiki_id(title):
    """Fandom Wiki identifier"""
    pass


def the_tvdb_dot_com_id(title):
    """thetvdb.com identifier

    >>> the_tvdb_dot_com_id("Inception")
    "movies/inception"
    >>> the_tvdb_dot_com_id("Interstellar")
    "movies/interstellar"
    >>> the_tvdb_dot_com_id("Harry Potter and the Philosopher's Stone")
    "movies/harry-potter-and-the-sorcerers-stone"
    """
    pass


def board_game_geek_id(title):
    """The BGG ID on boardgamegeek.com

    >>> board_game_geek_id("Clank!")
    201808
    >>> board_game_geek_id("Bunny Kingdom")
    184921
    """
    res = requests.get('https://boardgamegeek.com/geeksearch.php?action=search&objecttype=boardgame&q={}'.format(title))
    if res.status_code != 200:
        return ""
    else:
        web_text = res.content
        soup = BeautifulSoup(web_text, "html.parser")
        td_details = soup.find('table',{'id':'collectionitems'})
        matching_url = td_details.find_all('a',attrs={'href': re.compile("^/boardgame")})[0]['href']
        matches = re.findall('[0-9]+', matching_url)
        if len(matches) > 0:
            return int(matches[0])
        else:
            return ""

if __name__ == "__main__":
    import doctest
    doctest.testmod()
