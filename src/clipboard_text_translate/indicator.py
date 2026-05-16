#!/usr/bin/python3

from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel, QScrollArea, QPushButton, QTextEdit, QDialog, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QPixmap, QDesktopServices
from PyQt5.QtCore import QStandardPaths, Qt,QUrl

import sys
import json
import signal
import platform
import os


from clipboard_text_translate.desktop import create_desktop_file
from clipboard_text_translate.desktop import create_desktop_directory
from clipboard_text_translate.desktop import create_desktop_menu
from clipboard_text_translate.modules.wabout import show_about_window
from clipboard_text_translate.modules.resources import resource_path
import clipboard_text_translate.modules.lib_files as lib_files
import clipboard_text_translate.modules.lib_translate as lib_translate
import clipboard_text_translate.about as about


CONFIG_PATH = os.path.join( os.path.expanduser("~"),
                            ".config", 
                            about.__package__, 
                            "config.json" )
                            
config_file_path = os.path.expanduser(CONFIG_PATH)
config_data = {
    "GoogleTranslateLauncher": {
        "To english": "en",
        "To spanish": "es",
        "To portuguese": "pt"
    },
    "RawTranslateLauncher": {
        "To english": "en",
        "To spanish": "es",
        "To portuguese": "pt"
    }
    
}


try:
    if not os.path.exists(config_file_path):
        os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
        
        with open(config_file_path, "w", encoding="utf-8") as arquivo:
            json.dump(config_data, arquivo, indent=4)
        print(f"Arquivo criado em: {config_file_path}")
        
    with open(config_file_path, "r") as arquivo:
        config_data = json.load(arquivo)
    
except FileNotFoundError:
    print(f"Erro: O arquivo '{config_file_path}' não foi encontrado.")
    sys.exit()
    
except json.JSONDecodeError:
    print(f"Erro: O arquivo '{config_file_path}' não contém um JSON válido.")
    sys.exit()

################################################################################
################################################################################
################################################################################


def show_notification_message(title, message):
    """Show a system notification"""
    if platform.system() == "Linux":
        os.system(f'notify-send "⚠️ {title} ⚠️" "{message}"')
    else:
        app = QApplication.instance()
        tray_icon = app.property("tray_icon")
        if tray_icon:
            tray_icon.showMessage("⚠️ " + title + " ⚠️", message, QSystemTrayIcon.Information, 3000)

