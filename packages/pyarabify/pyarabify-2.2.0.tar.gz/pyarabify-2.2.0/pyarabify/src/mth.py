import re

class محول_معادلات:
    def __init__(self):
        self.ارقام_عربية = {
            'صفر': '0', 'واحد': '1', 'اثنان': '2', 'اثنين': '2',
            'ثلاثة': '3', 'ثلاثه': '3',
            'اربعة': '4', 'اربعه': '4', 'أربعة': '4', 'أربعه': '4',
            'خمسة': '5', 'خمسه': '5',
            'ستة': '6', 'سته': '6',
            'سبعة': '7', 'سبعه': '7',
            'ثمانية': '8', 'ثمانيه': '8',
            'تسعة': '9', 'تسعه': '9',
            'عشرة': '10', 'عشره': '10',
            'عشرون': '20', 'عشرين': '20',
            'ثلاثون': '30', 'ثلاثين': '30',
            'اربعون': '40', 'اربعين': '40', 'أربعون': '40', 'أربعين': '40',
            'خمسون': '50', 'خمسين': '50',
            'ستون': '60', 'ستين': '60',
            'سبعون': '70', 'سبعين': '70',
            'ثمانون': '80', 'ثمانين': '80',
            'تسعون': '90', 'تسعين': '90',
            'مئة': '100', 'مائة': '100', 'مئه': '100', 'مائه': '100',
            'الف': '1000', 'ألف': '1000', 'الاف': '1000', 'آلاف': '1000'
        }
        
        self.عمليات = {
            'زائد': '+', 'جمع': '+', 'اضافة': '+', 'plus': '+',
            'ناقص': '-', 'طرح': '-', 'minus': '-',
            'ضرب': '*', 'مضروب': '*', 'في': '*', 'times': '*',
            'قسمة': '/', 'مقسوم': '/', 'على': '/', 'divide': '/',
            'اس': '**', 'قوة': '**', 'power': '**',
            'باقي': '%', 'modulo': '%',
        }

    def حول_نص_لرقم(self, نص):
        نص_اصلي = نص.strip()
        نص_منظف = نص_اصلي.lower()
        
        if نص_منظف.isdigit():
            return نص_منظف
        
        for عربي, رقم in self.ارقام_عربية.items():
            if نص_منظف == عربي.lower():
                return رقم
        
        if 'و' in نص_منظف:
            اجزاء = نص_منظف.split('و')
            مجموع = 0
            for جزء in اجزاء:
                جزء = جزء.strip()
                for عربي, رقم in self.ارقام_عربية.items():
                    if جزء == عربي.lower():
                        مجموع += int(رقم)
                        break
            if مجموع > 0:
                return str(مجموع)
        
        return نص_اصلي

    def حول_معادلة(self, معادلة):
        معادلة = معادلة.strip()
        
        for عربي, عملية in self.عمليات.items():
            معادلة = معادلة.replace(' ' + عربي + ' ', ' ' + عملية + ' ')
            معادلة = معادلة.replace(عربي, عملية)
        
        كلمات = معادلة.split()
        نتيجة = []
        
        for كلمة in كلمات:
            if كلمة not in ['+', '-', '*', '/', '**', '%', '(', ')']:
                رقم = self.حول_نص_لرقم(كلمة)
                نتيجة.append(رقم)
            else:
                نتيجة.append(كلمة)
        
        return ' '.join(نتيجة)

    def نفذ_معادلة(self, معادلة):
        try:
            معادلة_مترجمة = self.حول_معادلة(معادلة)
            
            import ast
            import operator
            
            ops = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.Mod: operator.mod,
                ast.USub: operator.neg,
            }
            
            def safe_eval_expr(node):
                if isinstance(node, ast.Num):
                    return node.n
                elif isinstance(node, ast.BinOp):
                    left = safe_eval_expr(node.left)
                    right = safe_eval_expr(node.right)
                    return ops[type(node.op)](left, right)
                elif isinstance(node, ast.UnaryOp):
                    operand = safe_eval_expr(node.operand)
                    return ops[type(node.op)](operand)
                else:
                    raise ValueError("عملية غير مسموحة")
            
            tree = ast.parse(معادلة_مترجمة, mode='eval')
            نتيجة = safe_eval_expr(tree.body)
            return نتيجة
        except Exception as e:
            return "خطأ في المعادلة: {}".format(str(e))

المحول = محول_معادلات()

def حول_معادلة(معادلة):
    return المحول.حول_معادلة(معادلة)

def احسب(معادلة):
    return المحول.نفذ_معادلة(معادلة)

def حول_نص_لرقم(نص):
    return المحول.حول_نص_لرقم(نص)
