# [file name]: ui/chat_box.py
"""
Main Chat Interface with enhanced features:
- Tool execution status display in status bar
- Settings buttons moved to left panel
- Improved splitter visibility and drag functionality
- Direct AI instance updates from settings
- Conversation history loading into AI context
"""
import sys
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QScrollArea, QListWidget, QListWidgetItem, QSplitter, QFrame,
    QInputDialog, QMessageBox, QStatusBar, QFileDialog,
    QSizePolicy, QSpacerItem, QApplication
)
from PySide6.QtGui import QFont, QFontMetrics, QIcon, QFontDatabase, QLinearGradient, QBrush, QColor
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSize, QPoint

from config.i18n import i18n
from utils.config_manager import ConfigManager
from ui.init_dialog import InitDialog
from ui.settings_dialog import SettingsDialog
from aiclass import AI

class AIThread(QThread):
    """AI Processing Thread with tool execution status updates."""
    finished = Signal(str)
    error = Signal(str)
    status_update = Signal(str)  # Signal for status updates
    
    def __init__(self, ai_instance, message):
        super().__init__()
        self.ai_instance = ai_instance
        self.message = message
        self.last_command = ""  # Store the last command executed
        
    def run(self):
        try:
            # Emit initial status
            self.status_update.emit("Processing request...")
            
            # Process the user input and get response
            response, _ = self.ai_instance.process_user_inp(self.message)
            
            # Check execution status for tool execution
            status = self.ai_instance.get_execution_status()
            
            # Update status based on execution state
            if status["status"] == "executing_tool":
                tool_name = status["tool_name"] or "Unknown Tool"
                tool_args = status.get("tool_args", [])
                
                # Format the command display
                if tool_args:
                    args_str = " " + " ".join([str(arg) for arg in tool_args])
                else:
                    args_str = ""
                
                command_display = f"{self.ai_instance.command_start}{tool_name}{args_str}"
                self.status_update.emit(f"Executing: {command_display}")
            
            if response:
                self.finished.emit(response)
                # Check if there's a pending command to display
                if status["status"] == "idle":
                    self.status_update.emit("Ready")
                else:
                    # Show the last executed command
                    self.status_update.emit(f"Executed: {self.last_command}")
                
        except Exception as e:
            self.error.emit(str(e))
            self.status_update.emit(f"Error: {str(e)}")

