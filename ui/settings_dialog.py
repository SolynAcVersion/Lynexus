# [file name]: ui/settings_dialog.py
"""
Settings Dialog - Enhanced version with existing AI instance update capability
Allows modifying settings of an existing AI instance without creating a new one
"""

import os
import json
import yaml
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QGridLayout, QFileDialog, QMessageBox, QComboBox,
    QGroupBox, QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox,
    QScrollArea
)
from PySide6.QtCore import Qt, Signal

from config.i18n import i18n
from utils.config_manager import ConfigManager

class SettingsDialog(QWidget):
    """
    Settings dialog that can update existing AI instances.
    Emits settings dictionary when saved, allowing the parent to update the AI instance.
    """
    
    sig_save_settings = Signal(dict)  # Signal to emit complete settings dictionary
    
    def __init__(self, ai_instance=None, current_config=None, conversation_name=""):
        super().__init__()
        self.ai = ai_instance  # Store reference to existing AI instance
        self.current_config = current_config or {}
        self.conversation_name = conversation_name
        self.mcp_paths = []  # Store MCP paths
        self.config_manager = ConfigManager()
        
        self.setWindowTitle(f"Lynexus - Settings ({conversation_name})")
        self.resize(700, 800)
        
        # Initialize UI components
        self.init_ui()
        
        # Load current settings from AI instance or config
        if self.ai:
            self.load_current_settings()
        elif self.current_config:
            self.load_from_config(self.current_config)
    
    def init_ui(self):
        """Initialize all UI components."""
        # Create scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title section
        title_label = QLabel(f"Settings for: {self.conversation_name}")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4a9cff; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # API Settings Group
        api_group = QGroupBox("API Configuration")
        api_layout = QGridLayout()
        api_layout.setSpacing(10)
        
        # API provider selection
        self.api_provider_combo = QComboBox()
        self.api_provider_combo.addItems(["DeepSeek", "OpenAI", "Anthropic", "Local", "Custom"])
        self.api_provider_combo.currentTextChanged.connect(self.on_api_provider_changed)
        
        # API key field with show/hide toggle
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        
        self.show_key_check = QCheckBox("Show")
        self.show_key_check.stateChanged.connect(self.toggle_show_key)
        
        # API base URL and model fields
        self.api_base_edit = QLineEdit()
        self.model_edit = QLineEdit()
        
        # Add API widgets to layout
        api_layout.addWidget(QLabel("Provider:"), 0, 0)
        api_layout.addWidget(self.api_provider_combo, 0, 1)
        api_layout.addWidget(QLabel("API Key:"), 1, 0)
        api_layout.addWidget(self.api_key_edit, 1, 1)
        api_layout.addWidget(self.show_key_check, 1, 2)
        api_layout.addWidget(QLabel("API Base:"), 2, 0)
        api_layout.addWidget(self.api_base_edit, 2, 1)
        api_layout.addWidget(QLabel("Model:"), 3, 0)
        api_layout.addWidget(self.model_edit, 3, 1)
        api_group.setLayout(api_layout)
        
        # Model Parameters Group
        model_group = QGroupBox("Model Parameters")
        model_layout = QGridLayout()
        model_layout.setSpacing(10)
        
        # Temperature control
        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.0, 2.0)
        self.temp_spin.setSingleStep(0.1)
        self.temp_spin.setValue(1.0)
        self.temp_spin.setToolTip("Higher values make output more random, lower values more deterministic")
        
        # Max tokens control - fix for None values
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(0, 100000)
        self.max_tokens_spin.setSpecialValueText("No limit (0)")
        self.max_tokens_spin.setValue(0)
        self.max_tokens_spin.setToolTip("Maximum number of tokens to generate (0 for no limit)")
        
        # Top-p control
        self.top_p_spin = QDoubleSpinBox()
        self.top_p_spin.setRange(0.0, 1.0)
        self.top_p_spin.setSingleStep(0.05)
        self.top_p_spin.setValue(1.0)
        self.top_p_spin.setToolTip("Nucleus sampling: higher values allow more diverse outputs")
        
        # Presence penalty control
        self.presence_spin = QDoubleSpinBox()
        self.presence_spin.setRange(-2.0, 2.0)
        self.presence_spin.setSingleStep(0.1)
        self.presence_spin.setValue(0.0)
        self.presence_spin.setToolTip("Positive values penalize new tokens based on whether they appear in the text so far")
        
        # Frequency penalty control
        self.frequency_spin = QDoubleSpinBox()
        self.frequency_spin.setRange(-2.0, 2.0)
        self.frequency_spin.setSingleStep(0.1)
        self.frequency_spin.setValue(0.0)
        self.frequency_spin.setToolTip("Positive values penalize new tokens based on their frequency in the text so far")
        
        # Add model widgets to layout
        model_layout.addWidget(QLabel("Temperature:"), 0, 0)
        model_layout.addWidget(self.temp_spin, 0, 1)
        model_layout.addWidget(QLabel("Max Tokens:"), 1, 0)
        model_layout.addWidget(self.max_tokens_spin, 1, 1)
        model_layout.addWidget(QLabel("Top P:"), 2, 0)
        model_layout.addWidget(self.top_p_spin, 2, 1)
        model_layout.addWidget(QLabel("Presence Penalty:"), 3, 0)
        model_layout.addWidget(self.presence_spin, 3, 1)
        model_layout.addWidget(QLabel("Frequency Penalty:"), 4, 0)
        model_layout.addWidget(self.frequency_spin, 4, 1)
        model_group.setLayout(model_layout)
        
        # Command Configuration Group
        command_group = QGroupBox("Command Configuration")
        command_layout = QGridLayout()
        command_layout.setSpacing(10)
        
        # Command start marker
        self.cmd_start_edit = QLineEdit()
        self.cmd_start_edit.setText("YLDEXECUTE:")
        self.cmd_start_edit.setToolTip("Marker that indicates a command execution request")
        
        # Command separator
        self.cmd_separator_edit = QLineEdit()
        self.cmd_separator_edit.setText("￥|")
        self.cmd_separator_edit.setToolTip("Separator between command and parameters")
        
        # Maximum iterations
        self.max_iter_spin = QSpinBox()
        self.max_iter_spin.setRange(1, 100)
        self.max_iter_spin.setValue(15)
        self.max_iter_spin.setToolTip("Maximum number of command execution iterations")
        
        # Add command widgets to layout
        command_layout.addWidget(QLabel("Command Start:"), 0, 0)
        command_layout.addWidget(self.cmd_start_edit, 0, 1)
        command_layout.addWidget(QLabel("Command Separator:"), 1, 0)
        command_layout.addWidget(self.cmd_separator_edit, 1, 1)
        command_layout.addWidget(QLabel("Max Iterations:"), 2, 0)
        command_layout.addWidget(self.max_iter_spin, 2, 1)
        command_group.setLayout(command_layout)
        
        # System Prompt Group
        prompt_group = QGroupBox("System Prompt")
        prompt_layout = QVBoxLayout()
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setMinimumHeight(150)
        self.prompt_edit.setAcceptRichText(False)
        self.prompt_edit.setToolTip("System prompt that guides the AI's behavior")
        prompt_layout.addWidget(self.prompt_edit)
        prompt_group.setLayout(prompt_layout)
        
        # MCP Tools Group
        tools_group = QGroupBox("MCP Tools")
        tools_layout = QVBoxLayout()
        self.mcp_files_label = QLabel("No MCP files loaded")
        self.mcp_files_label.setWordWrap(True)
        self.mcp_files_label.setStyleSheet("""
            background-color: #252525; 
            padding: 10px; 
            border-radius: 4px;
            color: #e0e0e0;
        """)
        
        # Add MCP files button
        add_tools_btn = QPushButton("Add MCP Files")
        add_tools_btn.clicked.connect(self.add_mcp_files)
        add_tools_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                color: #e0e0e0;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #4a9cff;
            }
        """)
        
        tools_layout.addWidget(self.mcp_files_label)
        tools_layout.addWidget(add_tools_btn)
        tools_group.setLayout(tools_layout)
        
        # Action Buttons Group
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        
        # Save Settings button - updates existing AI instance
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9cff; 
                color: white; 
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5aacff;
            }
        """)
        
        # Save As Config button - exports settings to file
        save_as_btn = QPushButton("Save As Config")
        save_as_btn.clicked.connect(self.save_config_file)
        save_as_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                color: #e0e0e0;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #4a9cff;
            }
        """)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                color: #e0e0e0;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #4a9cff;
            }
        """)
        
        # Add buttons to layout
        button_layout.addWidget(save_btn)
        button_layout.addWidget(save_as_btn)
        button_layout.addWidget(cancel_btn)
        
        # Assemble all groups in order
        layout.addWidget(api_group)
        layout.addWidget(model_group)
        layout.addWidget(command_group)
        layout.addWidget(prompt_group)
        layout.addWidget(tools_group)
        layout.addWidget(button_container)
        layout.addStretch()
        
        # Set scroll widget
        scroll.setWidget(scroll_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
    
    def on_api_provider_changed(self, provider):
        """Update default values when API provider changes."""
        defaults = {
            "DeepSeek": ("https://api.deepseek.com", "deepseek-chat"),
            "OpenAI": ("https://api.openai.com/v1", "gpt-4-turbo"),
            "Anthropic": ("https://api.anthropic.com", "claude-3-opus-20240229"),
            "Local": ("http://localhost:11434", "llama2"),
            "Custom": ("", "custom")
        }
        
        if provider in defaults:
            api_base, model = defaults[provider]
            self.api_base_edit.setText(api_base)
            
            # Check if model exists in combo box
            if hasattr(self, 'model_combo'):  # For backward compatibility
                if model in [self.model_combo.itemText(i) for i in range(self.model_combo.count())]:
                    self.model_combo.setCurrentText(model)
            else:
                # If using line edit for model
                self.model_edit.setText(model)
    
    def toggle_show_key(self):
        """Toggle API key visibility."""
        if self.show_key_check.isChecked():
            self.api_key_edit.setEchoMode(QLineEdit.Normal)
        else:
            self.api_key_edit.setEchoMode(QLineEdit.Password)
    
    def load_current_settings(self):
        """Load settings from existing AI instance."""
        if not self.ai:
            return
        
        try:
            # Get configuration from AI instance
            config = getattr(self.ai, 'get_config', lambda: {})()
            
            # Store MCP paths
            self.mcp_paths = config.get('mcp_paths', [])
            
            # API settings
            self.api_base_edit.setText(config.get('api_base', 'https://api.deepseek.com'))
            self.model_edit.setText(config.get('model', 'deepseek-chat'))
            
            # Load API key from .confignore
            api_key = self.config_manager.load_api_key()
            if api_key:
                self.api_key_edit.setText(api_key)
            elif hasattr(self.ai, 'api_key'):
                self.api_key_edit.setText(getattr(self.ai, 'api_key', ''))
            
            # Model parameters - handle None values safely
            self.temp_spin.setValue(config.get('temperature', 1.0))
            
            max_tokens = config.get('max_tokens')
            if max_tokens is None:
                self.max_tokens_spin.setValue(0)  # 0 means no limit
            else:
                self.max_tokens_spin.setValue(max_tokens)
            
            self.top_p_spin.setValue(config.get('top_p', 1.0))
            self.presence_spin.setValue(config.get('presence_penalty', 0.0))
            self.frequency_spin.setValue(config.get('frequency_penalty', 0.0))
            
            # Command settings
            self.cmd_start_edit.setText(config.get('command_start', 'YLDEXECUTE:'))
            self.cmd_separator_edit.setText(config.get('command_separator', '￥|'))
            self.max_iter_spin.setValue(config.get('max_iterations', 15))
            
            # System prompt
            self.prompt_edit.setText(config.get('system_prompt', ''))
            
            # MCP files display
            self.update_mcp_files_display()
            
        except Exception as e:
            print(f"Error loading current settings: {e}")
            QMessageBox.warning(self, "Load Error", f"Failed to load current settings: {e}")
    
    def load_from_config(self, config):
        """Load settings from configuration dictionary."""
        try:
            # API settings
            if 'api_base' in config:
                self.api_base_edit.setText(config['api_base'])
            if 'model' in config:
                self.model_edit.setText(config['model'])
            
            # Load API key from .confignore first
            api_key = self.config_manager.load_api_key()
            if api_key:
                self.api_key_edit.setText(api_key)
            elif 'api_key' in config:
                self.api_key_edit.setText(config['api_key'])
            
            # Model parameters - handle None values safely
            if 'temperature' in config:
                self.temp_spin.setValue(config['temperature'])
            
            if 'max_tokens' in config:
                max_tokens = config['max_tokens']
                if max_tokens is None:
                    self.max_tokens_spin.setValue(0)
                else:
                    self.max_tokens_spin.setValue(max_tokens)
            
            if 'top_p' in config:
                self.top_p_spin.setValue(config['top_p'])
            if 'presence_penalty' in config:
                self.presence_spin.setValue(config['presence_penalty'])
            if 'frequency_penalty' in config:
                self.frequency_spin.setValue(config['frequency_penalty'])
            
            # Command settings
            if 'command_start' in config:
                self.cmd_start_edit.setText(config['command_start'])
            if 'command_separator' in config:
                self.cmd_separator_edit.setText(config['command_separator'])
            if 'max_iterations' in config:
                self.max_iter_spin.setValue(config['max_iterations'])
            
            # System prompt
            if 'system_prompt' in config:
                self.prompt_edit.setText(config['system_prompt'])
            
            # MCP files
            if 'mcp_paths' in config:
                self.mcp_paths = config['mcp_paths']
                self.update_mcp_files_display()
                
        except Exception as e:
            print(f"Error loading from config: {e}")
    
    def update_mcp_files_display(self):
        """Update the MCP files display label."""
        if self.mcp_paths:
            display_text = f"MCP Files: {len(self.mcp_paths)} loaded\n\n"
            for i, path in enumerate(self.mcp_paths[:5], 1):
                filename = os.path.basename(path)
                display_text += f"  {i}. {filename}\n"
            if len(self.mcp_paths) > 5:
                display_text += f"  ... and {len(self.mcp_paths) - 5} more\n"
            self.mcp_files_label.setText(display_text)
        else:
            self.mcp_files_label.setText("No MCP files loaded")
    
    def add_mcp_files(self):
        """Add additional MCP files to the configuration."""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Add MCP Files")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        selected_files, _ = file_dialog.getOpenFileNames(
            self, "Select MCP Files", "", 
            "All Supported (*.py *.json *.yaml *.yml);;"
            "Python Files (*.py);;"
            "JSON Files (*.json);;"
            "YAML Files (*.yaml *.yml)"
        )
        
        if selected_files:
            # Add to paths list
            self.mcp_paths.extend(selected_files)
            
            # Update display
            self.update_mcp_files_display()
    
    def save_settings(self):
        """
        Save settings and emit signal to update existing AI instance.
        This method does NOT create a new AI instance.
        """
        try:
            # Collect all settings
            settings = {
                # API settings
                'api_key': self.api_key_edit.text().strip(),
                'api_base': self.api_base_edit.text().strip(),
                'model': self.model_edit.text().strip(),
                
                # Model parameters
                'temperature': self.temp_spin.value(),
                'max_tokens': self.max_tokens_spin.value() if self.max_tokens_spin.value() > 0 else None,
                'top_p': self.top_p_spin.value(),
                'presence_penalty': self.presence_spin.value(),
                'frequency_penalty': self.frequency_spin.value(),
                
                # Command settings
                'command_start': self.cmd_start_edit.text().strip(),
                'command_separator': self.cmd_separator_edit.text().strip(),
                'max_iterations': self.max_iter_spin.value(),
                
                # System prompt
                'system_prompt': self.prompt_edit.toPlainText().strip(),
                
                # MCP paths
                'mcp_paths': self.mcp_paths
            }
            
            # Validate required fields
            if not settings['api_base']:
                QMessageBox.warning(self, "Validation Error", "API Base URL is required")
                return
            
            if not settings['model']:
                QMessageBox.warning(self, "Validation Error", "Model name is required")
                return
            
            # Save API key to .confignore if provided
            if settings['api_key']:
                self.config_manager.save_api_key(settings['api_key'])
            
            # Save conversation-specific configuration
            if self.conversation_name:
                self.config_manager.save_conversation_config(self.conversation_name, settings)
            
            # Emit settings for the parent to update the existing AI instance
            self.sig_save_settings.emit(settings)
            
            # Close dialog
            self.close()
            
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Failed to save settings: {e}")
    
    def save_config_file(self):
        """Save current settings to a configuration file (without sensitive data)."""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Save Configuration File")
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("JSON Files (*.json);;YAML Files (*.yaml *.yml)")
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                config_path = selected_files[0]
                
                try:
                    # Create safe configuration (without API key)
                    safe_config = {
                        'api_base': self.api_base_edit.text().strip(),
                        'model': self.model_edit.text().strip(),
                        'temperature': self.temp_spin.value(),
                        'max_tokens': self.max_tokens_spin.value() if self.max_tokens_spin.value() > 0 else None,
                        'top_p': self.top_p_spin.value(),
                        'presence_penalty': self.presence_spin.value(),
                        'frequency_penalty': self.frequency_spin.value(),
                        'command_start': self.cmd_start_edit.text().strip(),
                        'command_separator': self.cmd_separator_edit.text().strip(),
                        'max_iterations': self.max_iter_spin.value(),
                        'system_prompt': self.prompt_edit.toPlainText().strip(),
                        'mcp_paths': self.mcp_paths,
                        'name': f'Lynexus Configuration - {self.conversation_name}',
                        'version': '1.0.0',
                        'created': os.path.basename(config_path)
                    }
                    
                    # Save based on file type
                    if config_path.endswith('.json'):
                        with open(config_path, 'w', encoding='utf-8') as f:
                            json.dump(safe_config, f, indent=2, ensure_ascii=False)
                    elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
                        with open(config_path, 'w', encoding='utf-8') as f:
                            yaml.dump(safe_config, f, default_flow_style=False, allow_unicode=True)
                    
                    QMessageBox.information(self, "Success", f"Configuration saved to:\n{config_path}")
                    
                except Exception as e:
                    QMessageBox.warning(self, "Save Error", f"Failed to save configuration file:\n{e}")