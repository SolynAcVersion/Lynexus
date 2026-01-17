# [file name]: config/i18n.py
import json
import os

class I18n:
    """国际化支持类"""
    
    def __init__(self, lang="en"):
        self.lang = lang
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """从文件加载翻译"""
        translations_dir = os.path.join(os.path.dirname(__file__), "translations")
        os.makedirs(translations_dir, exist_ok=True)
        
        # 默认翻译
        self.translations = {
            "en": {
                # General
                "app_name": "Lynexus",
                "status_connected": "Connected",
                "status_not_connected": "Not connected",
                "tools_available": "tools available",
                
                # Buttons
                "send": "Send",
                "settings": "Settings",
                "initialize": "Initialize",
                "load_config": "Load Config",
                "tools": "Tools",
                "new_chat": "New Chat",
                "clear_chat": "Clear Chat",
                "export_chat": "Export Chat",
                "delete_chat": "Delete Chat",
                "stop": "Stop",
                
                # Dialogs
                "initial_setup": "Initial Setup",
                "setup_title": "Lynexus AI Assistant Setup",
                "setup_desc": "Configure your AI assistant to get started",
                "select_mcp_files": "Select MCP Files",
                "start_lynexus": "Start Lynexus",
                "load_config_file": "Load Config",
                "import_config": "Load Config",
                "confirm_delete": "Confirm Delete",
                "confirm_delete_message": 'Are you sure you want to delete chat "{0}"?',
                "warning": "Warning",
                "cannot_switch_during_process": "Please wait for the current response to complete before switching conversations.",
                
                # Messages
                "type_message": "Type your message here...",
                "conversations": "Conversations",
                "quick_actions": "Quick Actions",
                
                # Chat names
                "general_chat": "Chat 1",
            },
            "zh": {
                # General
                "app_name": "Lynexus",
                "status_connected": "已连接",
                "status_not_connected": "未连接",
                "tools_available": "个工具可用",
                
                # Buttons
                "send": "发送",
                "settings": "设置",
                "initialize": "初始化",
                "load_config": "加载配置",
                "tools": "工具",
                "new_chat": "新建对话",
                "clear_chat": "清空对话",
                "export_chat": "导出对话",
                "delete_chat": "删除聊天",
                "stop": "停止",
                
                # Dialogs
                "initial_setup": "初始设置",
                "setup_title": "Lynexus AI 助手设置",
                "setup_desc": "配置你的AI助手以开始使用",
                "select_mcp_files": "选择MCP文件",
                "start_lynexus": "启动 Lynexus",
                "load_config_file": "加载配置",
                "import_config": "加载配置文件",
                "confirm_delete": "确认删除",
                "confirm_delete_message": '确定要删除聊天 "{0}" 吗？',
                "warning": "警告",
                "cannot_switch_during_process": "请等待当前响应完成后再切换对话。",
                
                # Messages
                "type_message": "在此输入消息...",
                "conversations": "对话列表",
                "quick_actions": "快速操作",
                
                # Chat names
                "general_chat": "对话 1",
            }
        }
        
        # 尝试从文件加载额外的翻译
        lang_file = os.path.join(translations_dir, f"{self.lang}.json")
        if os.path.exists(lang_file):
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    file_translations = json.load(f)
                    if self.lang in self.translations:
                        self.translations[self.lang].update(file_translations)
                    else:
                        self.translations[self.lang] = file_translations
            except:
                pass
    
    def set_language(self, lang):
        """设置语言"""
        if lang in self.translations:
            self.lang = lang
        elif os.path.exists(os.path.join("config", "translations", f"{lang}.json")):
            self.lang = lang
            self.load_translations()
    
    def tr(self, key):
        """获取翻译"""
        return self.translations.get(self.lang, {}).get(key, key)
    
    def get_supported_languages(self):
        """获取支持的语言列表"""
        return list(self.translations.keys())

# 创建全局实例
i18n = I18n("en")