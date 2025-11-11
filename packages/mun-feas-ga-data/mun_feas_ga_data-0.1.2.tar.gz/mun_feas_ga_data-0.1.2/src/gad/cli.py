import click
import os.path

from . import formats


@click.group()
def main():
    pass


@main.command()
@click.argument("files_or_directories", nargs=-1)
@click.option("-m", "--curriculum-map", required=True, help="Curriculum map file")
@click.option("-o", "--output_dir", help="Output directory for FEAMS files")
def feamsify(files_or_directories, curriculum_map, output_dir):
    """Convert assessment tool data file(s) into FEAMS files.

    This input to this command is a set of data files and/or directories (which will be
    searched recursively for data files). Those files may include data in any supported
    format, so gad can be used to combine data from differently-formatted repositories
    into a single FEAMS hierarchy, e.g.:

    gad feamsify core-data/ feams-input-1/ feams-input-2/ --output feams-output/
    """

    try:
        curriculum_map = formats.CurriculumMapFile.parse(curriculum_map)
        files = formats.parse(files_or_directories, curriculum_map)

        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, ".gitignore"), "w") as gitignore:
            gitignore.write("*\n")

        for f in files:
            formats.FEAMS.dump_files(output_dir, f, curriculum_map)

    except formats.DataError as err:
        click.secho("Error: ", fg="red", bold=True, nl=False)
        click.echo(err)


@main.command()
@click.argument("files_or_directories", nargs=-1)
@click.option("-m", "--curriculum-map", help="Curriculum map file")
def parse(files_or_directories, curriculum_map: str | None):
    """Parse GA data files from either ATsheet or FEAMS format."""

    try:
        cmap = (
            formats.CurriculumMapFile.parse(curriculum_map) if curriculum_map else None
        )
        files = formats.parse(files_or_directories, cmap)

        for f in files:
            print(f)

    except formats.DataError as err:
        click.secho("Error: ", fg="red", bold=True, nl=False)
        click.echo(err)


if __name__ == "__main__":
    main()
