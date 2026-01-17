# [file name]: ui/chat_box.py
"""
Modern Chat Interface with Fluent Design
Enhanced with real-time streaming and modern UI elements
Uses independent history management system with clear state transitions
Author: Lynexus AI Assistant
Version: 3.0.0 (Refactored)
Last Updated: 2024-01-16
"""

import sys
import os
import json
import time
import traceback
from datetime import datetime
from typing import Optional, List, Dict, Callable, Any
from pathlib import Path
from enum import Enum, auto
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QScrollArea, QListWidget, QListWidgetItem, QFrame,
    QInputDialog, QMessageBox, QStatusBar, QFileDialog,
    QSizePolicy, QSpacerItem, QApplication, QProgressBar
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import (
    Qt, QTimer, QThread, Signal, QSize, QPoint, QRect, QEvent,
    QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
    QSequentialAnimationGroup, Property, QTime, QAbstractAnimation,
    QMetaObject, Slot, Q_ARG
)

from config.i18n import i18n
from utils.config_manager import ConfigManager
from utils.ai_history_manager import AIHistoryManager
from utils.markdown_renderer import MarkdownRenderer, RenderMode, get_renderer
from ui.init_dialog import InitDialog
from ui.settings_dialog import SettingsDialog
from aiclass import AI


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class ConversationConfig:
    """Configuration for a conversation session"""
    api_key: str = ""
    api_base: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    temperature: float = 1.0
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    stream: bool = True
    command_start: str = "YLDEXECUTE:"
    command_separator: str = "￥|"
    max_iterations: int = 15
    mcp_paths: List[str] = None
    system_prompt: str = ""

    # Customizable prompts for command execution flow
    command_execution_prompt: str = (
        "Execution result: {result}\n\n"
        "CRITICAL INSTRUCTION: If the task is COMPLETE, provide a FINAL SUMMARY in Chinese of ONLY this specific result - "
        "do NOT summarize previous operations or entire conversation history. "
        "Focus ONLY on what was accomplished in THIS execution. "
        "Then STOP - do NOT execute any more commands. Only execute another command if this result shows the task is incomplete "
        "and you have a clear next step."
    )

    command_retry_prompt: str = (
        "Execution failed: {error}\n\n"
        "Please analyze the error and retry with a corrected command, or provide an alternative solution."
    )

    final_summary_prompt: str = (
        "Based on the CURRENT execution result ONLY, please provide a FINAL SUMMARY in Chinese of what was found or accomplished in THIS operation. "
        "This is the FINAL request - after this summary, do NOT execute any more commands. "
        "IMPORTANT: Do NOT include summaries of previous operations or entire conversation. "
        "Focus ONLY on the most recent result. Just provide the summary and stop."
    )

    max_execution_iterations: int = 3  # Maximum iterations before forcing summary

    def __post_init__(self):
        if self.mcp_paths is None:
            self.mcp_paths = []


@dataclass
class ProcessingContext:
    """Context for AI processing operations"""
    conversation_name: str
    user_message: str
    ai_instance: Optional[AI] = None
    history_manager: Optional[AIHistoryManager] = None
    stream_callback: Optional[Callable] = None


# ============================================================================
# ENUM DEFINITIONS
# ============================================================================

class ProcessingState(Enum):
    """Processing state enumeration"""
    IDLE = auto()
    STREAMING = auto()
    EXECUTING_COMMAND = auto()
    AWAITING_SUMMARY = auto()
    ERROR = auto()


class BubbleType(Enum):
    """Message bubble type enumeration"""
    USER_MESSAGE = auto()
    AI_RESPONSE = auto()
    COMMAND_REQUEST = auto()
    COMMAND_RESULT = auto()
    FINAL_SUMMARY = auto()
    ERROR = auto()
    INFO = auto()


class MessageSource(Enum):
    """Message source for tracking"""
    USER = auto()
    AI = auto()
    SYSTEM = auto()


# ============================================================================
# ANIMATION MANAGER
# ============================================================================

class AnimationManager:
    """Manages UI animations"""
    
    @staticmethod
    def create_typing_animation(target, text: str) -> QPropertyAnimation:
        """Create typing animation"""
        animation = QPropertyAnimation(target, b"text")
        animation.setDuration(min(1000, len(text) * 30))
        animation.setEasingCurve(QEasingCurve.InOutCubic)
        animation.setStartValue("")
        animation.setEndValue(text)
        return animation
    
    @staticmethod
    def create_fade_animation(target, fade_in: bool = True) -> QPropertyAnimation:
        """Create fade animation"""
        animation = QPropertyAnimation(target, b"windowOpacity")
        animation.setDuration(300)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        if fade_in:
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
        else:
            animation.setStartValue(1.0)
            animation.setEndValue(0.0)
        return animation


# ============================================================================
# CONTEXT MANAGER
# ============================================================================

