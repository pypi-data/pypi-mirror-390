from .prs import ArabicParser

_default_parser = None

def _get_parser():
    global _default_parser
    if _default_parser is None:
        _default_parser = ArabicParser()
    return _default_parser

def to_english(arabic_code, dialect='formal'):
    parser = ArabicParser(dialect=dialect)
    return parser.to_english(arabic_code)

def to_arabic(english_code, dialect='formal'):
    parser = ArabicParser(dialect=dialect)
    return parser.to_arabic(english_code)

def convert_file(input_file, output_file, to_language='english', dialect='formal'):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if to_language == 'english':
        converted = to_english(content, dialect)
    elif to_language == 'arabic':
        converted = to_arabic(content, dialect)
    else:
        raise ValueError(f"اللغة '{to_language}' غير مدعومة")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(converted)
    
    return converted

def add_custom_translation(arabic, english, category='keywords'):
    parser = _get_parser()
    parser.add_custom_word(arabic, english, category)
