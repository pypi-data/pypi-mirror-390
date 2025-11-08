#!/usr/bin/env python3
"""
Simple example showing how to use raster2dggs to convert a raster to A5 cells.

This demonstrates using the raster2dggs package to index raster data to A5 DGGS.

Usage:
    python convert_raster.py <input.tif> <resolution>

Example:
    python convert_raster.py sample.tif 10
"""

import sys
import argparse

try:
    from raster2dggs import raster_to_a5
except ImportError:
    print("Error: raster2dggs is required. Install with: pip install raster2dggs")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Convert a raster (GeoTIFF) file to A5 cells using raster2dggs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  # Convert sample.tif at resolution 10
  python convert_raster.py sample.tif 10

  # This will create output.parquet with A5-indexed raster data
        """
    )

    parser.add_argument('input', help='Input GeoTIFF file path')
    parser.add_argument('resolution', type=int, help='A5 resolution level (0-30)')
    parser.add_argument('--output', default='output.parquet',
                       help='Output Parquet file path (default: output.parquet)')

    args = parser.parse_args()

    # Validate resolution
    if args.resolution < 0 or args.resolution > 30:
        print("Error: Resolution must be between 0 and 30")
        sys.exit(1)

    print(f"Converting {args.input} to A5 cells at resolution {args.resolution}...")
    print(f"Output will be written to: {args.output}")

    try:
        # Use raster2dggs to convert the raster to A5 cells
        raster_to_a5(
            input_file=args.input,
            resolution=args.resolution,
            output_file=args.output,
            dggs_type='a5'
        )

        print(f"\nConversion complete! Results saved to {args.output}")

    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