class ConversationContextManager:
    """Manages conversation contexts and AI instances"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.conversation_ais: Dict[str, AI] = {}
        self.conversation_configs: Dict[str, ConversationConfig] = {}
        
    def get_ai_for_conversation(self, conversation_name: str) -> Optional[AI]:
        """Get or create AI instance for conversation"""
        if conversation_name in self.conversation_ais:
            return self.conversation_ais[conversation_name]
        
        try:
            config = self.load_conversation_config(conversation_name)
            if not config.api_key:
                return None
            
            ai_instance = self.create_ai_instance(config)
            self.conversation_ais[conversation_name] = ai_instance
            return ai_instance
            
        except Exception as e:
            print(f"[ContextManager] Failed to create AI instance: {e}")
            return None
    
    def load_conversation_config(self, conversation_name: str) -> ConversationConfig:
        """Load configuration for conversation"""
        if conversation_name in self.conversation_configs:
            return self.conversation_configs[conversation_name]
        
        # Load from config manager
        config_data = self.config_manager.load_conversation_config(conversation_name)
        
        # Get API key from environment or config
        api_key = (self.config_manager.load_api_key() or 
                  os.environ.get("DEEPSEEK_API_KEY") or 
                  os.environ.get("OPENAI_API_KEY") or 
                  "")
        
        if config_data:
            config = ConversationConfig(
                api_key=api_key,
                api_base=config_data.get('api_base', 'https://api.deepseek.com'),
                model=config_data.get('model', 'deepseek-chat'),
                temperature=config_data.get('temperature', 1.0),
                max_tokens=config_data.get('max_tokens'),
                top_p=config_data.get('top_p', 1.0),
                stream=config_data.get('stream', True),
                command_start=config_data.get('command_start', 'YLDEXECUTE:'),
                command_separator=config_data.get('command_separator', '￥|'),
                max_iterations=config_data.get('max_iterations', 15),
                mcp_paths=config_data.get('mcp_paths', []),
                system_prompt=config_data.get('system_prompt', ''),
                command_execution_prompt=config_data.get(
                    'command_execution_prompt',
                    ConversationConfig.command_execution_prompt
                ),
                command_retry_prompt=config_data.get(
                    'command_retry_prompt',
                    ConversationConfig.command_retry_prompt
                ),
                final_summary_prompt=config_data.get(
                    'final_summary_prompt',
                    ConversationConfig.final_summary_prompt
                ),
                max_execution_iterations=config_data.get(
                    'max_execution_iterations',
                    ConversationConfig.max_execution_iterations
                )
            )
        else:
            config = ConversationConfig(
                api_key=api_key,
                system_prompt="You are a helpful AI assistant. Be concise and clear in your responses."
            )
        
        self.conversation_configs[conversation_name] = config
        return config
    
    def create_ai_instance(self, config: ConversationConfig) -> AI:
        """Create AI instance from configuration"""
        ai_kwargs = {
            'api_key': config.api_key,
            'api_base': config.api_base,
            'model': config.model,
            'temperature': config.temperature,
            'max_tokens': config.max_tokens,
            'top_p': config.top_p,
            'stream': config.stream,
            'command_start': config.command_start,
            'command_separator': config.command_separator,
            'max_iterations': config.max_iterations,
            'mcp_paths': config.mcp_paths,
            'system_prompt': config.system_prompt,
            # Pass custom prompts
            'command_execution_prompt': config.command_execution_prompt,
            'command_retry_prompt': config.command_retry_prompt,
            'final_summary_prompt': config.final_summary_prompt,
            'max_execution_iterations': config.max_execution_iterations
        }

        # Remove None values
        ai_kwargs = {k: v for k, v in ai_kwargs.items() if v is not None}

        ai_instance = AI(**ai_kwargs)

        return ai_instance
    
    def clear_conversation(self, conversation_name: str):
        """Clear conversation data"""
        if conversation_name in self.conversation_ais:
            del self.conversation_ais[conversation_name]
        if conversation_name in self.conversation_configs:
            del self.conversation_configs[conversation_name]


# ============================================================================
# MESSAGE PROCESSING ENGINE
# ============================================================================

class MessageProcessor:
    """Handles message processing logic"""
    
    def __init__(self, context_manager: ConversationContextManager, 
                 history_manager: AIHistoryManager):
        self.context_manager = context_manager
        self.history_manager = history_manager
        
    def process_message(self, context: ProcessingContext) -> Dict[str, Any]:
        """Process a message and return results"""
        try:
            # Load AI instance
            ai_instance = self.context_manager.get_ai_for_conversation(
                context.conversation_name
            )
            
            if not ai_instance:
                return {
                    'success': False,
                    'error': "AI not initialized. Please check API key."
                }
            
            context.ai_instance = ai_instance
            
            # Load conversation history
            system_prompt = getattr(ai_instance, 'system_prompt', None)
            history = self.history_manager.load_history(
                context.conversation_name, 
                system_prompt
            )
            
            # Add user message to history
            history.append({
                "role": "user",
                "content": context.user_message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Process based on streaming mode
            if ai_instance.stream:
                return self._process_streaming(context, history)
            else:
                return self._process_non_streaming(context, history)
                
        except Exception as e:
            print(f"[MessageProcessor] Error: {e}")
            traceback.print_exc()
            return {
                'success': False,
                'error': f"Processing error: {str(e)}"
            }
    
    def _process_streaming(self, context: ProcessingContext, 
                          history: List[Dict]) -> Dict[str, Any]:
        """Process message with streaming"""
        result = {
            'success': False,
            'streaming': True,
            'chunks': [],
            'full_response': "",
            'contains_command': False
        }
        
        def stream_callback(chunk: str):
            """Callback for streaming chunks"""
            if chunk and chunk.strip():
                result['chunks'].append(chunk)
                result['full_response'] += chunk
                if context.stream_callback:
                    context.stream_callback(chunk)
        
        try:
            # Process with streaming
            if hasattr(context.ai_instance, 'process_user_input_stream'):
                response = context.ai_instance.process_user_input_stream(
                    context.user_message,
                    history,
                    callback=stream_callback
                )
                
                # Handle generator if needed
                if hasattr(response, '__iter__'):
                    for _ in response:
                        pass
                
                result['success'] = True
                result['contains_command'] = self._check_for_command(
                    result['full_response'], 
                    context.ai_instance
                )
                
            else:
                # Fallback to non-streaming
                return self._process_non_streaming(context, history)
                
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def _process_non_streaming(self, context: ProcessingContext,
                              history: List[Dict]) -> Dict[str, Any]:
        """Process message without streaming"""
        try:
            response = context.ai_instance.process_user_input_with_history(
                context.user_message,
                history
            )
            
            contains_command = self._check_for_command(
                response, 
                context.ai_instance
            )
            
            # Save to history
            history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            self.history_manager.save_history(
                context.conversation_name,
                history
            )
            
            return {
                'success': True,
                'streaming': False,
                'full_response': response,
                'contains_command': contains_command
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_for_command(self, response: str, ai_instance: AI) -> bool:
        """Check if response contains a command"""
        if not hasattr(ai_instance, 'command_start'):
            return False
        return ai_instance.command_start in response
    
    def execute_command(self, context: ProcessingContext, 
                       response: str) -> Dict[str, Any]:
        """Execute command found in AI response"""
        try:
            # Extract command
            command_text = self._extract_command(response, context.ai_instance)
            if not command_text:
                return {
                    'success': False,
                    'error': "No valid command found"
                }
            
            # Parse command
            func_name, args = self._parse_command(
                command_text, 
                context.ai_instance
            )
            
            # Validate command exists
            if not hasattr(context.ai_instance, 'funcs') or func_name not in context.ai_instance.funcs:
                return {
                    'success': False,
                    'error': f"Tool '{func_name}' does not exist. Please use only available tools."
                }
            
            # Execute command
            command_result = context.ai_instance.exec_func(func_name, *args)
            
            # Save to history
            history = self.history_manager.load_history(
                context.conversation_name,
                getattr(context.ai_instance, 'system_prompt', None)
            )
            
            history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            history.append({
                "role": "user",
                "content": f"Execution result: {command_result}",
                "timestamp": datetime.now().isoformat()
            })
            
            self.history_manager.save_history(
                context.conversation_name,
                history
            )
            
            return {
                'success': True,
                'command_text': command_text,
                'command_result': command_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Command execution error: {str(e)}"
            }
    
    def _extract_command(self, response: str, ai_instance: AI) -> Optional[str]:
        """Extract command from response"""
        if not hasattr(ai_instance, 'command_start'):
            return None
        
        start_idx = response.find(ai_instance.command_start)
        if start_idx == -1:
            return None
        
        end_idx = response.find('\n', start_idx)
        if end_idx == -1:
            end_idx = len(response)
        
        return response[start_idx:end_idx].strip()
    
    def _parse_command(self, command_text: str, ai_instance: AI) -> tuple:
        """Parse command text into function name and arguments"""
        command_text = command_text.replace(ai_instance.command_start, "").strip()
        tokens = command_text.split(ai_instance.command_separator)
        tokens = [t.strip() for t in tokens if t.strip()]
        
        if not tokens:
            return "", []
        
        func_name = tokens[0]
        args = tokens[1:] if len(tokens) > 1 else []
        
        return func_name, args


# ============================================================================
# PROCESSING WORKER (FOR NON-STREAMING)
# ============================================================================

class ProcessingWorker(QThread):
    """Worker thread for non-streaming processing"""
    
    # Signals
    processing_started = Signal()
    processing_completed = Signal(dict)  # {'response': str, 'contains_command': bool}
    processing_error = Signal(str)
    
    def __init__(self, processor: MessageProcessor, context: ProcessingContext):
        super().__init__()
        self.processor = processor
        self.context = context
        self._should_stop = False
        
    def run(self):
        """Main processing loop"""
        self.processing_started.emit()
        
        try:
            # Process message
            result = self.processor.process_message(self.context)
            
            if not result['success']:
                self.processing_error.emit(result.get('error', 'Unknown error'))
                return
            
            if not result['streaming']:
                # Non-streaming result is ready
                self.processing_completed.emit({
                    'response': result['full_response'],
                    'contains_command': result['contains_command']
                })
                
        except Exception as e:
            self.processing_error.emit(f"Worker error: {str(e)}")
    
    def stop(self):
        """Stop the worker"""
        self._should_stop = True
        if self.isRunning():
            self.wait(1000)


# ============================================================================
# STREAMING PROCESSOR
# ============================================================================

class StreamingProcessor:
    """Handles streaming processing with real-time updates"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.is_processing = False
        self.current_chunks = []
        
    def process_with_streaming(self, processor: MessageProcessor,
                              context: ProcessingContext):
        """Process with streaming and handle callbacks

        IMPORTANT: In streaming mode, the AI class handles command execution internally.
        We should NOT interfere with that process here. Just collect the stream chunks.
        """
        self.is_processing = True
        self.current_chunks = []

        def stream_callback(chunk: str):
            """Handle streaming chunks"""
            if not self.is_processing:
                return

            self.current_chunks.append(chunk)
            if self.parent:
                QMetaObject.invokeMethod(
                    self.parent,
                    "handle_stream_chunk",
                    Qt.QueuedConnection,
                    Q_ARG(str, chunk)
                )

        context.stream_callback = stream_callback

        try:
            result = processor.process_message(context)

            # In streaming mode, the AI class handles everything internally
            # Just return the result without interfering
            if not result['success']:
                return result
            else:
                # Return the full response from streaming
                # The AI class has already handled commands and provided final output
                return {
                    'success': True,
                    'response': result.get('full_response', ''),
                    'command_executed': False  # AI handled it internally
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            self.is_processing = False
    
    def _request_summary(self, processor: MessageProcessor, context: ProcessingContext,
                        original_response: str, command_result: str) -> tuple:
        """Request summary after command execution

        Returns:
            tuple: (summary, full_response_with_command)
        """
        try:
            # Load history
            history = processor.history_manager.load_history(
                context.conversation_name,
                getattr(context.ai_instance, 'system_prompt', None)
            )

            # Add summary request (without saving to history permanently)
            summary_request = "Based on the execution results, please provide a final summary in Chinese of what was found or accomplished. Be concise and clear. IMPORTANT: Do NOT repeat any previous responses or summaries. Only provide NEW, original summary content. Do NOT include phrases like 'as mentioned before' or repeat the same content multiple times.\n\nFORMAT REQUIREMENT: Use proper line breaks and structure. Separate different points with blank lines. Do NOT cram everything into one single paragraph."
            temp_history = history.copy()
            temp_history.append({
                "role": "user",
                "content": summary_request,
                "timestamp": datetime.now().isoformat()
            })

            # Get summary (without saving the summary request/response to history)
            summary = context.ai_instance.process_user_input_with_history(
                summary_request,
                temp_history
            )

            # Detect and remove repetitive content from summary
            # Split into sentences for better deduplication
            sentences = []
            for line in summary.split('\n'):
                # Split by common sentence delimiters
                parts = line.replace('。', '。\n').replace('！', '！\n').replace('？', '？\n').split('\n')
                sentences.extend([p.strip() for p in parts if p.strip()])

            # Remove duplicate sentences
            seen_sentences = set()
            unique_sentences = []
            for sentence in sentences:
                if sentence not in seen_sentences:
                    seen_sentences.add(sentence)
                    unique_sentences.append(sentence)

            # Reconstruct summary
            deduplicated_summary = '。'.join(unique_sentences)
            if deduplicated_summary and not deduplicated_summary.endswith('。'):
                deduplicated_summary += '。'

            # If deduplication removed too much, use original with line-based dedup
            if len(deduplicated_summary) < len(summary) * 0.3:
                lines = summary.split('\n')
                seen_lines = set()
                unique_lines = []
                for line in lines:
                    stripped_line = line.strip()
                    if stripped_line and stripped_line not in seen_lines:
                        seen_lines.add(stripped_line)
                        unique_lines.append(line)
                    elif stripped_line and stripped_line in seen_lines:
                        continue
                    else:
                        unique_lines.append(line)
                deduplicated_summary = '\n'.join(unique_lines)

            # Combine original response (with command) and summary for display
            # Extract clean response without command for display
            clean_response = original_response
            if context.ai_instance and hasattr(context.ai_instance, 'command_start'):
                cmd_start = context.ai_instance.command_start
                if cmd_start in clean_response:
                    # Remove command line from response
                    lines = clean_response.split('\n')
                    clean_response = '\n'.join([
                        line for line in lines
                        if cmd_start not in line and not line.strip().startswith('YLDEXECUTE')
                    ]).strip()

            full_response = f"{clean_response}\n\n{deduplicated_summary}" if clean_response else deduplicated_summary

            # Only save the combined response, not the summary exchange
            history.append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.now().isoformat()
            })

            processor.history_manager.save_history(
                context.conversation_name,
                history
            )

            return summary, full_response

        except Exception as e:
            return f"Summary error: {str(e)}", original_response
    
    def stop(self):
        """Stop streaming processing"""
        self.is_processing = False


