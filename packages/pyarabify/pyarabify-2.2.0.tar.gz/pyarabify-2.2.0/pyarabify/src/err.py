import json
import traceback
from pathlib import Path

class ArabicError:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.msgs_data = self._load_json('dat/msgs.json')
        
        try:
            ext_msgs = self._load_json('dat/msgs_ext.json')
            for category, mappings in ext_msgs.items():
                if category not in self.msgs_data:
                    self.msgs_data[category] = {}
                self.msgs_data[category].update(mappings)
        except FileNotFoundError:
            pass
    
    def _load_json(self, filepath):
        full_path = self.base_dir / filepath
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def translate_error(self, error):
        error_type = type(error).__name__
        error_msg = str(error)
        
        if error_type in self.msgs_data['errors']:
            template = self.msgs_data['errors'][error_type]
            return template.format(msg=error_msg)
        else:
            template = self.msgs_data['errors']['Exception']
            return template.format(msg=f"{error_type}: {error_msg}")
    
    def format_traceback(self, exc_info):
        error_type, error_value, error_traceback = exc_info
        tb_lines = traceback.format_exception(error_type, error_value, error_traceback)
        
        formatted = []
        for line in tb_lines:
            formatted.append(line)
        
        arabic_msg = self.translate_error(error_value)
        formatted.append(f"\n{arabic_msg}\n")
        
        return ''.join(formatted)
    
    def handle_error(self, error):
        return self.translate_error(error)
