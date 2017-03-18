import click


@click.command()
def main():
    """Start ipython with `beu` imported"""
    from IPython import embed
    import beu
    embed()


if __name__ == '__main__':
    main()