# ============================================================================
# MESSAGE BUBBLE (OPTIMIZED VERSION)
# ============================================================================

class ModernMessageBubble(QWidget):
    """Modern message bubble with improved performance"""
    
    def __init__(self, message: str = "", bubble_type: BubbleType = BubbleType.AI_RESPONSE,
                 timestamp: str = None, parent=None):
        super().__init__(parent)

        self.message = message
        self.bubble_type = bubble_type
        self.timestamp = timestamp or datetime.now().strftime("%H:%M")
        self.current_text = message
        self.is_streaming = False

        # Markdown renderer
        self.renderer = get_renderer()
        self.enable_markdown = True  # Enable markdown rendering for AI responses

        self._init_ui()
        self._apply_styling()
        self._update_size_hint()
    
    def _init_ui(self):
        """Initialize UI components"""
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Bubble container
        self.bubble_container = QFrame()
        self.bubble_container.setObjectName("bubbleContainer")
        self.bubble_container.setFrameStyle(QFrame.NoFrame)
        # Set fixed minimum width for AI bubbles to prevent jitter
        if self.bubble_type != BubbleType.USER_MESSAGE:
            self.bubble_container.setMinimumWidth(450)
            self.bubble_container.setMaximumWidth(800)

        bubble_layout = QVBoxLayout(self.bubble_container)
        bubble_layout.setContentsMargins(16, 12, 16, 8)
        bubble_layout.setSpacing(2)
        
        # Message label
        self.message_label = QLabel(self.message)
        self.message_label.setWordWrap(True)
        self.message_label.setTextFormat(Qt.TextFormat.RichText)  # Enable HTML rendering
        self.message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.message_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.message_label.setOpenExternalLinks(True)  # Allow opening links
        
        # Timestamp
        timestamp_layout = QHBoxLayout()
        timestamp_layout.setContentsMargins(0, 0, 0, 0)

        self.timestamp_label = QLabel(self.timestamp)
        self.timestamp_label.setObjectName("timestamp")
        self.timestamp_label.setAlignment(Qt.AlignRight)
        self.timestamp_label.setObjectName("timestamp")
        self.timestamp_label.setAlignment(Qt.AlignRight)
        
        timestamp_layout.addStretch()
        timestamp_layout.addWidget(self.timestamp_label)
        
        # Assemble
        bubble_layout.addWidget(self.message_label)
        bubble_layout.addLayout(timestamp_layout)
        
        # Add to main layout with alignment
        container_layout = QHBoxLayout()
        if self.bubble_type == BubbleType.USER_MESSAGE:
            container_layout.addStretch()
            container_layout.addWidget(self.bubble_container)
        else:
            container_layout.addWidget(self.bubble_container)
            container_layout.addStretch()
        
        main_layout.addLayout(container_layout)
    
    def _apply_styling(self):
        """Apply styling based on bubble type"""
        styles = {
            BubbleType.USER_MESSAGE: """
                #bubbleContainer {
                    background-color: #0084FF;
                    border-radius: 18px 4px 18px 18px;
                }
                QLabel { color: white; }
                QLabel#timestamp { color: rgba(255, 255, 255, 0.7); }
            """,
            
            BubbleType.COMMAND_REQUEST: """
                #bubbleContainer {
                    background-color: #1A5F1A;
                    border-radius: 4px 18px 18px 18px;
                    border: 1px solid #0F4F0F;
                }
                QLabel { color: #E0FFE0; }
                QLabel#timestamp { color: rgba(224, 255, 224, 0.7); }
            """,
            
            BubbleType.COMMAND_RESULT: """
                #bubbleContainer {
                    background-color: #2A4A6A;
                    border-radius: 4px 18px 18px 18px;
                    border: 1px solid #1A3A5A;
                }
                QLabel { color: #E0E0FF; }
                QLabel#timestamp { color: rgba(224, 224, 255, 0.7); }
            """,
            
            BubbleType.FINAL_SUMMARY: """
                #bubbleContainer {
                    background-color: #4A2A6A;
                    border-radius: 4px 18px 18px 18px;
                    border: 1px solid #3A1A5A;
                }
                QLabel { color: #F0E0FF; }
                QLabel#timestamp { color: rgba(240, 224, 255, 0.7); }
            """,
            
            BubbleType.ERROR: """
                #bubbleContainer {
                    background-color: #6A2A2A;
                    border-radius: 4px 18px 18px 18px;
                    border: 1px solid #5A1A1A;
                }
                QLabel { color: #FFE0E0; }
                QLabel#timestamp { color: rgba(255, 224, 224, 0.7); }
            """,
            
            BubbleType.INFO: """
                #bubbleContainer {
                    background-color: #2A4A4A;
                    border-radius: 4px 18px 18px 18px;
                    border: 1px solid #1A3A3A;
                }
                QLabel { color: #E0FFFF; }
                QLabel#timestamp { color: rgba(224, 255, 255, 0.7); }
            """
        }
        
        base_style = """
            QLabel {
                background-color: transparent;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                font-size: 14px;
                font-weight: 400;
                line-height: 1.4;
            }
            QLabel#timestamp {
                font-size: 11px;
                font-weight: 300;
            }
        """
        
        style_sheet = styles.get(self.bubble_type, """
            #bubbleContainer {
                background-color: #2D2D2D;
                border-radius: 4px 18px 18px 18px;
                border: 1px solid #333333;
            }
            QLabel { color: #E0E0E0; }
            QLabel#timestamp { color: rgba(224, 224, 224, 0.6); }
        """)
        
        self.bubble_container.setStyleSheet(style_sheet + base_style)
    
    def update_text(self, new_text: str, force_plain: bool = False):
        """
        Update bubble text with optional markdown rendering

        Args:
            new_text: New text to display
            force_plain: Force plain text (no markdown rendering)
        """
        self.current_text = new_text

        # Determine if we should render markdown
        should_render = (
            self.enable_markdown and
            not force_plain and
            self.bubble_type != BubbleType.USER_MESSAGE and
            self.bubble_type not in [BubbleType.COMMAND_REQUEST, BubbleType.ERROR, BubbleType.INFO]
        )

        # Render text (markdown for AI responses, plain for user messages)
        if should_render:
            display_text = self.renderer.render(new_text, mode=RenderMode.FINAL)
        else:
            display_text = self.renderer._escape_text(new_text)

        self.message_label.setText(display_text)
        self.timestamp_label.setText(datetime.now().strftime("%H:%M"))
        self._update_size_hint()

    def append_text(self, additional_text: str, render_html: bool = False):
        """
        Append text (for streaming) with optional incremental rendering

        Args:
            additional_text: Text to append
            render_html: Whether to render as HTML (for line-complete streaming)
        """
        self.current_text += additional_text

        # Determine if we should render markdown
        should_render = (
            self.enable_markdown and
            render_html and
            self.bubble_type != BubbleType.USER_MESSAGE and
            self.bubble_type not in [BubbleType.COMMAND_REQUEST, BubbleType.ERROR, BubbleType.INFO]
        )

        # For streaming: render incrementally if requested
        if should_render:
            display_text, _ = self.renderer.render_incremental(
                self.current_text[:-len(additional_text)],
                additional_text
            )
        else:
            # Plain text for streaming chunks
            display_text = self.renderer._escape_text(self.current_text)

        self.message_label.setText(display_text)
        self.timestamp_label.setText(datetime.now().strftime("%H:%M"))

        # Don't call _update_size_hint during streaming to prevent jitter
        # Size will be updated in finalize_rendering()

    def finalize_rendering(self):
        """Finalize markdown rendering after streaming completes"""
        # Stop streaming mode to allow size updates
        self.is_streaming = False

        # Enable markdown for all AI-related messages (not user messages)
        should_render = (
            self.enable_markdown and
            self.bubble_type != BubbleType.USER_MESSAGE and
            self.bubble_type not in [BubbleType.COMMAND_REQUEST, BubbleType.ERROR, BubbleType.INFO]
        )

        if should_render:
            final_html = self.renderer.finalize_rendering(self.current_text)
            self.message_label.setText(final_html)
            self._update_size_hint()
    
    def _update_size_hint(self):
        """Update size based on content"""
        # Only update if not streaming to avoid jitter
        if self.is_streaming:
            return

        # Let QLabel calculate its own size based on rendered content
        self.message_label.adjustSize()

        # Get the height from the label's size hint
        label_height = self.message_label.sizeHint().height()

        # Calculate total height with padding and timestamp
        total_height = label_height + 20 + 8  # Label height + timestamp + margin

        # Set minimum height but allow it to expand if needed
        self.setMinimumHeight(max(70, total_height))

    def sizeHint(self):
        # Use the message label's size hint as base
        base_height = self.message_label.sizeHint().height()
        total_height = base_height + 20 + 8  # + timestamp + margins
        return QSize(450, max(70, total_height))


