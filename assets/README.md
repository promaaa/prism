# Prism Assets

This directory contains image assets for the Prism application.

## Application Icon

### Required File: `prism2.png`

The application uses `prism2.png` as its primary icon. This icon will be displayed in:
- Application window title bar
- macOS Dock
- Application switcher (Cmd+Tab)
- Finder

### Icon Specifications

**Recommended Specifications:**
- **Format**: PNG with transparency
- **Size**: 512x512 pixels (minimum), 1024x1024 pixels (recommended)
- **Color Space**: sRGB
- **Transparency**: Supported (alpha channel)

**Design Guidelines:**
- Clean, modern design
- Recognizable at small sizes (16x16px)
- Works well on both light and dark backgrounds
- Represents finance/investment theme (e.g., prism, chart, currency symbol)

### Fallback

If `prism2.png` is not found, the application will fall back to `icon.png`.

## Creating Your Icon

### Option 1: Use an existing image
Place your icon file as `prism2.png` in this directory.

### Option 2: Design from scratch
Use design tools like:
- **Figma** (free, web-based)
- **Sketch** (macOS)
- **GIMP** (free, cross-platform)
- **Adobe Photoshop**

### Option 3: Generate with AI
Use AI image generators:
- DALL-E
- Midjourney
- Stable Diffusion

**Example prompts:**
- "Modern app icon for personal finance app, prism logo, gradient colors, minimalist, 3D"
- "Clean financial app icon with prism crystal splitting light into money symbols, professional"
- "App icon showing colorful prism with chart arrows, investment theme, sharp design"

## For macOS .app Bundle

When packaging the application with PyInstaller, convert the PNG to ICNS:

```bash
# Install iconutil (comes with Xcode Command Line Tools)
mkdir prism.iconset

# Create different sizes
sips -z 16 16     prism2.png --out prism.iconset/icon_16x16.png
sips -z 32 32     prism2.png --out prism.iconset/icon_16x16@2x.png
sips -z 32 32     prism2.png --out prism.iconset/icon_32x32.png
sips -z 64 64     prism2.png --out prism.iconset/icon_32x32@2x.png
sips -z 128 128   prism2.png --out prism.iconset/icon_128x128.png
sips -z 256 256   prism2.png --out prism.iconset/icon_128x128@2x.png
sips -z 256 256   prism2.png --out prism.iconset/icon_256x256.png
sips -z 512 512   prism2.png --out prism.iconset/icon_256x256@2x.png
sips -z 512 512   prism2.png --out prism.iconset/icon_512x512.png
sips -z 1024 1024 prism2.png --out prism.iconset/icon_512x512@2x.png

# Convert to ICNS
iconutil -c icns prism.iconset

# Cleanup
rm -rf prism.iconset
```

Then use in PyInstaller:
```bash
pyinstaller --name=Prism --windowed --icon=assets/prism.icns -m prism
```

## Current Files

- `icon.png` - Fallback icon (if present)
- `prism2.png` - Primary application icon (add this file!)

## Notes

- The application will print a warning if no icon is found
- Icons are loaded at application startup
- Changes to icons require restarting the application
- For best results on Retina displays, use 1024x1024px or higher

---

**Need help?** Check the [PyQt6 documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/) for more information on icons and resources.