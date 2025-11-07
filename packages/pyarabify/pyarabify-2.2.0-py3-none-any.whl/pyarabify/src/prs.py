import re
import json
import os
from pathlib import Path

class ArabicParser:
    def __init__(self, dialect='formal'):
        self.dialect = dialect
        self.base_dir = Path(__file__).parent.parent
        self.dict_data = self._load_json('dat/dict.json')
        self.dial_data = self._load_json('dat/dial.json')
        
        try:
            ext_dict = self._load_json('dat/dict_ext.json')
            for category, mappings in ext_dict.items():
                if category not in self.dict_data:
                    self.dict_data[category] = {}
                self.dict_data[category].update(mappings)
        except FileNotFoundError:
            pass
        
        self.reverse_dict = self._build_reverse_dict()
        
    def _load_json(self, filepath):
        full_path = self.base_dir / filepath
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _build_reverse_dict(self):
        reverse = {}
        for category, mappings in self.dict_data.items():
            if isinstance(mappings, dict):
                for ar, en in mappings.items():
                    reverse[ar] = en
                    reverse[en] = ar
        return reverse
    
    def parse(self, code):
        translated = code
        
        all_categories = list(self.dict_data.keys())
        for category in all_categories:
            if category in self.dict_data and isinstance(self.dict_data[category], dict):
                for arabic, english in self.dict_data[category].items():
                    pattern = r'\b' + re.escape(arabic) + r'\b'
                    translated = re.sub(pattern, english, translated)
        
        if self.dialect in self.dial_data:
            dialect_words = self.dial_data[self.dialect].get('keywords', {})
            for arabic, english in dialect_words.items():
                pattern = r'\b' + re.escape(arabic) + r'\b'
                translated = re.sub(pattern, english, translated)
        
        return translated
    
    def to_english(self, arabic_code):
        return self.parse(arabic_code)
    
    def to_arabic(self, english_code):
        translated = english_code
        
        all_categories = list(self.dict_data.keys())
        for category in all_categories:
            if category in self.dict_data and isinstance(self.dict_data[category], dict):
                items = sorted(self.dict_data[category].items(), 
                             key=lambda x: len(x[1]), reverse=True)
                for arabic, english in items:
                    pattern = r'\b' + re.escape(english) + r'\b'
                    translated = re.sub(pattern, arabic, translated)
        
        return translated
    
    def add_custom_word(self, arabic, english, category='keywords'):
        if category not in self.dict_data:
            self.dict_data[category] = {}
        self.dict_data[category][arabic] = english
        self.reverse_dict[arabic] = english
        self.reverse_dict[english] = arabic
        
        dict_path = self.base_dir / 'dat' / 'dict.json'
        with open(dict_path, 'w', encoding='utf-8') as f:
            json.dump(self.dict_data, f, ensure_ascii=False, indent=2)
    
    def set_dialect(self, dialect):
        if dialect in self.dial_data:
            self.dialect = dialect
            return True
        return False
    
    def get_available_dialects(self):
        return list(self.dial_data.keys())
