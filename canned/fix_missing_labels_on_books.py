"""Add an English label on books which have an English title"""
import click
from pywikibot import Site, ItemPage, WbMonolingualText, Claim

from sparql.queries import books_with_missing_labels_with_title
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
    for book_id, title in books_with_missing_labels_with_title():
        print(
            f"{dry_str}Setting label='{title}' for {book_id} ( https://www.wikidata.org/wiki/{book_id} )"
        )
        if not dry:
            movie_item = ItemPage(repo, book_id)
            movie_item.get()
            movie_item.editLabels({"en": title})


if __name__ == "__main__":
    main()
