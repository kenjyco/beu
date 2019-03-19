import click


@click.command()
def main():
    """Start ipython with `beu` imported"""
    from IPython import embed
    from traitlets.config import get_config
    import beu
    from pprint import pprint
    c = get_config()
    c.InteractiveShellEmbed.colors = "Linux"
    embed(config=c)


if __name__ == '__main__':
    main()
