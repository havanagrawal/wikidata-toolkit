def imdb_id(title):
    """IMDB identifier

    >>> imdb_id("Inception")
    "tt1375666"
    >>> imdb_id("Interstellar")
    "tt0816692"
    """
    pass


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
    """TVDB.com identifier

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
    pass