class MessageDialog(QDialog):
    """Display a message with copyable text and an OK button"""
    def __init__(self, message, width=600, height=300, parent=None, read_only=False, title="Message"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(width, height)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create text view for displaying the message
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(message)
        self.text_edit.setReadOnly(read_only)
        self.text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        
        # Add text view to a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.text_edit)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Copy to clipboard Button
        copy_button = QPushButton("Copy to clipboard")
        copy_button.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(copy_button)
        
        # OK Button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

    def copy_to_clipboard(self):
        """Copy the text from the text edit to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())

def show_message(message, width=600, height=300):
    dialog = MessageDialog(message, width, height)
    dialog.exec_()

def get_clipboard_text():
    """Get text from clipboard"""
    app = QApplication.instance()
    clipboard = app.clipboard()
    return clipboard.text()

def edit_config():
    lib_files.open_from_filepath(config_file_path)

def open_url_help():
    url = "https://github.com/trucomanx/ClipboardTextTranslate/blob/main/doc/README.md"
    show_notification_message("open_url_help", url)
    QDesktopServices.openUrl(QUrl(url))

def on_action_googletranslate(lang_code):
    text = get_clipboard_text()
    show_notification_message("Going to Google Translate", "Open in the default web browser")
    translated_link = lib_translate.generate_google_translate_link(text, target_lang=lang_code)
    
    QDesktopServices.openUrl(QUrl(translated_link))

def on_action_rawtranslate(lang_code):
    text = get_clipboard_text()
    show_notification_message("Translating", "Please wait")
    res = lib_translate.translate_text_sync(text, target_lang=lang_code)
    show_message(res)

def open_coffee_link():
    show_notification_message("Buy me a coffee", "https://ko-fi.com/trucomanx")
    QDesktopServices.openUrl(QUrl("https://ko-fi.com/trucomanx"))

def show_about():
    data = {
        "version": about.__version__,
        "package": about.__package__,
        "program_name": about.__linux_indicator__,
        "author": about.__author__,
        "email": about.__email__,
        "description": about.__description__,
        "url_source": about.__url_source__,
        "url_funding": about.__url_funding__,
        "url_doc": about.__url_doc__,
        "url_bugs": about.__url_bugs__
    }
    
    icon_path = resource_path('icons', 'logo.png')
    
    show_about_window(data, icon_path)

class ClipboardTextTranslate(QApplication):
    def __init__(self, argv):
        self.app = QApplication(sys.argv)
        self.setQuitOnLastWindowClosed(False)
        
        
        # Get base directory for icons
        self.icon_path = resource_path('icons', 'logo.png')
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(QIcon(self.icon_path))
        self.tray_icon.setToolTip("Clipboard Text Translate")

        # Menu
        self.menu = QMenu()
                
        # Criar submenu para traduções
        self.translate_menu = QMenu("📋 Google Translate launcher", self.menu)

        translate_data = config_data.get("GoogleTranslateLauncher", {})        
        for label, lang_code in translate_data.items():
            # Translate with google
            action = QAction("\t"+label, self.menu)
            action.setIcon(QIcon.fromTheme("emblem-default"))
            action.triggered.connect(lambda checked, code=lang_code: on_action_googletranslate(code))
            self.translate_menu.addAction(action)
        
        self.menu.addMenu(self.translate_menu)

        # Separator
        self.menu.addSeparator()
        
        # Criar submenu para traduções
        self.raw_translate_menu = QMenu("📋 Translate raw text", self.menu)
        
        raw_translate_data = config_data.get("RawTranslateLauncher", {})
        for label, lang_code in raw_translate_data.items():
            # Translate with google
            action = QAction("\t"+label, self.menu)
            action.setIcon(QIcon.fromTheme("emblem-default"))
            action.triggered.connect(lambda checked, code=lang_code: on_action_rawtranslate(code))
            self.raw_translate_menu.addAction(action)
        
        self.menu.addMenu(self.raw_translate_menu)
                
        # Separator
        self.menu.addSeparator()
               
        # Create program_information_submenu
        self.program_info_submenu = QMenu("🛠️ Program usage information")
        
        
        # Add actions to program_information_submenu
        edit_config_action = QAction("\tOpen config file", self.menu)
        edit_config_action.setIcon(QIcon.fromTheme("applications-utilities"))
        edit_config_action.triggered.connect(edit_config)
        self.program_info_submenu.addAction(edit_config_action)
        
        # Add heelp
        url_help_action = QAction("\tOpen url help", self.menu)
        url_help_action.setIcon(QIcon.fromTheme("help-contents"))
        url_help_action.triggered.connect(open_url_help)
        self.program_info_submenu.addAction(url_help_action)
        
        # Add program_information_submenu to main menu
        self.menu.addMenu(self.program_info_submenu)
        
        # Separator
        self.menu.addSeparator()
        
        
        # Coffee
        coffee_action = QAction("☕ Buy me a coffee", self.menu)
        coffee_action.setIcon(QIcon.fromTheme("emblem-favorite"))
        coffee_action.triggered.connect(open_coffee_link)
        self.menu.addAction(coffee_action)
        
        # About
        about_action = QAction("🌟 About", self.menu)
        about_action.setIcon(QIcon.fromTheme("help-about"))
        about_action.triggered.connect(show_about)
        self.menu.addAction(about_action)
        
        # Separator
        self.menu.addSeparator()

        # Exit        
        exit_action = QAction("❌ Exit", self.menu)
        exit_action.setIcon(QIcon.fromTheme("application-exit"))
        exit_action.triggered.connect(self.app.quit)
        self.menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()



def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    create_desktop_directory()    
    create_desktop_menu()
    create_desktop_file('~/.local/share/applications')
    
    for n in range(len(sys.argv)):
        if sys.argv[n] == "--autostart":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file('~/.config/autostart', overwrite=True)
            return
        if sys.argv[n] == "--applications":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file('~/.local/share/applications', overwrite=True)
            return
    
    app = ClipboardTextTranslate(sys.argv)
    app.setApplicationName(about.__package__) # xprop WM_CLASS # *.desktop -> StartupWMClass  
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

