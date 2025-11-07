import sys
from .prs import ArabicParser
from .err import ArabicError

def execute(arabic_code, dialect='formal', show_english=False, globals_dict=None, locals_dict=None):
    parser = ArabicParser(dialect=dialect)
    error_handler = ArabicError()
    
    try:
        english_code = parser.to_english(arabic_code)
        
        if show_english:
            print(f"الكود المترجم:\n{english_code}\n")
        
        if globals_dict is None:
            globals_dict = {}
        if locals_dict is None:
            locals_dict = {}
        
        exec(english_code, globals_dict, locals_dict)
        
        return {'status': 'success', 'english_code': english_code}
        
    except SyntaxError as e:
        arabic_error = error_handler.translate_error(e)
        print(f"خطأ في الصيغة: {arabic_error}", file=sys.stderr)
        return {'status': 'error', 'type': 'SyntaxError', 'message': arabic_error}
        
    except Exception as e:
        arabic_error = error_handler.translate_error(e)
        print(f"خطأ: {arabic_error}", file=sys.stderr)
        exc_info = sys.exc_info()
        formatted_tb = error_handler.format_traceback(exc_info)
        print(formatted_tb, file=sys.stderr)
        return {'status': 'error', 'type': type(e).__name__, 'message': arabic_error}

def execute_file(filepath, dialect='formal', show_english=False):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            arabic_code = f.read()
        
        return execute(arabic_code, dialect=dialect, show_english=show_english)
        
    except FileNotFoundError:
        error_msg = f"الملف '{filepath}' غير موجود"
        print(error_msg, file=sys.stderr)
        return {'status': 'error', 'type': 'FileNotFoundError', 'message': error_msg}
    except Exception as e:
        error_handler = ArabicError()
        arabic_error = error_handler.translate_error(e)
        print(f"خطأ: {arabic_error}", file=sys.stderr)
        return {'status': 'error', 'type': type(e).__name__, 'message': arabic_error}

def run_repl(dialect='formal'):
    parser = ArabicParser(dialect=dialect)
    error_handler = ArabicError()
    
    print("مرحباً بك في مفسر pyarabify التفاعلي")
    print(f"اللهجة الحالية: {dialect}")
    print("اكتب 'خروج()' أو 'exit()' للخروج\n")
    
    globals_dict = {}
    
    while True:
        try:
            arabic_input = input(">>> ")
            
            if arabic_input.strip() in ['خروج()', 'exit()', 'quit()', 'انهاء()']:
                print("وداعاً!")
                break
            
            if not arabic_input.strip():
                continue
            
            execute(arabic_input, dialect=dialect, globals_dict=globals_dict)
            
        except KeyboardInterrupt:
            print("\nتم المقاطعة. اكتب 'خروج()' للخروج.")
            continue
        except EOFError:
            print("\nوداعاً!")
            break
