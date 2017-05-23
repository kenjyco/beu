import click
import beu


@click.command()
@click.argument('query', nargs=1, default='')
def main(query):
    """Find and download vids"""
    query = query or beu.ih.user_input('vid query')
    if not query:
        return

    selected = beu.ih.make_selections(
        beu.ph.youtube_serp(query),
        wrap=False,
        item_format='{duration} .::. {title} .::. {user} .::. {uploaded}',
    )
    if selected:
        results = [beu.yh.av_from_url(x['link'], playlist=True, query=query) for x in selected]
        return results
