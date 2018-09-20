import click


@click.command()
def main():
    """Start ipython with `beu` imported"""
    from IPython import embed
    import beu
    from pprint import pprint
    embed()


if __name__ == '__main__':
    main()
