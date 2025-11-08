#!/usr/bin/env python3
"""Generate Talky icon files at multiple resolutions for desktop integration."""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Import PIL before talky to avoid dependency issues
from PIL import Image, ImageDraw

# Import the icons module directly, bypassing __init__.py
import importlib.util
icons_path = src_path / "talky" / "ui" / "icons.py"
spec = importlib.util.spec_from_file_location("icons", icons_path)
icons_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(icons_module)
IconGenerator = icons_module.IconGenerator


def generate_icons(output_dir: Path):
    """
    Generate icon files at standard resolutions.

    Args:
        output_dir: Directory to save icon files
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Standard icon sizes for freedesktop.org
    sizes = [16, 22, 24, 32, 48, 64, 128, 256]

    generator = IconGenerator()

    print("Generating Talky icons...")
    print(f"Output directory: {output_dir}")
    print()

    for size in sizes:
        # Generate idle state icon (main icon)
        icon = generator.create_icon("idle", (size, size))

        # Save as PNG
        output_path = output_dir / f"talky-{size}x{size}.png"
        icon.save(output_path, "PNG")

        print(f"  ✓ Generated {size}x{size} icon: {output_path.name}")

    # Generate SVG-size for scalable (256x256 as base)
    icon_256 = generator.create_icon("idle", (256, 256))
    svg_path = output_dir / "talky.svg"

    # Note: PIL doesn't directly create SVG, so we use PNG at highest resolution
    # For true SVG, would need additional library or manual creation
    scalable_path = output_dir / "talky-scalable.png"
    icon_256.save(scalable_path, "PNG")
    print(f"  ✓ Generated scalable icon: {scalable_path.name}")

    # Generate state icons for documentation/reference
    print("\n  Generating state icons (for reference)...")
    for state in ["idle", "recording", "processing"]:
        icon = generator.create_icon(state, (64, 64))
        state_path = output_dir / f"talky-{state}-64x64.png"
        icon.save(state_path, "PNG")
        print(f"    • {state}: {state_path.name}")

    print(f"\n✓ Icon generation complete! {len(sizes) + 1} icons generated.")
    print(f"\nTo install icons system-wide:")
    print(f"  sudo cp icons/talky-*.png /usr/share/icons/hicolor/<size>/apps/talky.png")
    print(f"  sudo gtk-update-icon-cache /usr/share/icons/hicolor/")


def main():
    """Generate icons."""
    # Default output directory
    icons_dir = Path(__file__).parent.parent / "icons"

    # Allow custom output directory via command line
    if len(sys.argv) > 1:
        icons_dir = Path(sys.argv[1])

    try:
        generate_icons(icons_dir)
        return 0
    except Exception as e:
        print(f"\n✗ Error generating icons: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