# ============================================================================
# MAIN CHAT BOX (REFACTORED)
# ============================================================================

class ModernChatBox(QWidget):
    """Refactored main chat interface"""
    
    def __init__(self):
        super().__init__()
        
        # Core managers
        self.config_manager = ConfigManager()
        self.history_manager = AIHistoryManager()
        self.context_manager = ConversationContextManager(self.config_manager)
        self.message_processor = MessageProcessor(self.context_manager, self.history_manager)
        self.streaming_processor = StreamingProcessor(self)
        
        # State
        self.current_state = ProcessingState.IDLE
        self.current_conversation = i18n.tr("general_chat")
        
        # UI references
        self.current_stream_bubble = None
        self.last_command_bubble = None
        
        # Threading
        self.processing_worker = None
        self.processing_thread_pool = ThreadPoolExecutor(max_workers=2)
        
        # Data
        self.chat_list_names = self.config_manager.load_chat_list() or [i18n.tr("general_chat")]
        self.chat_records = self.config_manager.load_chat_history()
        
        # Dialogs
        self.init_dialog = None
        self.settings_dialog = None
        
        # Initialize
        self._initialize_ui()
        self._initialize_ai()
        
        print("[ModernChatBox] Initialization complete")
    
    # ============================================================================
    # UI INITIALIZATION
    # ============================================================================
    
    def _initialize_ui(self):
        """Initialize user interface"""
        self.setWindowTitle(f'{i18n.tr("app_name")} - AI Assistant')
        self.setGeometry(100, 100, 1400, 900)
        
        # Set icon
        icon_path = "assets/logo.ico"
        if os.path.isfile(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Apply theme
        self._apply_dark_theme()
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add components
        self.title_bar = self._create_title_bar()
        main_layout.addWidget(self.title_bar)
        
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.sidebar = self._create_sidebar()
        content_layout.addWidget(self.sidebar)
        
        self.chat_area = self._create_chat_area()
        content_layout.addWidget(self.chat_area, 1)
        
        main_layout.addWidget(content_widget, 1)
        
        self.status_bar = self._create_status_bar()
        main_layout.addWidget(self.status_bar)
        
        # Load initial data
        self._load_chat_list_to_ui()
        
        # Select first chat
        if self.chat_list.count() > 0:
            self.switch_chat_target(self.chat_list.item(0))
    
    def _apply_dark_theme(self):
        """Apply dark theme"""
        # Get base markdown CSS
        markdown_css = MarkdownRenderer.get_base_css()

        self.setStyleSheet(f"""
            QWidget {{
                background-color: #1E1E1E;
                color: #E0E0E0;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }}
            QScrollBar:vertical {{
                background-color: #2A2A2A;
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #404040;
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: #4A4A4A;
            }}

            /* Markdown Content Styles */
            {markdown_css}
        """)
    
    def _create_title_bar(self):
        """Create title bar"""
        title_bar = QWidget()
        title_bar.setFixedHeight(52)
        title_bar.setStyleSheet("""
            QWidget {
                background-color: #1A1A1A;
                border-bottom: 1px solid #333333;
            }
        """)
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # App icon
        icon_label = QLabel("⚡")
        icon_label.setFixedSize(32, 32)
        icon_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: #4A9CFF;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        
        # App title
        title_label = QLabel(i18n.tr("app_name"))
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 18px;
                font-weight: 600;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                background-color: transparent;
                letter-spacing: 0.5px;
            }
        """)
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addStretch()
        
        return title_bar
    
    def _create_sidebar(self):
        """Create sidebar"""
        sidebar = QWidget()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border-right: 1px solid #333333;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # New chat button
        new_chat_btn = QPushButton(i18n.tr("new_chat"))
        new_chat_btn.setFixedHeight(56)
        new_chat_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A9CFF;
                color: white;
                border: none;
                font-size: 14px;
                font-weight: 500;
                margin: 16px;
                border-radius: 12px;
                padding: 0px 20px;
            }
            QPushButton:hover { background-color: #5AACFF; }
            QPushButton:pressed { background-color: #3A8CEE; }
        """)
        new_chat_btn.clicked.connect(self._add_new_chat)
        layout.addWidget(new_chat_btn)
        
        # Conversations label
        chats_label = QLabel(i18n.tr("conversations"))
        chats_label.setFixedHeight(48)
        chats_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 12px;
                font-weight: 600;
                padding-left: 20px;
                background-color: transparent;
                letter-spacing: 1px;
                text-transform: uppercase;
            }
        """)
        layout.addWidget(chats_label)
        
        # Chat list
        self.chat_list = QListWidget()
        self.chat_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
                font-size: 14px;
                padding: 4px 8px;
            }
            QListWidget::item {
                color: #CCCCCC;
                padding: 12px 16px;
                border-radius: 8px;
                margin: 2px 8px;
                background-color: transparent;
            }
            QListWidget::item:hover {
                background-color: rgba(45, 45, 45, 0.8);
                color: #FFFFFF;
                padding-left: 20px;
            }
            QListWidget::item:selected {
                background-color: #4A9CFF;
                color: white;
                font-weight: 500;
                padding-left: 24px;
            }
        """)
        self.chat_list.itemClicked.connect(self.switch_chat_target)
        layout.addWidget(self.chat_list, 1)
        
        # Bottom actions
        bottom_widget = QWidget()
        bottom_widget.setFixedHeight(280)
        bottom_widget.setStyleSheet("background-color: transparent;")
        
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(16, 16, 16, 16)
        bottom_layout.setSpacing(8)
        
        # Action buttons
        actions = [
            (i18n.tr("import_config"), self._import_config_file, "#3A3A3A"),
            (i18n.tr("settings"), self._open_settings, "#4A4A4A"),
            (i18n.tr("initialize"), self._show_init_dialog, "#2A7CDD"),
            (i18n.tr("tools"), self._show_tools_list, "#3A3A3A"),
            (i18n.tr("export_chat"), self._export_chat_history, "#3A3A3A"),
            (i18n.tr("clear_chat"), self._clear_current_chat, "#D32F2F")
        ]
        
        for text, callback, color in actions:
            btn = self._create_sidebar_button(text, callback, color)
            bottom_layout.addWidget(btn)
        
        bottom_layout.addStretch()
        layout.addWidget(bottom_widget)
        
        return sidebar
    
    def _create_sidebar_button(self, text: str, callback, color: str):
        """Create sidebar button"""
        button = QPushButton(text)
        button.setFixedHeight(44)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #E0E0E0;
                border: none;
                text-align: left;
                padding-left: 16px;
                font-size: 14px;
                font-weight: 400;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: #3D3D3D;
                color: white;
                padding-left: 20px;
            }}
        """)
        button.clicked.connect(callback)
        return button
    
    def _create_chat_area(self):
        """Create main chat area"""
        chat_widget = QWidget()
        chat_widget.setStyleSheet("background-color: #1E1E1E;")
        
        layout = QVBoxLayout(chat_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Chat title
        self.chat_title = QLabel(i18n.tr("general_chat"))
        self.chat_title.setFixedHeight(68)
        self.chat_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: 600;
                padding-left: 28px;
                background-color: transparent;
                border-bottom: 1px solid #333333;
            }
        """)
        layout.addWidget(self.chat_title)
        
        # Message area
        self.message_scroll = QScrollArea()
        self.message_scroll.setWidgetResizable(True)
        self.message_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.message_scroll.setStyleSheet("""
            QScrollArea {
                background-color: #1E1E1E;
                border: none;
            }
        """)
        
        self.message_container = QWidget()
        self.message_container.setStyleSheet("background-color: #1E1E1E;")
        
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.setContentsMargins(20, 20, 20, 20)
        self.message_layout.setSpacing(12)
        self.message_layout.addStretch()
        
        self.message_scroll.setWidget(self.message_container)
        layout.addWidget(self.message_scroll, 1)
        
        # Input area
        input_widget = QWidget()
        input_widget.setFixedHeight(160)
        input_widget.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border-top: 1px solid #333333;
            }
        """)
        
        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(20, 16, 20, 16)
        input_layout.setSpacing(12)
        
        # Input text box
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText(i18n.tr("type_message"))
        self.input_text.setAcceptRichText(False)
        self.input_text.setStyleSheet("""
            QTextEdit {
                background-color: #2D2D2D;
                border: 2px solid #333333;
                border-radius: 12px;
                color: #FFFFFF;
                padding: 16px;
                font-size: 14px;
                selection-background-color: #4A9CFF;
                line-height: 1.5;
            }
            QTextEdit:focus {
                border-color: #4A9CFF;
                background-color: #2A2A2A;
            }
            QTextEdit::placeholder {
                color: #777777;
                font-style: italic;
            }
        """)
        self.input_text.setMaximumHeight(80)
        input_layout.addWidget(self.input_text, 1)
        
        # Button layout
        button_layout = QHBoxLayout()

        # Delete chat button
        self.delete_chat_button = QPushButton(i18n.tr("delete_chat"))
        self.delete_chat_button.setFixedHeight(40)
        self.delete_chat_button.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #777777; }
            QPushButton:pressed { background-color: #555555; }
            QPushButton:disabled {
                background-color: #444444;
                color: #888888;
            }
        """)
        self.delete_chat_button.clicked.connect(self._delete_current_chat)
        button_layout.addWidget(self.delete_chat_button)

        button_layout.addStretch()

        # Stop button
        self.stop_button = QPushButton(i18n.tr("stop"))
        self.stop_button.setFixedHeight(40)
        self.stop_button.setVisible(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #FF4757;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #FF5E6D; }
            QPushButton:pressed { background-color: #E63E4D; }
            QPushButton:disabled {
                background-color: #444444;
                color: #888888;
            }
        """)
        self.stop_button.clicked.connect(self._stop_processing)
        button_layout.addWidget(self.stop_button)
        
        # Send button
        self.send_button = QPushButton(i18n.tr("send"))
        self.send_button.setFixedHeight(40)
        self.send_button.setShortcut('Ctrl+Return')
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4A9CFF;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                padding: 0 24px;
            }
            QPushButton:hover { background-color: #5AACFF; }
            QPushButton:pressed { background-color: #3A8CEE; }
            QPushButton:disabled {
                background-color: #444444;
                color: #888888;
            }
        """)
        self.send_button.clicked.connect(self._send_message)
        button_layout.addWidget(self.send_button)
        
        input_layout.addLayout(button_layout)
        layout.addWidget(input_widget)
        
        return chat_widget
    
    def _create_status_bar(self):
        """Create status bar"""
        status_bar = QStatusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #252525;
                color: #AAAAAA;
                font-size: 11px;
                font-weight: 400;
                border-top: 1px solid #333333;
                padding: 8px 16px;
            }
        """)
        
        status_bar.showMessage("Lynexus AI | Not connected")
        return status_bar
    
    def _load_chat_list_to_ui(self):
        """Load chat list to UI"""
        self.chat_list.clear()
        
        for name in self.chat_list_names:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, name)
            
            if name not in self.chat_records:
                self.chat_records[name] = []
            
            self.chat_list.addItem(item)
            
            if name not in self.chat_list_names:
                self.chat_list_names.append(name)
                self.config_manager.save_chat_list(self.chat_list_names)
    
    # ============================================================================
    # MESSAGE PROCESSING
    # ============================================================================
    
    def _send_message(self):
        """Send message to AI"""
        message = self.input_text.toPlainText().strip()
        if not message:
            return
        
        if self.current_state != ProcessingState.IDLE:
            return
        
        # Check AI initialization
        ai_instance = self.context_manager.get_ai_for_conversation(self.current_conversation)
        if not ai_instance:
            QMessageBox.warning(self, "Error", "AI not initialized. Please check API key.")
            return
        
        try:
            # Update state
            self.current_state = ProcessingState.STREAMING
            self.send_button.setEnabled(False)
            self.stop_button.setVisible(True)
            self.input_text.clear()

            # Initialize chat records for new conversation if needed
            if self.current_conversation not in self.chat_records:
                self.chat_records[self.current_conversation] = []

            # Save user message
            current_time = datetime.now().isoformat()
            self.chat_records[self.current_conversation].append({
                "text": message,
                "is_sender": True,
                "timestamp": current_time
            })
            
            # Display user message
            self._add_message_to_display(
                message=message,
                bubble_type=BubbleType.USER_MESSAGE,
                timestamp=current_time
            )
            
            QApplication.processEvents()
            
            # Start processing
            self._start_message_processing(message, ai_instance)
            
        except Exception as e:
            print(f"[ModernChatBox] Send message error: {e}")
            traceback.print_exc()
            self._reset_state()
    
    def _start_message_processing(self, message: str, ai_instance: AI):
        """Start message processing based on mode"""
        context = ProcessingContext(
            conversation_name=self.current_conversation,
            user_message=message,
            ai_instance=ai_instance,
            history_manager=self.history_manager
        )
        
        if ai_instance.stream:
            # Streaming mode
            self._process_streaming(context)
        else:
            # Non-streaming mode (use thread)
            self._process_non_streaming(context)
    
    def _process_streaming(self, context: ProcessingContext):
        """Process message with streaming"""
        # Run in thread pool to avoid blocking
        future = self.processing_thread_pool.submit(
            self._execute_streaming_processing,
            context
        )
        future.add_done_callback(self._handle_streaming_result)
    
    def _execute_streaming_processing(self, context: ProcessingContext):
        """Execute streaming processing in background"""
        return self.streaming_processor.process_with_streaming(
            self.message_processor,
            context
        )
    
    def _handle_streaming_result(self, future):
        """Handle streaming result from thread pool"""
        try:
            result = future.result()
            print(f"[ChatBox] Streaming result received: {result}")

            if not result['success']:
                self._handle_processing_error(result.get('error', 'Unknown error'))
                return

            # In streaming mode, AI handles everything internally
            # Just finalize the current bubble if it exists
            response_text = result.get('response', '')
            print(f"[ChatBox] Finalizing streaming response, text length: {len(response_text)}")

            # Save AI conversation history (this is critical for context memory)
            if self.current_conversation:
                ai_instance = self.context_manager.get_ai_for_conversation(self.current_conversation)
                if ai_instance and hasattr(ai_instance, 'conv_his') and ai_instance.conv_his:
                    print(f"[ChatBox] Saving AI history with {len(ai_instance.conv_his)} messages")
                    self.history_manager.save_history(
                        self.current_conversation,
                        ai_instance.conv_his
                    )

            # Use QMetaObject.invokeMethod to ensure execution on main thread
            # This is more reliable than QTimer.singleShot in thread pool callbacks
            print("[ChatBox] Scheduling finalize with QMetaObject.invokeMethod")
            QMetaObject.invokeMethod(
                self,
                "_finalize_streaming_response",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, response_text)
            )

        except Exception as e:
            print(f"[ChatBox] Error in _handle_streaming_result: {e}")
            traceback.print_exc()
            self._handle_processing_error(f"Streaming error: {str(e)}")

    @Slot(str)
    def _finalize_streaming_response(self, response_text: str):
        """Finalize streaming response in main thread"""
        try:
            print(f"[ChatBox] _finalize_streaming_response called, current_stream_bubble: {self.current_stream_bubble}")

            # Clean and process response text
            display_text = self._clean_response_text(response_text)

            if self.current_stream_bubble:
                self.current_stream_bubble.is_streaming = False
                if display_text:
                    # Update with final summary only and finalize markdown rendering
                    self.current_stream_bubble.update_text(display_text)
                    self.current_stream_bubble.finalize_rendering()
                self._save_chat_record(display_text, False)
            else:
                # Should have been created via streaming chunks
                print("[ChatBox] No stream bubble found, showing final response")
                self._show_final_response(display_text)

            print("[ChatBox] Calling _reset_state()")
            self._reset_state()
            print("[ChatBox] _reset_state() completed")
        except Exception as e:
            print(f"[ChatBox] Error finalizing response: {e}")
            traceback.print_exc()

    def _clean_response_text(self, response_text: str) -> str:
        """Clean response text by removing commands and duplicates"""
        # Step 1: Remove all command lines
        lines = response_text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Skip command lines
            if 'YLDEXECUTE:' in line or line.strip().startswith('￥|'):
                continue
            cleaned_lines.append(line)

        # Step 2: Join and split by "最终总结" to find the last one
        text = '\n'.join(cleaned_lines)

        # Find all "最终总结" occurrences
        if '**最终总结**' in text:
            parts = text.split('**最终总结**')
            # Take only the last "最终总结" section
            text = '**最终总结**' + parts[-1]

        # Step 3: Clean up extra whitespace and ensure proper formatting
        lines = text.split('\n')
        final_lines = []
        prev_empty = False

        for line in lines:
            stripped = line.strip()
            if stripped:
                final_lines.append(stripped)
                prev_empty = False
            elif not prev_empty:
                # Keep single empty lines between paragraphs
                final_lines.append('')
                prev_empty = True

        # Step 4: Rejoin with proper line breaks
        display_text = '\n'.join(final_lines).strip()

        # Remove any trailing whitespace and ensure single newline at end
        display_text = display_text.replace('\n\n\n', '\n\n')

        return display_text
    
    def _process_non_streaming(self, context: ProcessingContext):
        """Process message without streaming"""
        # Clear any existing worker
        if self.processing_worker:
            self.processing_worker.stop()
        
        # Create and start worker
        self.processing_worker = ProcessingWorker(self.message_processor, context)
        
        self.processing_worker.processing_started.connect(
            self._on_non_streaming_started
        )
        self.processing_worker.processing_completed.connect(
            self._on_non_streaming_completed
        )
        self.processing_worker.processing_error.connect(
            self._handle_processing_error
        )
        
        self.processing_worker.start()
    
    def _on_non_streaming_started(self):
        """Handle non-streaming processing started"""
        # Show progress indicator
        self._add_message_to_display(
            message="Processing...",
            bubble_type=BubbleType.INFO
        )
    
    def _on_non_streaming_completed(self, result: dict):
        """Handle non-streaming processing completed"""
        # Remove progress indicator
        self._remove_last_bubble()
        
        response = result.get('response', '')
        contains_command = result.get('contains_command', False)
        
        if contains_command:
            # Handle command execution
            self._handle_non_streaming_command(response)
        else:
            # Show regular response
            self._show_final_response(response)
        
        self._reset_state()
    
    def _handle_non_streaming_command(self, response: str):
        """Handle command in non-streaming mode"""
        # Show command bubble and save reference
        command_bubble = self._add_message_to_display(
            message=f"🔧 Executing command...",
            bubble_type=BubbleType.COMMAND_REQUEST
        )
        self.last_command_bubble = command_bubble

        # Execute command
        context = ProcessingContext(
            conversation_name=self.current_conversation,
            user_message="",
            ai_instance=self.context_manager.get_ai_for_conversation(self.current_conversation)
        )

        command_result = self.message_processor.execute_command(context, response)

        # Update command bubble with result
        if command_result['success']:
            command_bubble.update_text(
                f"✅ Command executed successfully\n{command_result['command_result'][:200]}..."
            )

            # Request and show summary
            summary, full_response = self._request_summary_after_command(
                response,
                command_result['command_result']
            )

            self._show_final_summary(summary, full_response)

        else:
            command_bubble.update_text(
                f"❌ Command failed\n{command_result['error']}"
            )
            command_bubble.bubble_type = BubbleType.ERROR
            command_bubble._apply_styling()
            self.last_command_bubble = None  # Clear reference on error
    
    def _request_summary_after_command(self, original_response: str,
                                      command_result: str) -> tuple:
        """Request summary after command execution

        Returns:
            tuple: (summary, full_response_with_command)
        """
        try:
            ai_instance = self.context_manager.get_ai_for_conversation(
                self.current_conversation
            )

            # Load history
            history = self.history_manager.load_history(
                self.current_conversation,
                getattr(ai_instance, 'system_prompt', None)
            )

            # Add summary request (without saving to history permanently)
            summary_request = "Based on the execution results, please provide a final summary in Chinese of what was found or accomplished. Be concise and clear. IMPORTANT: Do NOT repeat any previous responses or summaries. Only provide NEW, original summary content. Do NOT include phrases like 'as mentioned before' or repeat the same content multiple times.\n\nFORMAT REQUIREMENT: Use proper line breaks and structure. Separate different points with blank lines. Do NOT cram everything into one single paragraph."
            temp_history = history.copy()
            temp_history.append({
                "role": "user",
                "content": summary_request,
                "timestamp": datetime.now().isoformat()
            })

            # Get summary (without saving the summary request/response to history)
            summary = ai_instance.process_user_input_with_history(
                summary_request,
                temp_history
            )

            # Detect and remove repetitive content from summary
            # Split into sentences for better deduplication
            sentences = []
            for line in summary.split('\n'):
                # Split by common sentence delimiters
                parts = line.replace('。', '。\n').replace('！', '！\n').replace('？', '？\n').split('\n')
                sentences.extend([p.strip() for p in parts if p.strip()])

            # Remove duplicate sentences
            seen_sentences = set()
            unique_sentences = []
            for sentence in sentences:
                if sentence not in seen_sentences:
                    seen_sentences.add(sentence)
                    unique_sentences.append(sentence)

            # Reconstruct summary
            deduplicated_summary = '。'.join(unique_sentences)
            if deduplicated_summary and not deduplicated_summary.endswith('。'):
                deduplicated_summary += '。'

            # If deduplication removed too much, use original with line-based dedup
            if len(deduplicated_summary) < len(summary) * 0.3:
                lines = summary.split('\n')
                seen_lines = set()
                unique_lines = []
                for line in lines:
                    stripped_line = line.strip()
                    if stripped_line and stripped_line not in seen_lines:
                        seen_lines.add(stripped_line)
                        unique_lines.append(line)
                    elif stripped_line and stripped_line in seen_lines:
                        continue
                    else:
                        unique_lines.append(line)
                deduplicated_summary = '\n'.join(unique_lines)

            # Combine original response (with command) and summary for display
            # Extract clean response without command for display
            clean_response = original_response
            if ai_instance and hasattr(ai_instance, 'command_start'):
                cmd_start = ai_instance.command_start
                if cmd_start in clean_response:
                    # Remove command line from response
                    lines = clean_response.split('\n')
                    clean_response = '\n'.join([
                        line for line in lines
                        if cmd_start not in line and not line.strip().startswith('YLDEXECUTE')
                    ]).strip()

            full_response = f"{clean_response}\n\n{deduplicated_summary}" if clean_response else deduplicated_summary

            # Only save the combined response, not the summary exchange
            history.append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.now().isoformat()
            })

            self.history_manager.save_history(
                self.current_conversation,
                history
            )

            return summary, full_response

        except Exception as e:
            return f"Error generating summary: {str(e)}", original_response
    
    @Slot(str)
    def handle_stream_chunk(self, chunk: str):
        """Handle streaming chunk (called from streaming processor)

        IMPORTANT: Filter out ALL command-related content before display.
        Only show clean final results to the user.
        """
        if not chunk or not chunk.strip():
            return

        # Initialize command filtering state
        if not hasattr(self, '_in_command_mode'):
            self._in_command_mode = False
        if not hasattr(self, '_accumulated_before_command'):
            self._accumulated_before_command = ""

        # Check for command markers in the chunk
        if self.current_conversation:
            ai_instance = self.context_manager.get_ai_for_conversation(self.current_conversation)
            if ai_instance and hasattr(ai_instance, 'command_start'):
                cmd_start = ai_instance.command_start

                # If this chunk contains a command marker
                if cmd_start in chunk:
                    print(f"[ChatBox] Command detected in stream chunk: {chunk[:50]}...")
                    # Enter command mode - stop displaying
                    self._in_command_mode = True

                    # Clear any bubble that was created before the command
                    if self.current_stream_bubble:
                        print("[ChatBox] Clearing bubble that had content before command")
                        self._remove_bubble(self.current_stream_bubble)
                        self.current_stream_bubble = None
                        self._accumulated_before_command = ""

                    # Don't display command content
                    return

                # If we're in command mode, check if this is the start of real content
                if self._in_command_mode:
                    # Look for indicators that we're now getting real content (not command output)
                    # Real content typically starts with text after newlines, not command syntax
                    chunk_clean = chunk.strip()

                    # Skip empty chunks or chunks that look like continuation of command
                    if not chunk_clean:
                        return

                    # If we see actual content (not just special characters or command artifacts),
                    # exit command mode and start displaying
                    # Check if this looks like real content (has substantial text, not just symbols)
                    has_real_content = (
                        len(chunk_clean) > 2 and
                        not chunk_clean.startswith('￥|') and
                        not chunk_clean.startswith('》') and
                        not cmd_start in chunk_clean
                    )

                    if has_real_content:
                        print(f"[ChatBox] Exiting command mode, showing real content: {chunk_clean[:50]}...")
                        self._in_command_mode = False

                        # Create new bubble for the final conclusion
                        if self.current_stream_bubble is None:
                            self.current_stream_bubble = self._add_message_to_display(
                                message=chunk_clean,
                                bubble_type=BubbleType.AI_RESPONSE
                            )
                            self.current_stream_bubble.is_streaming = True
                        else:
                            self.current_stream_bubble.append_text(chunk_clean)

                        QApplication.processEvents()
                        self._scroll_to_bottom()
                        return
                    else:
                        # Still in command mode, skip this chunk
                        return

        # Not in command mode - display content normally
        chunk = chunk.strip()
        if not chunk:
            return

        # Create or update streaming bubble (only for clean content)
        if self.current_stream_bubble is None:
            self.current_stream_bubble = self._add_message_to_display(
                message=chunk,
                bubble_type=BubbleType.AI_RESPONSE
            )
            self.current_stream_bubble.is_streaming = True
        else:
            # Incremental rendering: Check if chunk ends with newline (line complete)
            ends_with_newline = chunk.endswith('\n') or '\n' in chunk
            self.current_stream_bubble.append_text(chunk, render_html=ends_with_newline)

        QApplication.processEvents()
        self._scroll_to_bottom()
    
    def _show_final_response(self, response: str):
        """Show final response bubble with markdown rendering"""
        bubble = self._add_message_to_display(
            message=response,
            bubble_type=BubbleType.AI_RESPONSE
        )

        # Apply final markdown rendering
        bubble.finalize_rendering()

        self._save_chat_record(response, False)
    
    def _show_final_summary(self, summary: str, full_response: str = ""):
        """Show final summary bubble with markdown rendering

        Args:
            summary: The summary text from AI
            full_response: The full response including cleaned original response
        """
        # Remove intermediate bubbles (command execution bubbles)
        # We need to remove the command bubble that was shown before
        if self.last_command_bubble:
            self._remove_bubble(self.last_command_bubble)
            self.last_command_bubble = None

        # Also remove current streaming bubble if it exists
        if self.current_stream_bubble:
            self._remove_bubble(self.current_stream_bubble)
            self.current_stream_bubble = None

        # Use full_response if provided, otherwise use summary
        display_text = full_response if full_response else summary

        bubble = self._add_message_to_display(
            message=f"✅ Task completed:\n{display_text}",
            bubble_type=BubbleType.FINAL_SUMMARY
        )

        # Apply final markdown rendering
        bubble.finalize_rendering()

        self._save_chat_record(f"Task completed:\n{display_text}", False)
    
    def _handle_processing_error(self, error_text: str):
        """Handle processing error"""
        self._add_message_to_display(
            message=f"❌ Error:\n{error_text}",
            bubble_type=BubbleType.ERROR
        )
        
        self._save_chat_record(f"Error:\n{error_text}", False)
        self._reset_state()
    
    def _reset_state(self):
        """Reset processing state"""
        self.current_state = ProcessingState.IDLE
        self.send_button.setEnabled(True)
        self.stop_button.setVisible(False)
        self.current_stream_bubble = None
        self.processing_worker = None

        # CRITICAL: Reset AI stop flag to allow future processing
        if self.current_conversation:
            ai_instance = self.context_manager.get_ai_for_conversation(self.current_conversation)
            if ai_instance and hasattr(ai_instance, 'set_stop_flag'):
                ai_instance.set_stop_flag(False)

        # Reset command filtering state
        if hasattr(self, '_in_command_mode'):
            self._in_command_mode = False
        if hasattr(self, '_accumulated_before_command'):
            self._accumulated_before_command = ""

        self._update_status_bar()
        QApplication.processEvents()
    
    def _stop_processing(self):
        """Stop ongoing processing"""
        # Stop streaming processor
        self.streaming_processor.stop()

        # Stop worker if running
        if self.processing_worker and self.processing_worker.isRunning():
            self.processing_worker.stop()

        # Stop AI instance
        ai_instance = self.context_manager.get_ai_for_conversation(self.current_conversation)
        if ai_instance and hasattr(ai_instance, 'set_stop_flag'):
            ai_instance.set_stop_flag(True)

        # Show stopped message
        self._add_message_to_display(
            message="⏹️ Processing stopped",
            bubble_type=BubbleType.INFO
        )

        self._reset_state()

    def _delete_current_chat(self):
        """Delete current chat conversation"""
        if not self.current_conversation:
            return

        # Confirm deletion
        confirm_title = i18n.tr("confirm_delete") or "Confirm Delete"
        confirm_msg = i18n.tr("confirm_delete_message")

        if confirm_msg and "{0}" in confirm_msg:
            message = confirm_msg.replace("{0}", self.current_conversation)
        else:
            message = f'Are you sure you want to delete chat "{self.current_conversation}"?'

        reply = QMessageBox.question(
            self,
            confirm_title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Stop any ongoing processing
            self._stop_processing()

            # Store the name being deleted
            deleted_conversation = self.current_conversation

            # Clear conversation data from context manager
            self.context_manager.clear_conversation(deleted_conversation)

            # Remove from chat records
            if deleted_conversation in self.chat_records:
                del self.chat_records[deleted_conversation]

            # Remove from chat list
            if deleted_conversation in self.chat_list_names:
                self.chat_list_names.remove(deleted_conversation)

            # Clear AI history
            self.history_manager.delete_history(deleted_conversation)

            # Save updated config
            self.config_manager.save_chat_history(self.chat_records)
            self.config_manager.save_chat_list(self.chat_list_names)

            # Reload chat list UI
            self._load_chat_list_to_ui()

            # Switch to first available chat or create new one
            if self.chat_list_names:
                first_chat = self.chat_list_names[0]
                if first_chat:
                    items = self.chat_list.findItems(first_chat, Qt.MatchFlag.MatchExactly)
                    if items:
                        self.switch_chat_target(items[0])
            else:
                # Create a new default chat
                self._add_new_chat()
                self._load_chat_list_to_ui()

            print(f"[ModernChatBox] Deleted conversation: {deleted_conversation}")
    
    # ============================================================================
    # UI HELPERS
    # ============================================================================
    
    def _add_message_to_display(self, message: str, bubble_type: BubbleType, 
                               timestamp: str = None) -> ModernMessageBubble:
        """Add message to display area"""
        if not timestamp:
            timestamp = datetime.now().strftime("%H:%M")
        
        bubble = ModernMessageBubble(message, bubble_type, timestamp)
        self.message_layout.insertWidget(self.message_layout.count() - 1, bubble)
        
        self.message_container.adjustSize()
        QTimer.singleShot(100, self._scroll_to_bottom)
        
        return bubble
    
    def _remove_bubble(self, bubble: ModernMessageBubble):
        """Remove bubble from display"""
        index = self.message_layout.indexOf(bubble)
        if index != -1:
            item = self.message_layout.takeAt(index)
            if item and item.widget():
                item.widget().deleteLater()
    
    def _remove_last_bubble(self):
        """Remove last bubble (for progress indicators)"""
        count = self.message_layout.count()
        if count > 1:  # Don't remove the stretch item
            item = self.message_layout.takeAt(count - 2)
            if item and item.widget():
                item.widget().deleteLater()
    
    def _clear_message_display(self):
        """Clear all messages from display"""
        while self.message_layout.count() > 1:
            item = self.message_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Clear bubble references
        self.current_stream_bubble = None
        self.last_command_bubble = None
    
    def _scroll_to_bottom(self):
        """Scroll to bottom of message area"""
        scrollbar = self.message_scroll.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())
    
    def _save_chat_record(self, text: str, is_sender: bool):
        """Save chat record"""
        self.chat_records[self.current_conversation].append({
            "text": text,
            "is_sender": is_sender,
            "timestamp": datetime.now().isoformat()
        })
        
        self.config_manager.save_chat_history(self.chat_records)
    
    def _update_status_bar(self):
        """Update status bar"""
        ai_instance = self.context_manager.get_ai_for_conversation(self.current_conversation)
        
        if ai_instance:
            tools_count = len(ai_instance.funcs) if hasattr(ai_instance, 'funcs') else 0
            streaming_status = "Streaming" if ai_instance.stream else "Standard"
            model_name = getattr(ai_instance, 'model', 'Unknown')
            
            state_text = {
                ProcessingState.STREAMING: " | Streaming",
                ProcessingState.EXECUTING_COMMAND: " | Executing Command",
                ProcessingState.AWAITING_SUMMARY: " | Awaiting Summary",
                ProcessingState.ERROR: " | Error"
            }.get(self.current_state, "")
            
            status_text = f"Lynexus AI | {model_name} | {tools_count} tools | {streaming_status}{state_text}"
            self.status_bar.showMessage(status_text)
        else:
            self.status_bar.showMessage("Lynexus AI | Not connected")
    
    # ============================================================================
    # CONVERSATION MANAGEMENT
    # ============================================================================
    
    def switch_chat_target(self, item):
        """Switch to different chat conversation"""
        if not item:
            return

        conversation_name = item.data(Qt.UserRole)

        if conversation_name == self.current_conversation:
            return

        # If currently processing, warn user and don't switch
        if self.current_state != ProcessingState.IDLE:
            QMessageBox.warning(
                self,
                i18n.tr("warning") or "Warning",
                i18n.tr("cannot_switch_during_process") or "Please wait for the current response to complete before switching conversations.",
                QMessageBox.StandardButton.Ok
            )
            return

        print(f"[ModernChatBox] Switching to: {conversation_name}")

        try:
            # Set as current item in QListWidget for visual selection
            self.chat_list.setCurrentItem(item)

            self.current_conversation = conversation_name
            self.chat_title.setText(conversation_name)

            # Save as last active
            self.config_manager.save_last_active_chat(conversation_name)

            # Clear UI
            self._clear_message_display()
            self.current_stream_bubble = None
            self.last_command_bubble = None

            # Load AI for conversation
            self.context_manager.get_ai_for_conversation(conversation_name)
            
            # Load messages
            self._load_conversation_messages(conversation_name)
            
            # Update status
            self._update_status_bar()
            
            # Scroll to bottom
            QTimer.singleShot(100, self._scroll_to_bottom)
            
        except Exception as e:
            print(f"[ModernChatBox] Switch error: {e}")
            QMessageBox.warning(self, "Switch Error", f"Error: {e}")
    
    def _load_conversation_messages(self, conversation_name: str):
        """Load and display conversation messages"""
        if conversation_name in self.chat_records:
            messages = self.chat_records[conversation_name]
            
            self.message_container.setUpdatesEnabled(False)
            
            for msg in messages:
                # Get timestamp
                timestamp = msg.get("timestamp", "")
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        time_str = dt.strftime("%H:%M")
                    except:
                        time_str = datetime.now().strftime("%H:%M")
                else:
                    time_str = datetime.now().strftime("%H:%M")
                
                # Determine bubble type
                is_sender = msg.get("is_sender", False)
                text = msg.get("text", "")
                
                if is_sender:
                    bubble_type = BubbleType.USER_MESSAGE
                elif "执行命令" in text or "Executing command" in text:
                    bubble_type = BubbleType.COMMAND_REQUEST
                elif "执行结果" in text or "Command executed" in text:
                    bubble_type = BubbleType.COMMAND_RESULT
                elif "任务完成" in text or "Task completed" in text:
                    bubble_type = BubbleType.FINAL_SUMMARY
                elif "错误" in text or "Error" in text:
                    bubble_type = BubbleType.ERROR
                elif "Processing" in text:
                    bubble_type = BubbleType.INFO
                else:
                    bubble_type = BubbleType.AI_RESPONSE
                
                # Create bubble
                bubble = ModernMessageBubble(text, bubble_type, time_str)
                self.message_layout.insertWidget(self.message_layout.count() - 1, bubble)

                # Apply markdown rendering for AI responses and summaries
                if not is_sender and bubble_type in [BubbleType.AI_RESPONSE, BubbleType.FINAL_SUMMARY]:
                    bubble.finalize_rendering()

            self.message_container.setUpdatesEnabled(True)
            self.message_container.adjustSize()
            QTimer.singleShot(50, self._scroll_to_bottom)
    
    def _add_new_chat(self):
        """Add new chat"""
        name, ok = QInputDialog.getText(self, "New Chat", "Enter chat name:")
        
        if ok and name:
            # Add to UI
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, name)
            self.chat_list.addItem(item)
            
            if name not in self.chat_list_names:
                self.chat_list_names.append(name)
                self.config_manager.save_chat_list(self.chat_list_names)
            
            # Select new chat
            items = self.chat_list.findItems(name, Qt.MatchExactly)
            if items:
                self.chat_list.setCurrentItem(items[0])
                self.switch_chat_target(items[0])
    
    # ============================================================================
    # AI INITIALIZATION
    # ============================================================================
    
    def _initialize_ai(self):
        """Initialize AI"""
        api_key = self.config_manager.load_api_key()
        
        if not api_key and not (os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")):
            # Show init dialog
            QTimer.singleShot(500, self._show_init_dialog)
        else:
            # Load AI for current conversation
            self.context_manager.get_ai_for_conversation(self.current_conversation)
            
            has_api_key = bool(api_key)
            self.send_button.setEnabled(has_api_key)
            self._update_status_bar()
    
    # ============================================================================
    # DIALOGS AND ACTIONS
    # ============================================================================
    
    def _open_settings(self):
        """Open settings dialog"""
        if not self.current_conversation:
            return
        
        # Get current AI instance
        ai_instance = self.context_manager.get_ai_for_conversation(self.current_conversation)
        
        if ai_instance:
            self.settings_dialog = SettingsDialog(
                ai_instance=ai_instance,
                conversation_name=self.current_conversation
            )
        else:
            # Default config
            default_config = ConversationConfig()
            self.settings_dialog = SettingsDialog(
                current_config=default_config.__dict__,
                conversation_name=self.current_conversation
            )
        
        self.settings_dialog.sig_save_settings.connect(self._handle_settings_save)
        self.settings_dialog.show()
    
    def _handle_settings_save(self, settings: dict):
        """Handle settings save"""
        if self.current_conversation:
            # Save configuration
            self.config_manager.save_conversation_config(self.current_conversation, settings)
            
            # Update AI configuration
            ai_instance = self.context_manager.get_ai_for_conversation(self.current_conversation)
            if ai_instance:
                ai_instance.update_config(settings)
            
            # Clear and reload AI
            self.context_manager.clear_conversation(self.current_conversation)
            self.context_manager.get_ai_for_conversation(self.current_conversation)
            
            self._update_status_bar()
            QMessageBox.information(self, "Success", f"Settings updated for {self.current_conversation}")
    
    def _import_config_file(self):
        """Import configuration file"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Import Configuration File")
        file_dialog.setNameFilter("Config Files (*.json);;All Files (*)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                config_path = selected_files[0]
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    if not isinstance(config, dict):
                        raise ValueError("Invalid configuration format")
                    
                    ai_instance = self.context_manager.get_ai_for_conversation(self.current_conversation)
                    if ai_instance:
                        ai_instance.update_config(config)
                        self.config_manager.save_conversation_config(self.current_conversation, config)
                        
                        if 'mcp_paths' in config:
                            ai_instance.load_mcp_tools()
                        
                        QMessageBox.information(self, "Success",
                            f"Configuration imported for '{self.current_conversation}'")
                        
                        self._update_status_bar()
                    else:
                        QMessageBox.warning(self, "Error",
                            "No AI instance available. Please initialize AI first.")
                        
                except json.JSONDecodeError:
                    QMessageBox.warning(self, "Error", "Invalid JSON file")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to import: {str(e)}")
    
    def _clear_current_chat(self):
        """Clear current chat"""
        if self.current_conversation:
            reply = QMessageBox.question(
                self, "Clear Chat",
                f"Clear all messages in '{self.current_conversation}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Clear UI history
                self.chat_records[self.current_conversation] = []
                self._clear_message_display()
                
                # Clear AI history
                ai_instance = self.context_manager.get_ai_for_conversation(self.current_conversation)
                system_prompt = ai_instance.system_prompt if ai_instance else None
                self.history_manager.clear_history(self.current_conversation, system_prompt)
                
                QMessageBox.information(self, "Chat Cleared",
                    f"Chat history cleared for '{self.current_conversation}'.\n"
                    f"AI conversation history has also been reset.")
    
    def _export_chat_history(self):
        """Export chat history"""
        if not self.current_conversation or not self.chat_records.get(self.current_conversation):
            QMessageBox.warning(self, "Export Error", "No chat history to export")
            return
        
        desktop_path = str(Path.home() / "Desktop")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_file = f"{self.current_conversation}_{timestamp}.txt"
        default_path = os.path.join(desktop_path, default_file)
        
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Export Chat History")
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDirectory(desktop_path)
        file_dialog.selectFile(default_file)
        file_dialog.setNameFilter("Text Files (*.txt);;JSON Files (*.json);;Markdown Files (*.md)")
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                try:
                    messages = self.chat_records[self.current_conversation]
                    
                    if file_path.endswith('.json'):
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(messages, f, indent=2, ensure_ascii=False)
                    
                    elif file_path.endswith('.md'):
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(f"# Chat: {self.current_conversation}\n\n")
                            f.write(f"*Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
                            f.write("---\n\n")
                            for msg in messages:
                                sender = "**You**" if msg.get("is_sender", False) else "**AI**"
                                timestamp = msg.get("timestamp", "")
                                if timestamp:
                                    try:
                                        dt = datetime.fromisoformat(timestamp)
                                        time_str = dt.strftime("%H:%M")
                                    except:
                                        time_str = timestamp
                                else:
                                    time_str = ""
                                
                                f.write(f"{sender} ({time_str}):\n\n")
                                f.write(f"{msg.get('text', '')}\n\n")
                                f.write("---\n\n")
                    
                    else:
                        if not file_path.endswith('.txt'):
                            file_path += '.txt'
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(f"Chat: {self.current_conversation}\n")
                            f.write("=" * 50 + "\n\n")
                            for msg in messages:
                                sender = "You" if msg.get("is_sender", False) else "AI"
                                timestamp = msg.get("timestamp", "")
                                if timestamp:
                                    try:
                                        dt = datetime.fromisoformat(timestamp)
                                        time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                                    except:
                                        time_str = timestamp
                                else:
                                    time_str = ""
                                
                                f.write(f"[{time_str}] {sender}:\n")
                                f.write(f"{msg.get('text', '')}\n\n")
                    
                    QMessageBox.information(self, "Export Success", f"Chat exported to:\n{file_path}")
                    
                except Exception as e:
                    QMessageBox.warning(self, "Export Error", f"Failed to export: {e}")
    
    def _show_init_dialog(self):
        """Show initialization dialog"""
        if self.init_dialog is None:
            self.init_dialog = InitDialog()
            self.init_dialog.sig_done.connect(self._handle_init_done)
        
        self.init_dialog.show()
    
    def _handle_init_done(self, api_key: str, mcp_files: list, config_file: str):
        """Handle initialization completion"""
        if api_key:
            self.config_manager.save_api_key(api_key)
        
        # Reload AI
        self.context_manager.get_ai_for_conversation(self.current_conversation)
        
        self.send_button.setEnabled(True)
        self._update_status_bar()
    
    def _show_tools_list(self):
        """Show tools list"""
        ai_instance = self.context_manager.get_ai_for_conversation(self.current_conversation)
        
        if ai_instance:
            tools = ai_instance.get_available_tools()
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
                msg_box.setStyleSheet("""
                    QLabel { 
                        color: #E0E0E0; 
                        min-width: 400px; 
                        font-size: 12px; 
                        line-height: 1.4;
                    }
                """)
                msg_box.exec()
            else:
                QMessageBox.information(self, "Tools", "No tools available. Add MCP files in Settings.")
    
    # ============================================================================
    # EVENT HANDLERS
    # ============================================================================
    
    def closeEvent(self, event):
        """Handle window close"""
        print("[ModernChatBox] Closing application...")
        
        # Stop processing
        if self.current_state != ProcessingState.IDLE:
            self._stop_processing()
        
        # Stop worker
        if self.processing_worker and self.processing_worker.isRunning():
            self.processing_worker.stop()
            self.processing_worker.wait(2000)
        
        # Save data
        try:
            self.config_manager.save_chat_history(self.chat_records)
            self.config_manager.save_chat_list(self.chat_list_names)
            print("[ModernChatBox] Chat data saved")
        except Exception as e:
            print(f"[ModernChatBox] Save error: {e}")
        
        # Shutdown thread pool
        self.processing_thread_pool.shutdown(wait=True)
        
        event.accept()
    
    def keyPressEvent(self, event):
        """Handle key presses"""
        if event.key() == Qt.Key_Escape:
            event.ignore()
        elif event.key() == Qt.Key_N and event.modifiers() & Qt.ControlModifier:
            self._add_new_chat()
        elif event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
            self._open_settings()
        elif event.key() == Qt.Key_T and event.modifiers() & Qt.ControlModifier:
            self._show_tools_list()
        else:
            super().keyPressEvent(event)


# ============================================================================
# LEGACY COMPATIBILITY
# ============================================================================

class ChatBox(ModernChatBox):
    """Legacy compatibility alias"""
    pass


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """Main entry point for testing"""
    print("Starting Lynexus AI Chat Box...")
    
    app = QApplication(sys.argv)
    chat_box = ModernChatBox()
    chat_box.show()
    
    sys.exit(app.exec())