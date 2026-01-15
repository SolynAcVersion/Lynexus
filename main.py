# [file name]: main.py
"""
Main entry point for Lynexus AI Assistant application.
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLocale

from ui.chat_box import ChatBox
from ui.styles import get_modern_style
from config.i18n import i18n

def main():
    """Main application entry point."""
    # Create application instance
    app = QApplication(sys.argv)
    app.setApplicationName("Lynexus")
    app.setOrganizationName("Lynexus")
    
    # Apply modern style
    app.setStyleSheet(get_modern_style())
    
    # Set language based on system locale
    system_language = QLocale.system().name()[:2]
    if system_language in i18n.get_supported_languages():
        i18n.set_language(system_language)
    else:
        i18n.set_language("en")  # Default to English
    
    # Create and show main window
    try:
        chat_box = ChatBox()
        chat_box.show()
        
        # Run application event loop
        return_code = app.exec()
        
        # Clean up
        sys.exit(return_code)
        
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()