class ChatBox(QWidget):
    """Main Chat Interface with all enhanced features."""
    
    def __init__(self):
        super().__init__()
        
        self.init_dialog = None
        self.settings_dialog = None
        self.DS_API_KEY = ""
        self.mcp_files = []
        self.system_prompt = ""
        self.temperature = 1.0
        self.ai = None
        self.current_chat_target = i18n.tr("general_chat")
        
        # Initialize config manager
        self.config_manager = ConfigManager()
        
        # History storage
        self.chat_records = self.config_manager.load_chat_history()
        
        # Conversation-specific AI instances
        self.conversation_ais = {}
        
        # Initialize UI
        self.init_ui()
        
        # Check for API key and initialize
        self.initialize_ai()
    
    def init_ui(self):
        """Initialize main user interface."""
        self.setWindowTitle(f'{i18n.tr("app_name")} - AI Assistant')
        self.setGeometry(100, 100, 1400, 900)
        
        # Set window icon
        icon_path = "assets/logo.ico"
        if os.path.isfile(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create main splitter with visible handle - REDUCED HEIGHT
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.setHandleWidth(4)  # Reduce splitter handle width
        self.main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #4a4a4a;
                border: 1px solid #3e3e3e;
                width: 4px;
            }
            QSplitter::handle:hover {
                background-color: #5a5a5a;
            }
            QSplitter::handle:pressed {
                background-color: #6a6a6a;
            }
        """)
        
        # Left panel (20% width) - Make it compact
        left_panel = self.create_left_panel()
        
        # Right panel (80% width) - Chat area
        right_panel = self.create_right_panel()
        
        # Add panels to splitter
        self.main_splitter.addWidget(left_panel)
        self.main_splitter.addWidget(right_panel)
        
        # Set initial sizes (20% left, 80% right) - Adjusted for compact left panel
        self.main_splitter.setSizes([200, 1200])
        
        # Add splitter to main layout
        main_layout.addWidget(self.main_splitter)
        
        # Create bottom status bar
        self.create_status_bar()
        main_layout.addWidget(self.status_bar)
        
        # Update status
        self.update_status_bar()
        
        # Switch to default chat
        if self.chat_list.count() > 0:
            self.switch_chat_target(self.chat_list.item(0))
    
    def create_left_panel(self):
        """Create left panel with conversation list and settings buttons."""
        left_panel = QWidget()
        left_panel.setMinimumWidth(150)  # Set minimum width
        left_panel.setMaximumWidth(300)  # Set maximum width
        left_panel.setStyleSheet("background-color: #252525;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # Conversations section - COMPACT VERSION
        conv_frame = QFrame()
        conv_frame.setFrameStyle(QFrame.StyledPanel)
        conv_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-bottom: 1px solid #3e3e3e;
                padding: 8px;
            }
        """)
        
        conv_layout = QVBoxLayout(conv_frame)
        conv_layout.setContentsMargins(8, 8, 8, 8)
        conv_layout.setSpacing(8)
        
        # Conversations title
        conv_title = QLabel(i18n.tr("conversations"))
        conv_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #4a9cff; margin-bottom: 5px;")
        conv_layout.addWidget(conv_title)
        
        # Chat list
        self.chat_list = QListWidget()
        self.chat_list.setMinimumHeight(120)  # Reduced height
        self.chat_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 6px;
                border-radius: 3px;
                color: #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #4a9cff;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #3a3a3a;
            }
        """)
        
        # Add default chats
        self.add_chat_item(i18n.tr("general_chat"))
        self.chat_list.itemClicked.connect(self.switch_chat_target)
        conv_layout.addWidget(self.chat_list)
        
        # New chat button
        add_chat_btn = QPushButton(i18n.tr("new_chat"))
        add_chat_btn.clicked.connect(self.add_new_chat)
        add_chat_btn.setStyleSheet(self.get_button_style())
        conv_layout.addWidget(add_chat_btn)
        
        # Add conversation frame to left panel
        left_layout.addWidget(conv_frame)
        
        # Settings section with separator - COMPACT VERSION
        settings_frame = QFrame()
        settings_frame.setFrameStyle(QFrame.StyledPanel)
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-top: 1px solid #3e3e3e;
                padding: 8px;
            }
        """)
        
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.setContentsMargins(8, 8, 8, 8)
        settings_layout.setSpacing(6)  # Reduced spacing
        
        # Settings title
        settings_title = QLabel(i18n.tr("quick_actions"))
        settings_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #4a9cff; margin-bottom: 5px;")
        settings_layout.addWidget(settings_title)
        
        # Settings buttons - compact style
        button_style = self.get_compact_button_style()
        
        self.settings_but = QPushButton(i18n.tr("settings"))
        self.settings_but.clicked.connect(self.open_settings)
        self.settings_but.setStyleSheet(button_style)
        settings_layout.addWidget(self.settings_but)
        
        self.init_but = QPushButton(i18n.tr("initialize"))
        self.init_but.clicked.connect(self.show_init_dialog)
        self.init_but.setStyleSheet(button_style)
        settings_layout.addWidget(self.init_but)
        
        self.load_config_btn = QPushButton(i18n.tr("load_config"))
        self.load_config_btn.clicked.connect(self.load_config_from_file)
        self.load_config_btn.setStyleSheet(button_style)
        settings_layout.addWidget(self.load_config_btn)
        
        self.tools_btn = QPushButton(i18n.tr("tools"))
        self.tools_btn.clicked.connect(self.show_tools_list)
        self.tools_btn.setStyleSheet(button_style)
        settings_layout.addWidget(self.tools_btn)
        
        # Quick action buttons
        clear_chat_btn = QPushButton(i18n.tr("clear_chat"))
        clear_chat_btn.clicked.connect(self.clear_current_chat)
        clear_chat_btn.setStyleSheet(button_style)
        settings_layout.addWidget(clear_chat_btn)
        
        export_chat_btn = QPushButton(i18n.tr("export_chat"))
        export_chat_btn.clicked.connect(self.export_chat_history)
        export_chat_btn.setStyleSheet(button_style)
        settings_layout.addWidget(export_chat_btn)
        
        # Add stretch to push everything up
        settings_layout.addStretch()
        
        # Add settings frame to left panel
        left_layout.addWidget(settings_frame)
        
        return left_panel
    
    def create_right_panel(self):
        """Create right panel with chat display and input area."""
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: #1e1e1e;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Chat display area
        chat_display_frame = QFrame()
        chat_display_frame.setFrameStyle(QFrame.StyledPanel)
        chat_display_frame.setStyleSheet("QFrame { background-color: #1e1e1e; }")
        
        chat_display_layout = QVBoxLayout(chat_display_frame)
        chat_display_layout.setContentsMargins(0, 0, 0, 0)
        chat_display_layout.setSpacing(0)
        
        # Scroll area for messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #4a4a4a;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5a5a5a;
            }
        """)
        
        # Chat container for messages
        self.chat_container = QWidget()
        self.chat_container.setStyleSheet("background-color: #1e1e1e;")
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(20, 20, 20, 20)
        self.chat_layout.setSpacing(10)
        self.chat_layout.addStretch()  # Add stretch to push messages to top
        
        self.scroll_area.setWidget(self.chat_container)
        chat_display_layout.addWidget(self.scroll_area)
        
        right_layout.addWidget(chat_display_frame, 4)  # 80% of space
        
        # Input area
        input_frame = QFrame()
        input_frame.setFrameStyle(QFrame.StyledPanel)
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-top: 1px solid #3e3e3e;
                padding: 12px;
            }
        """)
        
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(12, 12, 12, 12)
        input_layout.setSpacing(12)
        
        # Input text edit
        self.input_box_text_edit = QTextEdit()
        self.input_box_text_edit.setPlaceholderText(i18n.tr("type_message"))
        self.input_box_text_edit.setAcceptRichText(False)
        self.input_box_text_edit.setMinimumHeight(70)
        self.input_box_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                border: 1px solid #3e3e3e;
                border-radius: 8px;
                color: #e0e0e0;
                padding: 12px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border-color: #4a9cff;
                background-color: #2d2d2d;
            }
        """)
        input_layout.addWidget(self.input_box_text_edit, 4)
        
        # Send button - MODERN DESIGN
        self.send_button = QPushButton(i18n.tr("send"))
        self.send_button.setShortcut('Ctrl+Return')
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setMinimumHeight(70)
        self.send_button.setMinimumWidth(100)
        self.send_button.setStyleSheet("""
            QPushButton {
                /* Modern gradient background */
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #4a9cff, stop: 1 #2a7cff);
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                font-size: 14px;
                
                /* Subtle shadow effect */
                padding: 0px;
                
                /* Smooth hover effect */
                transition: all 0.2s;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #5aacff, stop: 1 #3a8cff);
                
                /* Slight lift effect on hover */
                margin-top: -1px;
                margin-bottom: 1px;
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #3a8cff, stop: 1 #1a6cff);
                
                /* Pressed down effect */
                margin-top: 1px;
                margin-bottom: -1px;
            }
            
            QPushButton:disabled {
                background: #2a2a2a;
                color: #666;
                border: 1px solid #3e3e3e;
            }
        """)
        
        # Add icon to send button (if available)
        send_icon_path = "assets/send_icon.png"
        if os.path.isfile(send_icon_path):
            self.send_button.setIcon(QIcon(send_icon_path))
            self.send_button.setIconSize(QSize(20, 20))
        
        input_layout.addWidget(self.send_button, 1)
        
        right_layout.addWidget(input_frame, 1)  # 20% of space
        
        return right_panel
    
    def create_status_bar(self):
        """Create status bar at the bottom."""
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #2d2d2d;
                color: #e0e0e0;
                font-size: 11px;
                padding: 3px 8px;
                border-top: 1px solid #3e3e3e;
                min-height: 20px;
                max-height: 20px;
            }
        """)
    
    def get_button_style(self):
        """Get consistent button style."""
        return """
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                color: #e0e0e0;
                padding: 6px;
                font-size: 11px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #4a9cff;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """
    
    def get_compact_button_style(self):
        """Get compact button style for left panel."""
        return """
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                color: #e0e0e0;
                padding: 5px 8px;
                font-size: 11px;
                text-align: center;
                min-height: 24px;
                max-height: 24px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #4a9cff;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """
    
    def initialize_ai(self):
        """Initialize AI based on saved configuration."""
        api_key = self.config_manager.load_api_key()
        if not api_key and not (os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")):
            QTimer.singleShot(500, self.show_init_dialog)
        else:
            # Load current conversation AI
            self.load_conversation_ai(self.current_chat_target)
            
            # Update button visibility
            has_api_key = bool(api_key)
            self.init_but.setVisible(not has_api_key)
            self.send_button.setEnabled(has_api_key)
            self.settings_but.setEnabled(has_api_key)
            self.tools_btn.setEnabled(has_api_key)
    
    def show_init_dialog(self):
        """Show initialization dialog."""
        if self.init_dialog is None:
            self.init_dialog = InitDialog()
            self.init_dialog.sig_done.connect(self.handle_init_done)
        self.init_dialog.show()
    
    def handle_init_done(self, api_key: str, mcp_files: list, config_file: str):
        """Handle initialization completion."""
        if api_key:
            self.config_manager.save_api_key(api_key)
        
        self.mcp_files = mcp_files
        
        # Load current conversation AI
        self.load_conversation_ai(self.current_chat_target)
        
        # Update UI
        self.init_but.setVisible(False)
        self.send_button.setEnabled(True)
        self.settings_but.setEnabled(True)
        self.tools_btn.setEnabled(True)
        self.update_status_bar()
    
    def load_conversation_ai(self, conversation_name):
        """Load or create AI instance for a conversation."""
        # Load conversation config
        config = self.config_manager.load_conversation_config(conversation_name)
        
        # Load API key
        api_key = self.config_manager.load_api_key()
        if not api_key:
            api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            print(f"No API key found for {conversation_name}")
            return
        
        try:
            if conversation_name in self.conversation_ais and self.conversation_ais[conversation_name]:
                # Use existing AI instance
                self.ai = self.conversation_ais[conversation_name]
                print(f"Using existing AI instance for {conversation_name}")
            else:
                # Create new AI instance
                if config:
                    # Use saved config
                    ai_config = config.copy()
                    ai_config['api_key'] = api_key
                    if 'mcp_paths' not in ai_config:
                        ai_config['mcp_paths'] = self.mcp_files
                    
                    self.ai = AI(
                        mcp_paths=ai_config.get('mcp_paths', []),
                        api_key=ai_config.get('api_key', ''),
                        api_base=ai_config.get('api_base', 'https://api.deepseek.com'),
                        model=ai_config.get('model', 'deepseek-chat'),
                        system_prompt=ai_config.get('system_prompt', ''),
                        temperature=ai_config.get('temperature', 1.0),
                        max_tokens=ai_config.get('max_tokens'),
                        top_p=ai_config.get('top_p', 1.0),
                        presence_penalty=ai_config.get('presence_penalty', 0.0),
                        frequency_penalty=ai_config.get('frequency_penalty', 0.0),
                        command_start=ai_config.get('command_start', 'YLDEXECUTE:'),
                        command_separator=ai_config.get('command_separator', '￥|'),
                        max_iterations=ai_config.get('max_iterations', 15)
                    )
                else:
                    # Create default AI instance
                    self.ai = AI(
                        mcp_paths=self.mcp_files,
                        api_key=api_key,
                        temperature=1.0
                    )
                
                # Store AI instance
                self.conversation_ais[conversation_name] = self.ai
                print(f"Created new AI instance for {conversation_name}")
            
            # Load conversation history into AI context
            if conversation_name in self.chat_records:
                history_messages = self.chat_records[conversation_name]
                if history_messages:
                    self.ai.load_conversation_history(history_messages)
                    print(f"Loaded {len(history_messages)} messages into AI context for {conversation_name}")
            
            # Update UI
            self.update_status_bar()
            
        except Exception as e:
            print(f"Failed to create/load AI instance for {conversation_name}: {e}")
    
    def update_status_bar(self):
        """Update status bar with connection and tool status."""
        if self.ai:
            tools_count = len(self.ai.funcs) if hasattr(self.ai, 'funcs') else 0
            
            # Get execution status
            status_info = self.ai.get_execution_status()
            if status_info["status"] == "executing_tool":
                tool_name = status_info.get("tool_name", "Unknown")
                tool_args = status_info.get("tool_args", [])
                
                # Format the command for display
                if tool_args:
                    args_str = " " + " ".join([str(arg) for arg in tool_args])
                else:
                    args_str = ""
                
                # Use the actual command separator
                command_sep = self.ai.command_separator if hasattr(self.ai, 'command_separator') else '￥|'
                command_display = f"{self.ai.command_start}{tool_name}{command_sep}{args_str}" if args_str else f"{self.ai.command_start}{tool_name}"
                tool_status = f" | Executing: {command_display}"
            elif status_info["status"] == "processing":
                tool_status = " | Processing..."
            else:
                tool_status = ""
            
            status_text = f"Lynexus AI | Connected to {self.ai.model} | {tools_count} tools available{tool_status}"
            self.status_bar.showMessage(status_text)
        else:
            self.status_bar.showMessage("Lynexus AI | Not connected")
    
    def open_settings(self):
        """Open settings dialog and update existing AI instance."""
        if not self.current_chat_target:
            return
        
        if self.ai:
            # Open settings with current AI instance
            self.settings_dialog = SettingsDialog(
                ai_instance=self.ai,
                conversation_name=self.current_chat_target
            )
        else:
            # Create with default config
            default_config = {
                'api_base': 'https://api.deepseek.com',
                'model': 'deepseek-chat',
                'temperature': 1.0,
                'command_start': 'YLDEXECUTE:',
                'command_separator': '￥|',
                'max_iterations': 15,
                'mcp_paths': self.mcp_files
            }
            self.settings_dialog = SettingsDialog(
                current_config=default_config,
                conversation_name=self.current_chat_target
            )
        
        # Connect signals
        self.settings_dialog.sig_save_settings.connect(self.handle_settings_save)
        self.settings_dialog.show()
    
    def handle_settings_save(self, settings: dict):
        """Handle settings save by updating existing AI instance."""
        if self.current_chat_target and self.ai:
            # Save conversation config
            self.config_manager.save_conversation_config(self.current_chat_target, settings)
            
            # Update existing AI instance instead of creating new one
            self.ai.update_config(settings)
            
            # Update UI
            self.update_status_bar()
            
            QMessageBox.information(self, "Success", f"Settings updated for {self.current_chat_target}")
    
    def load_config_from_file(self):
        """Load configuration from file."""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Load Configuration File")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        selected_files, _ = file_dialog.getOpenFileNames(
            self, "Select Config", "", 
            "Config Files (*.json *.yaml *.yml);;All Files (*.*)"
        )
        if selected_files:
            config_path = selected_files[0]
            try:
                import json
                import yaml
                
                if config_path.endswith('.json'):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                
                # Save as current conversation config
                if self.current_chat_target:
                    self.config_manager.save_conversation_config(self.current_chat_target, config)
                    
                    # Update existing AI instance if it exists
                    if self.ai:
                        self.ai.update_config(config)
                    
                    # Otherwise reload AI
                    else:
                        self.load_conversation_ai(self.current_chat_target)
                
                QMessageBox.information(self, "Success", f"Configuration loaded from {os.path.basename(config_path)}")
            except Exception as e:
                QMessageBox.warning(self, "Load Error", f"Failed to load config: {e}")
    
    def add_chat_item(self, name: str):
        """Add a chat item to the list."""
        item = QListWidgetItem(name)
        item.setData(Qt.UserRole, name)
        
        if name not in self.chat_records:
            self.chat_records[name] = []
        
        if not self.chat_list.count():
            item.setSelected(True)
        self.chat_list.addItem(item)
    
    def switch_chat_target(self, item):
        """Switch to a different chat."""
        conversation_name = item.data(Qt.UserRole)
        self.current_chat_target = conversation_name
        
        # Clear chat display
        self.clear_chat_layout()
        
        # Load AI for this conversation
        if conversation_name in self.conversation_ais:
            self.ai = self.conversation_ais[conversation_name]
        else:
            self.load_conversation_ai(conversation_name)
        
        # Load and display messages for this chat
        if conversation_name in self.chat_records:
            for msg in self.chat_records[conversation_name]:
                self.add_message(msg["text"], msg["is_sender"])
        
        # Update status bar
        self.update_status_bar()
        
        # Scroll to bottom
        self.scroll_to_bottom()
    
    def clear_chat_layout(self):
        """Clear the chat display area."""
        # Remove all widgets and spacers
        while self.chat_layout.count():
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add stretch back to bottom
        self.chat_layout.addStretch()
    
    def add_message(self, message: str, is_sender: bool):
        """Add a message bubble to the chat display with corrected width calculation."""
        # Remove the stretch temporarily
        if self.chat_layout.count() > 0:
            stretch = self.chat_layout.takeAt(self.chat_layout.count() - 1)
        
        # Create message container
        message_widget = QWidget()
        message_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Main layout for message
        message_layout = QVBoxLayout(message_widget)
        message_layout.setContentsMargins(0, 0, 0, 0)
        message_layout.setSpacing(2)
        
        # Determine bubble color and alignment
        if is_sender:
            bubble_color = "#2b5278"
            alignment = Qt.AlignRight
        elif "**AI Error**" in message:
            bubble_color = "#8b0000"
            alignment = Qt.AlignLeft
        elif "**Command Execution Requested**" in message:
            bubble_color = "#2d5a27"
            alignment = Qt.AlignLeft
        else:
            bubble_color = "#1e1e1e"
            alignment = Qt.AlignLeft
        
        # Create bubble widget
        bubble_widget = QWidget()
        bubble_widget.setStyleSheet(f"""
            background-color: {bubble_color};
            border-radius: 12px;
            padding: 12px;
            margin: 2px;
        """)
        
        bubble_layout = QHBoxLayout(bubble_widget)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create content label
        content_label = QLabel(message)
        content_label.setWordWrap(True)
        content_label.setTextFormat(Qt.MarkdownText)
        content_label.setStyleSheet("color: white; background-color: transparent;")
        content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # Calculate appropriate width - FIXED WIDTH CALCULATION
        font_metrics = QFontMetrics(content_label.font())
        
        # Get the width of the scroll area viewport (not the whole scroll area)
        available_width = self.scroll_area.viewport().width() - 60  # Account for margins and padding
        
        # Set reasonable constraints for bubble width
        max_bubble_width = min(600, available_width * 0.7)  # Max 600px or 70% of available width
        min_bubble_width = 200
        
        # Calculate the width needed for the text
        text_rect = font_metrics.boundingRect(
            0, 0, max_bubble_width, 0,
            Qt.TextWordWrap | Qt.AlignLeft, message
        )
        
        # Determine final bubble width
        bubble_width = max(min_bubble_width, min(max_bubble_width, text_rect.width() + 40))
        
        # Set fixed width for the bubble widget
        bubble_widget.setFixedWidth(int(bubble_width))
        content_label.setMaximumWidth(int(bubble_width - 24))  # Account for padding
        
        # Add content to bubble
        if alignment == Qt.AlignRight:
            bubble_layout.addStretch()
            bubble_layout.addWidget(content_label)
        else:
            bubble_layout.addWidget(content_label)
            bubble_layout.addStretch()
        
        # Add bubble to message layout
        message_layout.addWidget(bubble_widget)
        
        # Add timestamp
        timestamp = QLabel(datetime.now().strftime("%H:%M"))
        timestamp.setStyleSheet("color: #888; font-size: 10px;")
        timestamp.setAlignment(alignment)
        message_layout.addWidget(timestamp)
        
        # Add message widget to chat layout
        self.chat_layout.addWidget(message_widget)
        
        # Add the stretch back
        self.chat_layout.addStretch()
        
        # Scroll to bottom
        self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        """Scroll chat to bottom."""
        QTimer.singleShot(10, self._scroll_to_bottom)
    
    def _scroll_to_bottom(self):
        """Internal method to scroll to bottom."""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def send_message(self):
        """Send a message to the AI."""
        message = self.input_box_text_edit.toPlainText().strip()
        if not message or not self.ai:
            return
        
        # Add to chat records
        self.chat_records[self.current_chat_target].append({
            "text": message,
            "is_sender": True,
            "timestamp": datetime.now().isoformat()
        })
        
        # Display message
        self.add_message(message, is_sender=True)
        self.input_box_text_edit.clear()
        self.send_button.setEnabled(False)
        
        # Create and start AI thread
        self.ai_thread = AIThread(self.ai, message)
        self.ai_thread.finished.connect(self.handle_ai_response)
        self.ai_thread.error.connect(self.handle_ai_error)
        self.ai_thread.status_update.connect(self.handle_status_update)
        self.ai_thread.start()
    
    def handle_ai_response(self, response):
        """Handle AI response."""
        # Add to chat records
        self.chat_records[self.current_chat_target].append({
            "text": response,
            "is_sender": False,
            "timestamp": datetime.now().isoformat()
        })
        
        # Display response
        self.add_message(response, is_sender=False)
        self.send_button.setEnabled(True)
        
        # Update status
        self.update_status_bar()
    
    def handle_ai_error(self, error_msg):
        """Handle AI error."""
        error_display = f"**AI Error**\n```\n{error_msg}\n```"
        
        # Add to chat records
        self.chat_records[self.current_chat_target].append({
            "text": error_display,
            "is_sender": False,
            "timestamp": datetime.now().isoformat()
        })
        
        # Display error
        self.add_message(error_display, is_sender=False)
        self.send_button.setEnabled(True)
        
        # Update status
        self.update_status_bar()
    
    def handle_status_update(self, status_msg):
        """Handle status updates from AI thread."""
        # Update status bar with the detailed command execution status
        if self.ai:
            tools_count = len(self.ai.funcs) if hasattr(self.ai, 'funcs') else 0
            status_text = f"Lynexus AI | Connected to {self.ai.model} | {tools_count} tools available | {status_msg}"
            self.status_bar.showMessage(status_text)
        else:
            self.status_bar.showMessage(f"Lynexus AI | {status_msg}")
    
    def add_new_chat(self):
        """Add a new chat."""
        name, ok = QInputDialog.getText(self, "New Chat", "Enter chat name:")
        if ok and name:
            self.add_chat_item(name)
    
    def clear_current_chat(self):
        """Clear current chat."""
        if self.current_chat_target:
            reply = QMessageBox.question(
                self, "Clear Chat", 
                f"Clear all messages in '{self.current_chat_target}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.chat_records[self.current_chat_target] = []
                self.clear_chat_layout()
    
    def export_chat_history(self):
        """Export chat history to file."""
        if not self.current_chat_target or not self.chat_records.get(self.current_chat_target):
            QMessageBox.warning(self, "Export Error", "No chat history to export")
            return
        
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Export Chat History")
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("Text Files (*.txt);;JSON Files (*.json)")
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                try:
                    import json
                    messages = self.chat_records[self.current_chat_target]
                    if file_path.endswith('.json'):
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(messages, f, indent=2, ensure_ascii=False)
                    else:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(f"Chat: {self.current_chat_target}\n")
                            f.write("=" * 50 + "\n\n")
                            for msg in messages:
                                sender = "You" if msg.get("is_sender", False) else "AI"
                                f.write(f"{sender}: {msg.get('text', '')}\n\n")
                    
                    QMessageBox.information(self, "Export Success", f"Chat exported to {file_path}")
                except Exception as e:
                    QMessageBox.warning(self, "Export Error", f"Failed to export chat: {e}")
    
    def show_tools_list(self):
        """Show available tools list."""
        if self.ai:
            tools = self.ai.get_available_tools()
            if tools:
                tools_text = "**Available Tools**\n\n"
                for i, tool in enumerate(tools, 1):
                    desc = tool.get('description', 'No description')
                    if len(desc) > 100:
                        desc = desc[:100] + "..."
                    tools_text += f"**{i}. {tool.get('name', 'Unnamed')}**\n   {desc}\n\n"
                
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Available Tools")
                msg_box.setText(tools_text)
                msg_box.setStyleSheet("QLabel { color: white; min-width: 400px; }")
                msg_box.exec()
            else:
                QMessageBox.information(self, "Tools", "No tools available. Add MCP files in Settings.")
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save chat history
        self.config_manager.save_chat_history(self.chat_records)
        
        # Clean up AI instances
        for ai in self.conversation_ais.values():
            if hasattr(ai, 'close'):
                ai.close()
        
        super().closeEvent(event)