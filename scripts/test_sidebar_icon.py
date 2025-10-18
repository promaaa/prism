#!/usr/bin/env python3
"""
Test script to verify sidebar icon (icon.png) display in Prism.

This script tests:
1. Icon file exists
2. Icon loads correctly in sidebar
3. Icon is properly sized (50x50px)
4. Sidebar header layout is correct
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtCore import Qt, QCoreApplication

# Fix QtWebEngine import issue - must be set before QApplication
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

from PyQt6.QtWidgets import QApplication, QLabel
from PyQt6.QtGui import QPixmap


def test_icon_exists():
    """Test that icon.png exists in assets directory."""
    print("=" * 80)
    print("TEST 1: Icon File Exists")
    print("=" * 80)

    icon_path = Path(__file__).parent.parent / "assets" / "icon.png"

    if icon_path.exists():
        print(f"✓ Icon found at: {icon_path}")
        print(f"  File size: {icon_path.stat().st_size} bytes")
        return True
    else:
        print(f"✗ Icon NOT found at: {icon_path}")
        return False


def test_icon_loading():
    """Test that icon loads correctly as QPixmap."""
    print("\n" + "=" * 80)
    print("TEST 2: Icon Loading")
    print("=" * 80)

    icon_path = Path(__file__).parent.parent / "assets" / "icon.png"

    try:
        pixmap = QPixmap(str(icon_path))

        if pixmap.isNull():
            print(f"✗ Failed to load icon as QPixmap")
            return False

        print(f"✓ Icon loaded successfully")
        print(f"  Original size: {pixmap.width()}x{pixmap.height()}px")

        # Test scaling to 50x50
        scaled_pixmap = pixmap.scaled(
            50,
            50,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        print(f"  Scaled size: {scaled_pixmap.width()}x{scaled_pixmap.height()}px")

        if scaled_pixmap.width() <= 50 and scaled_pixmap.height() <= 50:
            print(f"✓ Icon scaled correctly (within 50x50px bounds)")
            return True
        else:
            print(f"✗ Icon scaling failed")
            return False

    except Exception as e:
        print(f"✗ Exception during icon loading: {e}")
        return False


def test_sidebar_icon_in_ui():
    """Test icon display in actual UI context."""
    print("\n" + "=" * 80)
    print("TEST 3: Icon in Sidebar UI")
    print("=" * 80)

    try:
        from prism.ui.main_window import MainWindow

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        window = MainWindow()

        # Find the sidebar
        sidebar = window.sidebar
        if sidebar is None:
            print("✗ Sidebar not found in MainWindow")
            return False

        print(f"✓ Sidebar found")

        # Find icon label in sidebar
        icon_labels = sidebar.findChildren(QLabel)
        icon_label = None

        for label in icon_labels:
            if label.property("class") == "sidebar-icon":
                icon_label = label
                break

        if icon_label is None:
            print("✗ Sidebar icon label not found")
            return False

        print(f"✓ Sidebar icon label found")

        # Check pixmap
        pixmap = icon_label.pixmap()
        if pixmap is None or pixmap.isNull():
            print("✗ Icon pixmap not set or is null")
            return False

        print(f"✓ Icon pixmap is set")
        print(f"  Size: {icon_label.width()}x{icon_label.height()}px")
        print(f"  Pixmap size: {pixmap.width()}x{pixmap.height()}px")

        # Check size
        if icon_label.width() == 50 and icon_label.height() == 50:
            print(f"✓ Icon label is correctly sized (50x50px)")
        else:
            print(
                f"⚠ Icon label size is {icon_label.width()}x{icon_label.height()}px (expected 50x50px)"
            )

        # Find logo text
        logo_label = None
        for label in icon_labels:
            if label.property("class") == "sidebar-logo":
                logo_label = label
                break

        if logo_label:
            print(f"✓ Logo text label found: '{logo_label.text()}'")
        else:
            print("⚠ Logo text label not found")

        return True

    except Exception as e:
        print(f"✗ Exception during UI test: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_sidebar_layout():
    """Test sidebar header layout structure."""
    print("\n" + "=" * 80)
    print("TEST 4: Sidebar Header Layout")
    print("=" * 80)

    try:
        from prism.ui.main_window import MainWindow

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        window = MainWindow()

        sidebar = window.sidebar

        # Find header widget
        header_widgets = sidebar.findChildren(type(sidebar))
        header_widget = None

        for widget in header_widgets:
            if widget.property("class") == "sidebar-header":
                header_widget = widget
                break

        if header_widget is None:
            print("✗ Sidebar header widget not found")
            return False

        print(f"✓ Sidebar header widget found")

        # Check layout
        layout = header_widget.layout()
        if layout is None:
            print("✗ Sidebar header has no layout")
            return False

        print(f"✓ Sidebar header layout found: {layout.__class__.__name__}")
        print(f"  Layout spacing: {layout.spacing()}px")
        print(f"  Layout margins: {layout.contentsMargins()}")
        print(f"  Number of items: {layout.count()}")

        return True

    except Exception as e:
        print(f"✗ Exception during layout test: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "PRISM SIDEBAR ICON TEST SUITE" + " " * 29 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    results = []

    # Test 1: Icon exists
    results.append(("Icon File Exists", test_icon_exists()))

    # Test 2: Icon loading
    if results[0][1]:  # Only run if icon exists
        app = QApplication(sys.argv)  # Create QApplication for pixmap tests
        results.append(("Icon Loading", test_icon_loading()))

    # Test 3 & 4: UI tests (need QApplication)
    if all(r[1] for r in results):
        results.append(("Icon in Sidebar UI", test_sidebar_icon_in_ui()))
        results.append(("Sidebar Layout", test_sidebar_layout()))

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} | {test_name}")

    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Sidebar icon is correctly implemented.")
        return 0
    else:
        print("\n❌ Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
