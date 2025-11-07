import sys
import traceback

class ArabicErrorHandler:
    def __init__(self):
        self.error_map = {
            'NameError': 'خطأ: اسم غير معرف',
            'SyntaxError': 'خطأ في بناء الجملة',
            'TypeError': 'خطأ في النوع',
            'ValueError': 'خطأ في القيمة',
            'AttributeError': 'خطأ: خاصية غير موجودة',
            'KeyError': 'خطأ: مفتاح غير موجود',
            'IndexError': 'خطأ: فهرس خارج النطاق',
            'ImportError': 'خطأ في الاستيراد',
            'ZeroDivisionError': 'خطأ: قسمة على صفر',
            'FileNotFoundError': 'خطأ: ملف غير موجود',
            'ModuleNotFoundError': 'خطأ: وحدة غير موجودة',
        }
    
    def excepthook(self, exc_type, exc_value, exc_traceback):
        error_name = exc_type.__name__
        arabic_error = self.error_map.get(error_name, 'خطأ: ' + error_name)
        
        print("\n" + "=" * 60)
        print(arabic_error)
        print("=" * 60)
        
        if exc_traceback:
            tb_lines = traceback.format_tb(exc_traceback)
            for line in tb_lines:
                if 'File' in line:
                    parts = line.split(', ')
                    if len(parts) >= 2:
                        file_part = parts[0].replace('File', 'الملف:')
                        line_part = parts[1].replace('line', 'السطر:')
                        print(file_part + ', ' + line_part)
                        if len(parts) > 2:
                            print('  ' + ', '.join(parts[2:]))
                else:
                    print(line, end='')
        
        print("\nالتفاصيل:", str(exc_value))
        print("=" * 60 + "\n")

_handler = ArabicErrorHandler()

def enable():
    sys.excepthook = _handler.excepthook

def disable():
    sys.excepthook = sys.__excepthook__

edat = enable
