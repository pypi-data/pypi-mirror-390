# Raster to A5 Example

This example demonstrates how to use the [raster2dggs](https://github.com/manaakiwhenua/raster2dggs) package to convert raster images (GeoTIFF files) to A5 cells.

## Installation

Install raster2dggs and its dependencies:

```bash
# raster2dggs requires Python 3.11+ and GDAL
pip install raster2dggs
```

**Note**: raster2dggs requires GDAL, which can be complex to install. On macOS with Homebrew:

```bash
brew install gdal
pip install raster2dggs
```

For other systems, see the [raster2dggs installation guide](https://github.com/manaakiwhenua/raster2dggs#installation).

## Usage

```bash
python convert_raster.py <input.tif> <resolution> [--output output.parquet]
```

### Arguments

- `input.tif`: Path to input GeoTIFF file
- `resolution`: A5 resolution level (0-30)
- `--output`: Output Parquet file path (default: `output.parquet`)

## Example

Download and convert the sample GeoTIFF from [mommermi/geotiff_sample](https://github.com/mommermi/geotiff_sample):

```bash
# Download sample data
wget https://raw.githubusercontent.com/mommermi/geotiff_sample/master/sample.tif

# Convert at resolution 10
python convert_raster.py sample.tif 10

# This creates output.parquet with A5-indexed raster data
```

## What raster2dggs Does

The raster2dggs package:
- Reads the GeoTIFF file and handles coordinate transformations
- Maps each pixel to an A5 cell at the specified resolution
- Aggregates pixel values when multiple pixels map to the same cell
- Outputs to Apache Parquet format for efficient storage and querying
- Supports multi-band rasters (preserves all bands in the output)

## Output Format

The output Parquet file contains columns for:
- Cell identifiers
- Aggregated band values
- Additional metadata

See the [raster2dggs documentation](https://github.com/manaakiwhenua/raster2dggs) for more details on the output format and additional options.
