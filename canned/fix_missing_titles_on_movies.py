"""Add an English title on movies which have an English label

    Sets the title to the same value as the label
"""
import click
from pywikibot import Site, ItemPage, WbMonolingualText, Claim

from sparql.queries import movies_with_missing_titles
import properties.wikidata_properties as wp


@click.command()
@click.option(
    "--dry",
    is_flag=True,
    default=False,
    help="Only print out the changes, don't run any commands",
)
def main(dry=False):
    dry_str = ""
    if dry:
        print("Running in dry-run mode, will not implement any changes")
        dry_str = "[DRY-RUN MODE] "
    repo = Site().data_repository()
    for movie_id, movie_label in movies_with_missing_titles():
        print(
            f"{dry_str}Setting title='{movie_label}' for {movie_id} ( https://www.wikidata.org/wiki/{movie_id} )"
        )
        if not dry:
            movie_item = ItemPage(repo, movie_id)
            movie_item.get()
            claim = Claim(repo, wp.TITLE.pid)
            claim.setTarget(WbMonolingualText(movie_label, "en"))
            movie_item.addClaim(claim)


if __name__ == "__main__":
    main()
