#!/bin/bash
# Prism Icon Setup Script
# This script helps you set up the application icon (prism2.png)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSETS_DIR="$SCRIPT_DIR/assets"
ICON_FILE="$ASSETS_DIR/prism2.png"

echo "======================================"
echo "  Prism Icon Setup"
echo "======================================"
echo ""

# Check if assets directory exists
if [ ! -d "$ASSETS_DIR" ]; then
    echo "❌ Assets directory not found!"
    echo "Creating assets directory..."
    mkdir -p "$ASSETS_DIR"
    echo "✅ Assets directory created"
fi

# Check if prism2.png already exists
if [ -f "$ICON_FILE" ]; then
    echo "✅ prism2.png already exists!"
    echo "   Location: $ICON_FILE"

    # Get file info
    if command -v file &> /dev/null; then
        echo ""
        echo "File info:"
        file "$ICON_FILE"
    fi

    if command -v sips &> /dev/null; then
        echo ""
        echo "Image dimensions:"
        sips -g pixelWidth -g pixelHeight "$ICON_FILE" 2>/dev/null | grep -E "pixelWidth|pixelHeight" || true
    fi

    echo ""
    read -p "Do you want to replace it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing icon. Exiting."
        exit 0
    fi
    echo "Preparing to replace icon..."
else
    echo "ℹ️  prism2.png not found"
fi

echo ""
echo "Options for setting up your icon:"
echo ""
echo "1. Copy from a local file"
echo "2. Download from URL"
echo "3. Create placeholder (for testing)"
echo "4. Generate instructions only"
echo ""
read -p "Choose an option (1-4): " -n 1 -r OPTION
echo
echo ""

case $OPTION in
    1)
        echo "📁 Copy from local file"
        echo ""
        read -p "Enter the path to your icon file: " SOURCE_FILE

        # Expand tilde
        SOURCE_FILE="${SOURCE_FILE/#\~/$HOME}"

        if [ ! -f "$SOURCE_FILE" ]; then
            echo "❌ File not found: $SOURCE_FILE"
            exit 1
        fi

        echo "Copying $SOURCE_FILE to $ICON_FILE..."
        cp "$SOURCE_FILE" "$ICON_FILE"
        echo "✅ Icon copied successfully!"
        ;;

    2)
        echo "🌐 Download from URL"
        echo ""
        read -p "Enter the URL of your icon: " ICON_URL

        if command -v curl &> /dev/null; then
            echo "Downloading..."
            curl -L -o "$ICON_FILE" "$ICON_URL"
            echo "✅ Icon downloaded successfully!"
        elif command -v wget &> /dev/null; then
            echo "Downloading..."
            wget -O "$ICON_FILE" "$ICON_URL"
            echo "✅ Icon downloaded successfully!"
        else
            echo "❌ Neither curl nor wget found. Please install one of them."
            exit 1
        fi
        ;;

    3)
        echo "🎨 Create placeholder icon (for testing)"
        echo ""

        if command -v sips &> /dev/null; then
            # Create a simple colored square using sips
            echo "Creating 512x512 placeholder icon..."

            # Create a temporary colored image
            TEMP_PNG=$(mktemp).png

            # Create a simple gradient placeholder using ImageMagick if available
            if command -v convert &> /dev/null; then
                convert -size 512x512 gradient:"#667EEA"-"#764BA2" "$ICON_FILE"
                echo "✅ Gradient placeholder created!"
            else
                # Fallback: copy and resize existing icon.png if available
                if [ -f "$ASSETS_DIR/icon.png" ]; then
                    cp "$ASSETS_DIR/icon.png" "$ICON_FILE"
                    echo "✅ Copied from icon.png as placeholder!"
                else
                    echo "⚠️  ImageMagick not found and no icon.png available"
                    echo "Creating basic placeholder..."
                    # This is a workaround - just create an empty file
                    # User should replace with actual icon
                    touch "$ICON_FILE"
                    echo "⚠️  Empty placeholder created - please replace with actual icon!"
                fi
            fi
        else
            echo "⚠️  sips command not found (are you on macOS?)"
            echo "Creating empty placeholder..."
            touch "$ICON_FILE"
            echo "⚠️  Empty placeholder created - please replace with actual icon!"
        fi
        ;;

    4)
        echo "📝 Icon Setup Instructions"
        echo ""
        echo "To set up your Prism application icon:"
        echo ""
        echo "1. Create or obtain a PNG icon file (512x512 or 1024x1024 recommended)"
        echo ""
        echo "2. Name it 'prism2.png'"
        echo ""
        echo "3. Place it in: $ASSETS_DIR/"
        echo ""
        echo "4. The icon should:"
        echo "   - Be in PNG format with transparency"
        echo "   - Have square dimensions (512x512 or 1024x1024)"
        echo "   - Use sRGB color space"
        echo "   - Be recognizable at small sizes (16x16px)"
        echo ""
        echo "Icon Design Ideas:"
        echo "   - Prism splitting light into colors"
        echo "   - Chart/graph with prism effect"
        echo "   - Currency symbols with gradient"
        echo "   - Modern, minimalist financial symbol"
        echo ""
        echo "You can:"
        echo "   - Design in Figma, Sketch, or GIMP"
        echo "   - Generate with AI (DALL-E, Midjourney)"
        echo "   - Hire a designer on Fiverr"
        echo ""
        echo "For macOS .app bundle, convert to .icns:"
        echo "   See: $ASSETS_DIR/README.md"
        echo ""
        exit 0
        ;;

    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "======================================"
echo "  Verifying Icon"
echo "======================================"
echo ""

if [ -f "$ICON_FILE" ]; then
    echo "✅ Icon file exists: $ICON_FILE"

    # Check file size
    FILE_SIZE=$(ls -lh "$ICON_FILE" | awk '{print $5}')
    echo "📊 File size: $FILE_SIZE"

    # Check if it's a valid image (macOS only)
    if command -v sips &> /dev/null; then
        if sips -g format "$ICON_FILE" &>/dev/null; then
            echo "✅ Valid image file"

            # Get dimensions
            WIDTH=$(sips -g pixelWidth "$ICON_FILE" 2>/dev/null | grep pixelWidth | awk '{print $2}')
            HEIGHT=$(sips -g pixelHeight "$ICON_FILE" 2>/dev/null | grep pixelHeight | awk '{print $2}')

            echo "📐 Dimensions: ${WIDTH}x${HEIGHT}"

            # Check if square
            if [ "$WIDTH" == "$HEIGHT" ]; then
                echo "✅ Square dimensions (recommended)"
            else
                echo "⚠️  Not square - may not display correctly"
            fi

            # Check size recommendations
            if [ "$WIDTH" -ge 512 ] && [ "$HEIGHT" -ge 512 ]; then
                echo "✅ Good resolution for Retina displays"
            elif [ "$WIDTH" -ge 256 ] && [ "$HEIGHT" -ge 256 ]; then
                echo "⚠️  Minimum resolution - consider using 512x512 or larger"
            else
                echo "⚠️  Resolution too low - recommend at least 512x512"
            fi
        else
            echo "❌ Not a valid image file!"
            exit 1
        fi
    fi

    echo ""
    echo "======================================"
    echo "  Setup Complete!"
    echo "======================================"
    echo ""
    echo "Your Prism icon has been set up successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Run the application: python main.py"
    echo "2. Check if the icon appears in the dock/taskbar"
    echo "3. If needed, restart the app to see changes"
    echo ""
    echo "To create a macOS .app bundle with this icon:"
    echo "   See: $ASSETS_DIR/README.md"
    echo ""
else
    echo "❌ Icon setup failed"
    exit 1
fi
