"""Add an English label on movies which have an English title"""
import click
from pywikibot import Site, ItemPage, WbMonolingualText, Claim

from sparql.queries import movies_with_missing_labels_with_title
import properties.wikidata_properties as wp


@click.command()
@click.option("--dry", is_flag=True, default=False, help="Only print out the changes, don't run any commands")
def main(dry=False):
    dry_str = ""
    if dry:
        print("Running in dry-run mode, will not implement any changes")
        dry_str = "[DRY-RUN MODE] "
    repo = Site().data_repository()
    for movie_id, title in movies_with_missing_labels_with_title():
        print(f"{dry_str}Setting label='{title}' for {movie_id} ( https://www.wikidata.org/wiki/{movie_id} )")
        if not dry:
            movie_item = ItemPage(repo, movie_id)
            movie_item.get()
            movie_item.editLabels({'en': title})


if __name__ == "__main__":
    main()
