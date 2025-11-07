"""cli.py.

Command-line interface (CLI) for civic-lib-geo.

Provides repo-specific commands for:
- Chunking
- Simplifying
- Property inspection
- File size checks

Run `civic-geo --help` for usage.
"""

from pathlib import Path
import sys

from civic_lib_core import log_utils
import typer

from civic_lib_geo import geojson_utils

logger = log_utils.logger

app = typer.Typer(help="Civic Geo CLI")

FOLDER_ARG = typer.Argument(..., exists=True, file_okay=False)
SINGLE_FILE_OPT = typer.Option(
    None, help="Optionally apply the action to one specific file instead of a folder."
)


@app.command("check-size")
@app.command("size")
def check_size_command(path: Path):
    """Report the size of a GeoJSON file and whether it exceeds the GitHub Pages 25MB limit."""
    from . import check_size

    check_size.main(path)


@app.command("chunk-geojson")
@app.command("chunk")
def chunk_command(
    folder: Path = FOLDER_ARG,
    max_features: int = 500,
    single_file: Path = SINGLE_FILE_OPT,
):
    """Chunk a GeoJSON file or all files in a folder into smaller files with limited features."""
    from . import chunk_geojson

    if single_file:
        chunk_geojson.main(single_file, max_features)
    else:
        geojson_utils.apply_to_geojson_folder(
            folder, chunk_geojson.main, max_features=max_features, suffix="_chunked.geojson"
        )


@app.command("read-props")
def props_command(path: Path):
    """Display the property keys from the first feature of a GeoJSON file."""
    from . import read_props

    read_props.main(path)


@app.command("simplify-geojson")
@app.command("simplify")
def simplify_command(
    folder: Path = FOLDER_ARG,
    tolerance: float = 0.01,
    single_file: Path = SINGLE_FILE_OPT,
):
    """Simplify one GeoJSON file or all files in a folder using the given tolerance."""
    from . import simplify_geojson

    if single_file:
        simplify_geojson.main(single_file, tolerance)
    else:
        geojson_utils.apply_to_geojson_folder(
            folder, simplify_geojson.main, tolerance=tolerance, suffix="_simplified.geojson"
        )


@app.command("shapefile-to-geojson")
@app.command("shp-to-geo")
def shapefile_to_geojson_command(shp_path: Path, geojson_path: Path):
    """Convert a shapefile to GeoJSON."""
    from . import shapefile_to_geojson

    shapefile_to_geojson.main(shp_path, geojson_path)


@app.command("topojson-to-geojson")
@app.command("topo-to-geo")
def topojson_to_geojson_command(topo_path: Path, geojson_path: Path):
    """Convert a TopoJSON file to GeoJSON using GeoPandas (if supported)."""
    from . import topojson_to_geojson

    logger.warning("⚠️ TopoJSON support depends on GDAL. Consider using mapshaper if this fails.")
    topojson_to_geojson.main(topo_path, geojson_path)


def main() -> int:
    """Run the main entry point for the CLI application.

    This function serves as the primary entry point for the command-line interface.
    It initializes and runs the app, then returns a success status code.

    Returns:
        int: Exit status code (0 for success).
    """
    app()
    return 0


if __name__ == "__main__":
    sys.exit(main())
