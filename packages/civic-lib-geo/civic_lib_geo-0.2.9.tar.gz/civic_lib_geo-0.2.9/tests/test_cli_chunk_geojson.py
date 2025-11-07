"""
tests/test_cli_chunk_geojson.py

Test the chunking of GeoJSON files into smaller files
with a maximum number of features.
"""

from pathlib import Path
import shutil

from civic_lib_geo.cli.chunk_geojson import main as chunk_geojson_main
from civic_lib_geo.geojson_utils import (
    load_geojson,
)

TEST_DATA = Path(__file__).parent / "data" / "test.geojson"
CHUNK_DIR = Path(__file__).parent / "temp_chunks"


def test_chunk_geojson_features_creates_chunks():
    if CHUNK_DIR.exists():
        shutil.rmtree(CHUNK_DIR)
    CHUNK_DIR.mkdir()

    # Run the chunking function
    chunk_geojson_main(path=TEST_DATA, max_features=10, output_dir=CHUNK_DIR)

    # Check that at least one chunk file was created
    chunk_files = list(CHUNK_DIR.glob("*.geojson"))
    assert len(chunk_files) > 0

    # Load and check each file has ≤ 10 features
    for file in chunk_files:
        gdf = load_geojson(file)
        assert len(gdf) <= 10

    # Cleanup
    shutil.rmtree(CHUNK_DIR)
