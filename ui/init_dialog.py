# [file name]: ui/init_dialog.py
import os
import json
import yaml
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QGridLayout, QFileDialog, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, Signal

from config.i18n import i18n

class InitDialog(QWidget):
    sig_done = Signal(str, list, str)  # api_key, mcp_files, config_file
    
    def __init__(self):
        super().__init__()
        
        self.DS_API_KEY = ""
        self.mcp_files = []
        self.config_file = ""
        
        self.setWindowTitle(i18n.tr("initial_setup"))
        self.resize(600, 350)
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title
        title_label = QLabel(i18n.tr("setup_title"))
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4a9cff;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(i18n.tr("setup_desc"))
        desc_label.setStyleSheet("color: #a0a0a0;")
        desc_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(desc_label)
        
        main_layout.addSpacing(20)
        
        # Configuration container
        config_container = QWidget()
        config_layout = QGridLayout(config_container)
        config_layout.setContentsMargins(0, 0, 0, 0)
        config_layout.setSpacing(12)
        
        # API source selection
        config_layout.addWidget(QLabel("API Provider:"), 0, 0, Qt.AlignRight)
        self.api_source_combo = QComboBox()
        self.api_source_combo.addItems(["DeepSeek", "OpenAI", "Anthropic", "Local", "Custom"])
        self.api_source_combo.currentTextChanged.connect(self.on_api_source_changed)
        config_layout.addWidget(self.api_source_combo, 0, 1)
        
        # API base URL
        config_layout.addWidget(QLabel("API Base URL:"), 1, 0, Qt.AlignRight)
        self.api_base_edit = QLineEdit()
        self.api_base_edit.setPlaceholderText("https://api.deepseek.com")
        self.api_base_edit.setText("https://api.deepseek.com")
        config_layout.addWidget(self.api_base_edit, 1, 1)
        
        # Model selection
        config_layout.addWidget(QLabel("Model:"), 2, 0, Qt.AlignRight)
        self.model_combo = QComboBox()
        self.model_combo.addItems(["deepseek-chat", "gpt-4-turbo", "claude-3-opus", "custom"])
        config_layout.addWidget(self.model_combo, 2, 1)
        
        # API key
        config_layout.addWidget(QLabel("API Key:"), 3, 0, Qt.AlignRight)
        self.api_key_line_edit = QLineEdit()
        self.api_key_line_edit.setPlaceholderText("Enter API key (sk-xxx...) or use config file")
        config_layout.addWidget(self.api_key_line_edit, 3, 1)
        
        # Config file selection
        config_layout.addWidget(QLabel("Config File:"), 4, 0, Qt.AlignRight)
        self.config_file_display = QLabel("No config file selected")
        self.config_file_display.setWordWrap(True)
        self.config_file_display.setStyleSheet("background-color: #252525; padding: 8px; border-radius: 4px;")
        config_layout.addWidget(self.config_file_display, 4, 1)
        
        main_layout.addWidget(config_container)
        
        # Button container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        
        select_config_button = QPushButton(i18n.tr("load_config_file"))
        select_config_button.clicked.connect(self.load_config_file)
        
        select_files_button = QPushButton(i18n.tr("select_mcp_files"))
        select_files_button.clicked.connect(self.read_mcp_files)
        
        done_button = QPushButton(i18n.tr("start_lynexus"))
        done_button.clicked.connect(self.close_dialog)
        done_button.setStyleSheet("background-color: #4a9cff; color: white; font-weight: bold;")
        
        button_layout.addWidget(select_config_button)
        button_layout.addWidget(select_files_button)
        button_layout.addStretch()
        button_layout.addWidget(done_button)
        
        main_layout.addWidget(button_container)
        main_layout.addStretch()
        
        # Set shortcut
        done_button.setShortcut('return')
    
    def on_api_source_changed(self, source):
        """根据选择的API提供商更新默认值"""
        defaults = {
            "DeepSeek": ("https://api.deepseek.com", "deepseek-chat"),
            "OpenAI": ("https://api.openai.com/v1", "gpt-4-turbo"),
            "Anthropic": ("https://api.anthropic.com", "claude-3-opus-20240229"),
            "Local": ("http://localhost:11434", "llama2"),
            "Custom": ("", "custom")
        }
        
        if source in defaults:
            api_base, model = defaults[source]
            self.api_base_edit.setText(api_base)
            if model in [self.model_combo.itemText(i) for i in range(self.model_combo.count())]:
                self.model_combo.setCurrentText(model)
    
    def close_dialog(self):
        """关闭对话框并发出信号"""
        self.DS_API_KEY = self.api_key_line_edit.text()
        config_data = {
            "api_key": self.DS_API_KEY,
            "api_base": self.api_base_edit.text(),
            "model": self.model_combo.currentText(),
            "mcp_paths": self.mcp_files
        }
        
        # 如果有数据则保存配置
        if self.DS_API_KEY or self.mcp_files:
            from utils.config_manager import ConfigManager
            config_manager = ConfigManager()
            if self.DS_API_KEY:
                config_manager.save_api_key(self.DS_API_KEY)
            
            # 保存非敏感配置
            config_path = "configs/last_config.json"
            os.makedirs("configs", exist_ok=True)
            safe_config = config_data.copy()
            del safe_config['api_key']
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(safe_config, f, indent=2)
        
        self.sig_done.emit(self.DS_API_KEY, self.mcp_files, self.config_file)
        self.close()
    
    def read_mcp_files(self):
        """打开文件对话框选择MCP文件"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle(i18n.tr("select_mcp_files"))
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        selected_files, _ = file_dialog.getOpenFileNames(
            self, "Select Files", "", 
            "All Supported (*.py *.json *.yaml *.yml);;Python Files (*.py);;JSON Files (*.json);;YAML Files (*.yaml *.yml)"
        )
        if selected_files:
            self.mcp_files = selected_files
            self.config_file_display.setText(f"MCP Files: {len(selected_files)} selected")
    
    def load_config_file(self):
        """从文件加载配置"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Load Configuration File")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        selected_files, _ = file_dialog.getOpenFileNames(
            self, "Select Config", "", 
            "Config Files (*.json *.yaml *.yml);;All Files (*.*)"
        )
        if selected_files:
            self.config_file = selected_files[0]
            self.config_file_display.setText(f"Config: {os.path.basename(self.config_file)}")
            
            # 加载并应用配置
            try:
                if self.config_file.endswith('.json'):
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                elif self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                
                # 将配置应用到UI
                if 'api_key' in config:
                    self.api_key_line_edit.setText(config['api_key'])
                if 'api_base' in config:
                    self.api_base_edit.setText(config['api_base'])
                if 'model' in config:
                    self.model_combo.setCurrentText(config['model'])
                if 'mcp_paths' in config:
                    self.mcp_files = config['mcp_paths']
                    self.config_file_display.setText(
                        f"Config: {os.path.basename(self.config_file)} | MCP: {len(self.mcp_files)} files"
                    )
            except Exception as e:
                QMessageBox.warning(self, "Load Error", f"Failed to load config: {e}")