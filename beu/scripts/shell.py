import click


@click.command()
def main():
    """Start ipython with `beu` imported"""
    from IPython import embed
    from traitlets.config import Config
    import beu
    from pprint import pprint
    c = Config()
    c.InteractiveShellEmbed.colors = "Linux"
    c.InteractiveShellEmbed.editing_mode = "vi"
    embed(config=c)


if __name__ == '__main__':
    main()
