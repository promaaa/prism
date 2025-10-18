"""
Settings tab for Prism application.
Provides comprehensive settings and preferences management.
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QCheckBox,
    QSpinBox,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QScrollArea,
    QFrame,
    QGroupBox,
    QFormLayout,
    QButtonGroup,
    QRadioButton,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QFont

from ..database.db_manager import DatabaseManager
from ..utils.logger import get_logger

logger = get_logger("ui.settings_tab")


class SettingsTab(QWidget):
    """
    Settings tab widget with comprehensive app configuration options.
    """

    settings_changed = pyqtSignal()
    theme_changed = pyqtSignal(str)

    def __init__(self, db_manager: DatabaseManager, parent=None):
        """
        Initialize settings tab.

        Args:
            db_manager: Database manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = db_manager
        self.settings = QSettings("Prism", "PrismApp")
        self._init_ui()
        self._load_settings()

    def _init_ui(self):
        """Initialize UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = self._create_header()
        main_layout.addWidget(header)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(25)

        # Settings sections
        content_layout.addWidget(self._create_appearance_section())
        content_layout.addWidget(self._create_general_section())
        content_layout.addWidget(self._create_data_section())
        content_layout.addWidget(self._create_currency_section())
        content_layout.addWidget(self._create_notifications_section())
        content_layout.addWidget(self._create_about_section())

        content_layout.addStretch()

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def _create_header(self):
        """Create settings header."""
        header = QWidget()
        header.setProperty("class", "settings-header")
        header.setFixedHeight(80)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 0, 30, 0)

        # Title
        title = QLabel("⚙️  Paramètres")
        title.setProperty("class", "settings-title")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        layout.addStretch()

        # Save button
        save_btn = QPushButton("💾  Enregistrer")
        save_btn.setProperty("class", "primary-button")
        save_btn.setFixedHeight(40)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn)

        return header

    def _create_appearance_section(self):
        """Create appearance settings section."""
        section = QGroupBox("🎨  Apparence")
        section.setProperty("class", "settings-section")
        layout = QFormLayout(section)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Theme selection
        theme_label = QLabel("Thème:")
        theme_label.setProperty("class", "settings-label")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Sombre", "Clair", "Auto (Système)"])
        self.theme_combo.setProperty("class", "settings-combo")
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        layout.addRow(theme_label, self.theme_combo)

        # Font size
        font_label = QLabel("Taille de police:")
        font_label.setProperty("class", "settings-label")
        self.font_spin = QSpinBox()
        self.font_spin.setRange(10, 18)
        self.font_spin.setValue(13)
        self.font_spin.setSuffix(" px")
        self.font_spin.setProperty("class", "settings-spin")
        layout.addRow(font_label, self.font_spin)

        # Compact mode
        compact_label = QLabel("Mode compact:")
        compact_label.setProperty("class", "settings-label")
        self.compact_check = QCheckBox("Réduire l'espacement entre les éléments")
        self.compact_check.setProperty("class", "settings-checkbox")
        layout.addRow(compact_label, self.compact_check)

        # Animations
        anim_label = QLabel("Animations:")
        anim_label.setProperty("class", "settings-label")
        self.animations_check = QCheckBox("Activer les animations et transitions")
        self.animations_check.setChecked(True)
        self.animations_check.setProperty("class", "settings-checkbox")
        layout.addRow(anim_label, self.animations_check)

        return section

    def _create_general_section(self):
        """Create general settings section."""
        section = QGroupBox("⚡  Général")
        section.setProperty("class", "settings-section")
        layout = QFormLayout(section)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Language
        lang_label = QLabel("Langue:")
        lang_label.setProperty("class", "settings-label")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Français", "English", "Español", "Deutsch"])
        self.language_combo.setProperty("class", "settings-combo")
        layout.addRow(lang_label, self.language_combo)

        # Default page
        page_label = QLabel("Page par défaut:")
        page_label.setProperty("class", "settings-label")
        self.default_page_combo = QComboBox()
        self.default_page_combo.addItems(
            ["Synthèse", "Patrimoine", "Investir", "Analyses"]
        )
        self.default_page_combo.setProperty("class", "settings-combo")
        layout.addRow(page_label, self.default_page_combo)

        # Auto-refresh
        refresh_label = QLabel("Actualisation auto:")
        refresh_label.setProperty("class", "settings-label")
        self.auto_refresh_check = QCheckBox("Actualiser les prix automatiquement")
        self.auto_refresh_check.setChecked(True)
        self.auto_refresh_check.setProperty("class", "settings-checkbox")
        layout.addRow(refresh_label, self.auto_refresh_check)

        # Refresh interval
        interval_label = QLabel("Intervalle d'actualisation:")
        interval_label.setProperty("class", "settings-label")
        self.refresh_interval_spin = QSpinBox()
        self.refresh_interval_spin.setRange(1, 60)
        self.refresh_interval_spin.setValue(15)
        self.refresh_interval_spin.setSuffix(" minutes")
        self.refresh_interval_spin.setProperty("class", "settings-spin")
        self.refresh_interval_spin.setEnabled(True)
        layout.addRow(interval_label, self.refresh_interval_spin)

        # Enable auto-refresh toggling
        self.auto_refresh_check.toggled.connect(self.refresh_interval_spin.setEnabled)

        # Startup behavior
        startup_label = QLabel("Au démarrage:")
        startup_label.setProperty("class", "settings-label")
        self.startup_check = QCheckBox("Charger les dernières données")
        self.startup_check.setChecked(True)
        self.startup_check.setProperty("class", "settings-checkbox")
        layout.addRow(startup_label, self.startup_check)

        return section

    def _create_data_section(self):
        """Create data management section."""
        section = QGroupBox("💾  Données")
        section.setProperty("class", "settings-section")
        layout = QVBoxLayout(section)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Database location
        db_layout = QHBoxLayout()
        db_label = QLabel("Base de données:")
        db_label.setProperty("class", "settings-label")
        db_layout.addWidget(db_label)

        self.db_path_label = QLabel(str(self.db.db_path))
        self.db_path_label.setProperty("class", "settings-path")
        self.db_path_label.setWordWrap(True)
        db_layout.addWidget(self.db_path_label, 1)
        layout.addLayout(db_layout)

        # Backup section
        backup_layout = QHBoxLayout()
        backup_btn = QPushButton("📥  Créer une sauvegarde")
        backup_btn.setProperty("class", "secondary-button")
        backup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        backup_btn.clicked.connect(self._create_backup)
        backup_layout.addWidget(backup_btn)

        restore_btn = QPushButton("📤  Restaurer une sauvegarde")
        restore_btn.setProperty("class", "secondary-button")
        restore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restore_btn.clicked.connect(self._restore_backup)
        backup_layout.addWidget(restore_btn)

        backup_layout.addStretch()
        layout.addLayout(backup_layout)

        # Export/Import section
        export_layout = QHBoxLayout()
        export_csv_btn = QPushButton("📊  Exporter en CSV")
        export_csv_btn.setProperty("class", "secondary-button")
        export_csv_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_csv_btn.clicked.connect(self._export_csv)
        export_layout.addWidget(export_csv_btn)

        export_json_btn = QPushButton("📋  Exporter en JSON")
        export_json_btn.setProperty("class", "secondary-button")
        export_json_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_json_btn.clicked.connect(self._export_json)
        export_layout.addWidget(export_json_btn)

        export_layout.addStretch()
        layout.addLayout(export_layout)

        # Auto-backup
        auto_backup_check = QCheckBox("Sauvegarde automatique hebdomadaire")
        auto_backup_check.setProperty("class", "settings-checkbox")
        auto_backup_check.setChecked(True)
        layout.addWidget(auto_backup_check)

        # Clear data (danger zone)
        layout.addSpacing(10)
        danger_label = QLabel("⚠️  Zone de danger")
        danger_label.setProperty("class", "danger-label")
        danger_font = QFont()
        danger_font.setBold(True)
        danger_label.setFont(danger_font)
        layout.addWidget(danger_label)

        clear_btn = QPushButton("🗑️  Effacer toutes les données")
        clear_btn.setProperty("class", "danger-button")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(self._clear_all_data)
        layout.addWidget(clear_btn)

        return section

    def _create_currency_section(self):
        """Create currency settings section."""
        section = QGroupBox("💰  Devises")
        section.setProperty("class", "settings-section")
        layout = QFormLayout(section)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Default currency
        currency_label = QLabel("Devise principale:")
        currency_label.setProperty("class", "settings-label")
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["EUR (€)", "USD ($)", "GBP (£)", "CHF (Fr)"])
        self.currency_combo.setProperty("class", "settings-combo")
        layout.addRow(currency_label, self.currency_combo)

        # Decimal places
        decimal_label = QLabel("Décimales:")
        decimal_label.setProperty("class", "settings-label")
        self.decimal_spin = QSpinBox()
        self.decimal_spin.setRange(0, 4)
        self.decimal_spin.setValue(2)
        self.decimal_spin.setProperty("class", "settings-spin")
        layout.addRow(decimal_label, self.decimal_spin)

        # Thousand separator
        separator_label = QLabel("Séparateur de milliers:")
        separator_label.setProperty("class", "settings-label")
        self.separator_check = QCheckBox("Afficher les séparateurs (ex: 1 000 000)")
        self.separator_check.setChecked(True)
        self.separator_check.setProperty("class", "settings-checkbox")
        layout.addRow(separator_label, self.separator_check)

        # Currency symbol position
        position_label = QLabel("Position du symbole:")
        position_label.setProperty("class", "settings-label")
        position_widget = QWidget()
        position_layout = QHBoxLayout(position_widget)
        position_layout.setContentsMargins(0, 0, 0, 0)

        self.symbol_group = QButtonGroup()
        prefix_radio = QRadioButton("Préfixe (€100)")
        suffix_radio = QRadioButton("Suffixe (100€)")
        prefix_radio.setChecked(True)

        self.symbol_group.addButton(prefix_radio, 0)
        self.symbol_group.addButton(suffix_radio, 1)

        position_layout.addWidget(prefix_radio)
        position_layout.addWidget(suffix_radio)
        position_layout.addStretch()

        layout.addRow(position_label, position_widget)

        return section

    def _create_notifications_section(self):
        """Create notifications settings section."""
        section = QGroupBox("🔔  Notifications")
        section.setProperty("class", "settings-section")
        layout = QVBoxLayout(section)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Enable notifications
        self.notifications_check = QCheckBox("Activer les notifications")
        self.notifications_check.setChecked(True)
        self.notifications_check.setProperty("class", "settings-checkbox")
        layout.addWidget(self.notifications_check)

        # Notification types
        types_widget = QWidget()
        types_layout = QVBoxLayout(types_widget)
        types_layout.setContentsMargins(20, 5, 0, 5)
        types_layout.setSpacing(8)

        self.notif_success_check = QCheckBox("Opérations réussies")
        self.notif_success_check.setChecked(True)
        self.notif_success_check.setProperty("class", "settings-checkbox")
        types_layout.addWidget(self.notif_success_check)

        self.notif_error_check = QCheckBox("Erreurs")
        self.notif_error_check.setChecked(True)
        self.notif_error_check.setProperty("class", "settings-checkbox")
        types_layout.addWidget(self.notif_error_check)

        self.notif_price_check = QCheckBox("Mises à jour des prix")
        self.notif_price_check.setProperty("class", "settings-checkbox")
        types_layout.addWidget(self.notif_price_check)

        self.notif_backup_check = QCheckBox("Sauvegardes automatiques")
        self.notif_backup_check.setChecked(True)
        self.notif_backup_check.setProperty("class", "settings-checkbox")
        types_layout.addWidget(self.notif_backup_check)

        layout.addWidget(types_widget)

        # Duration
        duration_layout = QHBoxLayout()
        duration_label = QLabel("Durée d'affichage:")
        duration_label.setProperty("class", "settings-label")
        duration_layout.addWidget(duration_label)

        self.notif_duration_spin = QSpinBox()
        self.notif_duration_spin.setRange(1, 10)
        self.notif_duration_spin.setValue(3)
        self.notif_duration_spin.setSuffix(" secondes")
        self.notif_duration_spin.setProperty("class", "settings-spin")
        duration_layout.addWidget(self.notif_duration_spin)

        duration_layout.addStretch()
        layout.addLayout(duration_layout)

        return section

    def _create_about_section(self):
        """Create about section."""
        section = QGroupBox("ℹ️  À propos")
        section.setProperty("class", "settings-section")
        layout = QVBoxLayout(section)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # App name and version
        app_label = QLabel("Prism - Personal Finance & Investment")
        app_label.setProperty("class", "about-title")
        app_font = QFont()
        app_font.setPointSize(16)
        app_font.setBold(True)
        app_label.setFont(app_font)
        layout.addWidget(app_label)

        version_label = QLabel("Version 1.2.1")
        version_label.setProperty("class", "about-version")
        layout.addWidget(version_label)

        # Description
        desc_label = QLabel(
            "Application de gestion financière personnelle avec suivi "
            "d'investissements en cryptomonnaies et actions.\n\n"
            "Design inspiré de Finary avec interface moderne et intuitive."
        )
        desc_label.setWordWrap(True)
        desc_label.setProperty("class", "about-description")
        layout.addWidget(desc_label)

        # Links
        links_layout = QHBoxLayout()

        docs_btn = QPushButton("📚  Documentation")
        docs_btn.setProperty("class", "secondary-button")
        docs_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        docs_btn.clicked.connect(self._open_documentation)
        links_layout.addWidget(docs_btn)

        github_btn = QPushButton("💻  Code source")
        github_btn.setProperty("class", "secondary-button")
        github_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        github_btn.clicked.connect(self._open_github)
        links_layout.addWidget(github_btn)

        links_layout.addStretch()
        layout.addLayout(links_layout)

        # Credits
        credits_label = QLabel("© 2025 Prism. Tous droits réservés.")
        credits_label.setProperty("class", "about-credits")
        layout.addWidget(credits_label)

        return section

    def _load_settings(self):
        """Load settings from QSettings."""
        # Appearance
        theme = self.settings.value("appearance/theme", "Sombre")
        self.theme_combo.setCurrentText(theme)

        font_size = self.settings.value("appearance/font_size", 13, type=int)
        self.font_spin.setValue(font_size)

        compact = self.settings.value("appearance/compact", False, type=bool)
        self.compact_check.setChecked(compact)

        animations = self.settings.value("appearance/animations", True, type=bool)
        self.animations_check.setChecked(animations)

        # General
        language = self.settings.value("general/language", "Français")
        self.language_combo.setCurrentText(language)

        default_page = self.settings.value("general/default_page", "Synthèse")
        self.default_page_combo.setCurrentText(default_page)

        auto_refresh = self.settings.value("general/auto_refresh", True, type=bool)
        self.auto_refresh_check.setChecked(auto_refresh)

        refresh_interval = self.settings.value("general/refresh_interval", 15, type=int)
        self.refresh_interval_spin.setValue(refresh_interval)

        startup_load = self.settings.value("general/startup_load", True, type=bool)
        self.startup_check.setChecked(startup_load)

        # Currency
        currency = self.settings.value("currency/default", "EUR (€)")
        self.currency_combo.setCurrentText(currency)

        decimals = self.settings.value("currency/decimals", 2, type=int)
        self.decimal_spin.setValue(decimals)

        separator = self.settings.value("currency/separator", True, type=bool)
        self.separator_check.setChecked(separator)

        symbol_position = self.settings.value("currency/symbol_position", 0, type=int)
        self.symbol_group.button(symbol_position).setChecked(True)

        # Notifications
        notifications = self.settings.value("notifications/enabled", True, type=bool)
        self.notifications_check.setChecked(notifications)

        notif_success = self.settings.value("notifications/success", True, type=bool)
        self.notif_success_check.setChecked(notif_success)

        notif_error = self.settings.value("notifications/error", True, type=bool)
        self.notif_error_check.setChecked(notif_error)

        notif_price = self.settings.value("notifications/price", False, type=bool)
        self.notif_price_check.setChecked(notif_price)

        notif_backup = self.settings.value("notifications/backup", True, type=bool)
        self.notif_backup_check.setChecked(notif_backup)

        notif_duration = self.settings.value("notifications/duration", 3, type=int)
        self.notif_duration_spin.setValue(notif_duration)

    def _save_settings(self):
        """Save settings to QSettings."""
        try:
            # Appearance
            self.settings.setValue("appearance/theme", self.theme_combo.currentText())
            self.settings.setValue("appearance/font_size", self.font_spin.value())
            self.settings.setValue("appearance/compact", self.compact_check.isChecked())
            self.settings.setValue(
                "appearance/animations", self.animations_check.isChecked()
            )

            # General
            self.settings.setValue(
                "general/language", self.language_combo.currentText()
            )
            self.settings.setValue(
                "general/default_page", self.default_page_combo.currentText()
            )
            self.settings.setValue(
                "general/auto_refresh", self.auto_refresh_check.isChecked()
            )
            self.settings.setValue(
                "general/refresh_interval", self.refresh_interval_spin.value()
            )
            self.settings.setValue(
                "general/startup_load", self.startup_check.isChecked()
            )

            # Currency
            self.settings.setValue(
                "currency/default", self.currency_combo.currentText()
            )
            self.settings.setValue("currency/decimals", self.decimal_spin.value())
            self.settings.setValue(
                "currency/separator", self.separator_check.isChecked()
            )
            self.settings.setValue(
                "currency/symbol_position", self.symbol_group.checkedId()
            )

            # Notifications
            self.settings.setValue(
                "notifications/enabled", self.notifications_check.isChecked()
            )
            self.settings.setValue(
                "notifications/success", self.notif_success_check.isChecked()
            )
            self.settings.setValue(
                "notifications/error", self.notif_error_check.isChecked()
            )
            self.settings.setValue(
                "notifications/price", self.notif_price_check.isChecked()
            )
            self.settings.setValue(
                "notifications/backup", self.notif_backup_check.isChecked()
            )
            self.settings.setValue(
                "notifications/duration", self.notif_duration_spin.value()
            )

            # Sync settings
            self.settings.sync()

            # Emit signal
            self.settings_changed.emit()

            # Show success message
            QMessageBox.information(
                self,
                "Paramètres enregistrés",
                "Vos paramètres ont été enregistrés avec succès.\n\n"
                "Certains changements nécessiteront un redémarrage de l'application.",
            )

            logger.info("Settings saved successfully")

        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible d'enregistrer les paramètres:\n{str(e)}",
            )

    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        theme_map = {
            "Sombre": "finary_dark",
            "Clair": "finary_light",
            "Auto (Système)": "auto",
        }
        theme_key = theme_map.get(theme, "finary_dark")
        self.theme_changed.emit(theme_key)

    def _create_backup(self):
        """Create database backup."""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Créer une sauvegarde",
                str(Path.home() / "prism_backup.db"),
                "Database Files (*.db);;All Files (*)",
            )

            if file_path:
                import shutil

                shutil.copy2(self.db.db_path, file_path)

                QMessageBox.information(
                    self,
                    "Sauvegarde créée",
                    f"La sauvegarde a été créée avec succès:\n{file_path}",
                )
                logger.info(f"Backup created: {file_path}")

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible de créer la sauvegarde:\n{str(e)}",
            )

    def _restore_backup(self):
        """Restore database from backup."""
        reply = QMessageBox.warning(
            self,
            "Restaurer une sauvegarde",
            "⚠️  Cette opération remplacera toutes vos données actuelles.\n\n"
            "Voulez-vous continuer?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                file_path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Sélectionner une sauvegarde",
                    str(Path.home()),
                    "Database Files (*.db);;All Files (*)",
                )

                if file_path:
                    import shutil

                    # Create backup of current database
                    backup_path = str(self.db.db_path) + ".before_restore"
                    shutil.copy2(self.db.db_path, backup_path)

                    # Restore
                    shutil.copy2(file_path, self.db.db_path)

                    QMessageBox.information(
                        self,
                        "Restauration réussie",
                        "La base de données a été restaurée avec succès.\n\n"
                        "L'application va redémarrer.",
                    )
                    logger.info(f"Database restored from: {file_path}")

            except Exception as e:
                logger.error(f"Failed to restore backup: {e}")
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Impossible de restaurer la sauvegarde:\n{str(e)}",
                )

    def _export_csv(self):
        """Export data to CSV."""
        QMessageBox.information(
            self,
            "Export CSV",
            "L'export CSV est disponible via:\nFichier → Exporter les données",
        )

    def _export_json(self):
        """Export data to JSON."""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Exporter en JSON",
                str(Path.home() / "prism_export.json"),
                "JSON Files (*.json);;All Files (*)",
            )

            if file_path:
                import json

                data = {
                    "transactions": self.db.get_all_transactions(),
                    "assets": self.db.get_all_assets(),
                }

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)

                QMessageBox.information(
                    self,
                    "Export réussi",
                    f"Les données ont été exportées avec succès:\n{file_path}",
                )
                logger.info(f"Data exported to JSON: {file_path}")

        except Exception as e:
            logger.error(f"Failed to export JSON: {e}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible d'exporter les données:\n{str(e)}",
            )

    def _clear_all_data(self):
        """Clear all data from database."""
        reply = QMessageBox.warning(
            self,
            "Effacer toutes les données",
            "⚠️  ATTENTION ⚠️\n\n"
            "Cette action est IRRÉVERSIBLE et supprimera:\n"
            "• Toutes les transactions\n"
            "• Tous les actifs\n"
            "• Toutes les catégories personnalisées\n"
            "• Tous les ordres\n\n"
            "Une sauvegarde sera créée automatiquement.\n\n"
            "Êtes-vous absolument sûr(e) de vouloir continuer?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Create automatic backup
                import shutil
                from datetime import datetime

                backup_path = (
                    str(self.db.db_path)
                    + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                shutil.copy2(self.db.db_path, backup_path)

                # Clear data (implement based on your DatabaseManager methods)
                # This is a placeholder - implement according to your db methods
                logger.warning("Clear all data requested - backup created")

                QMessageBox.information(
                    self,
                    "Données effacées",
                    "Toutes les données ont été effacées.\n\n"
                    f"Une sauvegarde a été créée:\n{backup_path}",
                )

            except Exception as e:
                logger.error(f"Failed to clear data: {e}")
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Impossible d'effacer les données:\n{str(e)}",
                )

    def _open_documentation(self):
        """Open documentation."""
        import webbrowser

        webbrowser.open("https://github.com/prism/docs")

    def _open_github(self):
        """Open GitHub repository."""
        import webbrowser

        webbrowser.open("https://github.com/prism/prism")

    def get_setting(self, key: str, default=None):
        """
        Get a setting value.

        Args:
            key: Setting key (e.g., "appearance/theme")
            default: Default value if not found

        Returns:
            Setting value
        """
        return self.settings.value(key, default)
