#!/usr/bin/env python3
"""
Download JDBC connectors for DVT Spark integration.

This script downloads JDBC drivers from Maven Central and places them in the
connectors directory for use by DVT's Spark compute engine.

Usage:
    python download_connectors.py [--all] [--connector=NAME] [--list]

Options:
    --all               Download all connectors
    --connector=NAME    Download specific connector
    --list              List all available connectors
    --output-dir=PATH   Output directory (default: ./jars)
    --clean             Remove existing JARs before downloading
"""

import argparse
import hashlib
import os
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

import yaml


class ConnectorDownloader:
    """Downloads and manages JDBC connectors."""

    MAVEN_CENTRAL = "https://repo1.maven.org/maven2"

    def __init__(self, catalog_path: Path, output_dir: Path):
        """
        Initialize downloader.

        Args:
            catalog_path: Path to connector catalog YAML
            output_dir: Directory to save JARs
        """
        self.catalog_path = catalog_path
        self.output_dir = output_dir
        self.catalog = self._load_catalog()

    def _load_catalog(self) -> Dict:
        """Load connector catalog from YAML."""
        with open(self.catalog_path) as f:
            return yaml.safe_load(f)

    def list_connectors(self) -> None:
        """List all available connectors."""
        print("\n" + "=" * 70)
        print("DVT JDBC Connector Catalog")
        print("=" * 70)
        print(f"\nVersion: {self.catalog.get('version', 'unknown')}\n")

        connectors = self.catalog.get("connectors", {})
        print(f"Available connectors: {len(connectors)}\n")

        for name, info in sorted(connectors.items()):
            print(f"  {name:20s} - {info['description']}")
            print(f"  {'':20s}   Maven: {info['maven_coordinates']}")
            print(f"  {'':20s}   License: {info['license']}")
            print()

    def _maven_to_url(self, maven_coords: str) -> str:
        """
        Convert Maven coordinates to download URL.

        Args:
            maven_coords: Maven coordinates (group:artifact:version)

        Returns:
            Download URL
        """
        parts = maven_coords.split(":")
        if len(parts) != 3:
            raise ValueError(f"Invalid Maven coordinates: {maven_coords}")

        group, artifact, version = parts
        group_path = group.replace(".", "/")

        return (
            f"{self.MAVEN_CENTRAL}/{group_path}/{artifact}/{version}/"
            f"{artifact}-{version}.jar"
        )

    def download_connector(self, name: str, force: bool = False) -> bool:
        """
        Download a specific connector.

        Args:
            name: Connector name
            force: Force re-download if already exists

        Returns:
            True if successful, False otherwise
        """
        connectors = self.catalog.get("connectors", {})
        if name not in connectors:
            print(f"Error: Connector '{name}' not found in catalog")
            return False

        connector = connectors[name]
        maven_coords = connector["maven_coordinates"]
        url = self._maven_to_url(maven_coords)

        # Extract filename from Maven coordinates
        parts = maven_coords.split(":")
        artifact, version = parts[1], parts[2]
        filename = f"{artifact}-{version}.jar"
        output_path = self.output_dir / filename

        # Check if already exists
        if output_path.exists() and not force:
            print(f"✓ {name}: Already downloaded ({filename})")
            return True

        # Download
        print(f"↓ {name}: Downloading from Maven Central...")
        print(f"  URL: {url}")

        try:
            # Ensure output directory exists
            self.output_dir.mkdir(parents=True, exist_ok=True)

            # Download with progress
            def progress_hook(block_num, block_size, total_size):
                if total_size > 0:
                    percent = min(100, block_num * block_size * 100 / total_size)
                    print(f"\r  Progress: {percent:.1f}%", end="", flush=True)

            urllib.request.urlretrieve(url, output_path, progress_hook)
            print()  # New line after progress

            # Verify download
            if output_path.exists():
                size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"✓ {name}: Downloaded successfully ({size_mb:.2f} MB)")
                print(f"  Saved to: {output_path}")
                return True
            else:
                print(f"✗ {name}: Download failed")
                return False

        except Exception as e:
            print(f"✗ {name}: Download failed - {str(e)}")
            if output_path.exists():
                output_path.unlink()  # Clean up partial download
            return False

    def download_all(self, force: bool = False) -> Dict[str, bool]:
        """
        Download all connectors.

        Args:
            force: Force re-download if already exists

        Returns:
            Dictionary mapping connector names to success status
        """
        connectors = self.catalog.get("connectors", {})
        results = {}

        print(f"\nDownloading {len(connectors)} connectors...\n")

        for i, name in enumerate(sorted(connectors.keys()), 1):
            print(f"[{i}/{len(connectors)}] ", end="")
            results[name] = self.download_connector(name, force)
            print()

        return results

    def clean_jars(self) -> None:
        """Remove all downloaded JARs."""
        if not self.output_dir.exists():
            print("No JARs directory found")
            return

        jar_files = list(self.output_dir.glob("*.jar"))
        if not jar_files:
            print("No JARs to clean")
            return

        print(f"\nRemoving {len(jar_files)} JAR files from {self.output_dir}...")
        for jar in jar_files:
            jar.unlink()
            print(f"  Removed: {jar.name}")

        print("\nCleanup complete")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Download JDBC connectors for DVT",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all connectors",
    )

    parser.add_argument(
        "--connector",
        type=str,
        help="Download specific connector by name",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available connectors",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("jars"),
        help="Output directory for JARs (default: ./jars)",
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove existing JARs before downloading",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if JAR exists",
    )

    args = parser.parse_args()

    # Find catalog file
    script_dir = Path(__file__).parent
    catalog_path = script_dir / "catalog.yml"

    if not catalog_path.exists():
        print(f"Error: Catalog file not found: {catalog_path}")
        sys.exit(1)

    # Initialize downloader
    downloader = ConnectorDownloader(catalog_path, args.output_dir)

    # Execute command
    if args.list:
        downloader.list_connectors()

    elif args.clean:
        downloader.clean_jars()

    elif args.all:
        if args.clean:
            downloader.clean_jars()
            print()

        results = downloader.download_all(args.force)

        # Summary
        success_count = sum(1 for v in results.values() if v)
        fail_count = len(results) - success_count

        print("=" * 70)
        print("Download Summary")
        print("=" * 70)
        print(f"Total connectors: {len(results)}")
        print(f"Successful: {success_count}")
        print(f"Failed: {fail_count}")

        if fail_count > 0:
            print("\nFailed connectors:")
            for name, success in results.items():
                if not success:
                    print(f"  - {name}")

        sys.exit(0 if fail_count == 0 else 1)

    elif args.connector:
        if args.clean:
            downloader.clean_jars()
            print()

        success = downloader.download_connector(args.connector, args.force)
        sys.exit(0 if success else 1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
