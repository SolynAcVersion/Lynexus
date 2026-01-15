# [file name]: ui/styles.py
"""
Style definitions for the application with enhanced splitter styles.
"""

def get_modern_style():
    """Get modern application stylesheet with enhanced splitter visibility."""
    return """
    QWidget {
        font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
    }
    
    QMainWindow {
        background-color: #1e1e1e;
    }
    
    QPushButton {
        background-color: #2d2d2d;
        border: 1px solid #3e3e3e;
        border-radius: 4px;
        color: #e0e0e0;
        padding: 6px 12px;
        font-weight: 500;
    }
    
    QPushButton:hover {
        background-color: #3d3d3d;
        border-color: #4a9cff;
    }
    
    QPushButton:pressed {
        background-color: #1a1a1a;
    }
    
    QPushButton:disabled {
        background-color: #2a2a2a;
        color: #666;
    }
    
    QLineEdit, QTextEdit {
        background-color: #252525;
        border: 1px solid #3e3e3e;
        border-radius: 4px;
        color: #e0e0e0;
        padding: 6px;
        selection-background-color: #4a9cff;
    }
    
    QLineEdit:focus, QTextEdit:focus {
        border-color: #4a9cff;
    }
    
    /* Enhanced splitter styles for better visibility */
    QSplitter::handle {
        background-color: #4a4a4a;
        border: 1px solid #3e3e3e;
    }
    
    QSplitter::handle:horizontal {
        width: 8px;
    }
    
    QSplitter::handle:vertical {
        height: 8px;
    }
    
    QSplitter::handle:hover {
        background-color: #5a5a5a;
    }
    
    QSplitter::handle:pressed {
        background-color: #6a6a6a;
    }
    
    /* Rest of the styles remain the same... */
    QGroupBox {
        font-weight: bold;
        border: 1px solid #3e3e3e;
        border-radius: 6px;
        margin-top: 12px;
        padding-top: 12px;
        color: #e0e0e0;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 8px 0 8px;
    }
    
    QLabel {
        color: #d0d0d0;
    }
    
    QScrollArea {
        border: none;
        background-color: transparent;
    }
    
    QScrollBar:vertical {
        border: none;
        background-color: #2a2a2a;
        width: 10px;
        margin: 0px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #4a4a4a;
        border-radius: 5px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #5a5a5a;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QListWidget {
        background-color: #252525;
        border: 1px solid #3e3e3e;
        border-radius: 4px;
        color: #e0e0e0;
        padding: 4px;
    }
    
    QListWidget::item {
        padding: 8px;
        border-radius: 4px;
        margin: 2px;
    }
    
    QListWidget::item:selected {
        background-color: #4a9cff;
        color: white;
    }
    
    QListWidget::item:hover {
        background-color: #3a3a3a;
    }
    
    QComboBox {
        background-color: #252525;
        border: 1px solid #3e3e3e;
        border-radius: 4px;
        color: #e0e0e0;
        padding: 6px;
        min-width: 100px;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #252525;
        color: #e0e0e0;
        selection-background-color: #4a9cff;
        border: 1px solid #3e3e3e;
    }
    
    QSpinBox, QDoubleSpinBox {
        background-color: #252525;
        border: 1px solid #3e3e3e;
        border-radius: 4px;
        color: #e0e0e0;
        padding: 6px;
    }
    
    QCheckBox {
        color: #e0e0e0;
    }
    
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
    }
    
    QCheckBox::indicator:checked {
        background-color: #4a9cff;
        border: 2px solid #4a9cff;
    }
    
    QProgressDialog {
        background-color: #1e1e1e;
        color: #e0e0e0;
    }
    
    QMessageBox {
        background-color: #1e1e1e;
        color: #e0e0e0;
    }
    
    QMessageBox QLabel {
        color: #e0e0e0;
    }
    
    /* Status Bar */
    QStatusBar {
        background-color: #2d2d2d;
        border-top: 1px solid #3e3e3e;
        color: #e0e0e0;
        font-size: 12px;
        padding: 4px;
    }
    
    /* Message bubbles */
    QLabel#messageContent {
        background-color: transparent;
        color: white;
        font-size: 14px;
        line-height: 1.4;
    }
    """