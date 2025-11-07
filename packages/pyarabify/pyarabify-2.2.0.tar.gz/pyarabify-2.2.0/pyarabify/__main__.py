import sys
import argparse

def main():
    parser = argparse.ArgumentParser(
        prog='pyarabify',
        description='مكتبة Python للبرمجة بالعربية - الإصدار 2.2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
المطور: MERO
Telegram: @QP4RM
GitHub: https://github.com/6x-u

الاستخدام:
  pyarabify program.py              تنفيذ ملف عربي
  pyarabify ترجم hello             ترجمة نص للعربية
  pyarabify مثال الحلقات           عرض مثال
  pyarabify اختبر                  اختبار المكتبة
  pyarabify بحث numpy              البحث في GitHub
  pyarabify انشئ_مشروع آلة_حاسبة   إنشاء مشروع جاهز

المميزات الجديدة في 2.2.0:
  - 6 لهجات عربية (فصحى، مختصر، مصري، خليجي، فلسطيني، عراقي)
  - البحث في GitHub
  - مساعد ذكي للإجابة على الأسئلة
  - تحويل المعادلات العربية لأكواد
  - دعم الرسوميات (Turtle)
  - مولد المشاريع الجاهزة
  - تصحيح إملائي تلقائي
  - دعم كامل لمكتبات Python الشهيرة

للمزيد: https://github.com/6x-u/pyarabify
'''
    )
    
    parser.add_argument('command', nargs='?', help='الأمر أو ملف Python للتنفيذ')
    parser.add_argument('args', nargs='*', help='معاملات الأمر')
    parser.add_argument('--dialect', default='formal', 
                       choices=['formal', 'short', 'egyptian', 'gulf', 'palestinian', 'iraqi'],
                       help='اللهجة المستخدمة')
    parser.add_argument('--show-english', action='store_true',
                       help='عرض الكود المترجم للإنجليزية')
    parser.add_argument('--version', action='version',
                       version='pyarabify 2.2.0')
    
    args_parsed = parser.parse_args()
    
    if not args_parsed.command:
        from pyarabify.src.exe import run_repl
        run_repl(dialect=args_parsed.dialect)
        return
    
    cmd = args_parsed.command
    cmd_args = args_parsed.args
    
    if cmd == 'ترجم' or cmd == 'translate':
        if not cmd_args:
            print("الاستخدام: pyarabify ترجم <نص>")
            return
        text = ' '.join(cmd_args)
        from pyarabify import to_arabic
        result = to_arabic(text, dialect=args_parsed.dialect)
        print(result)
        
    elif cmd == 'مثال' or cmd == 'example':
        if not cmd_args:
            print("الأمثلة المتاحة: الحلقات، الدوال، الشروط، القوائم، الأصناف")
            return
        example_type = cmd_args[0]
        show_example(example_type)
        
    elif cmd == 'اختبر' or cmd == 'test':
        run_tests()
        
    elif cmd == 'بحث' or cmd == 'search':
        if not cmd_args:
            print("الاستخدام: pyarabify بحث <كلمة_البحث>")
            return
        search_query = ' '.join(cmd_args)
        from pyarabify import ghb
        print("جاري البحث في GitHub عن: {}...".format(search_query))
        results = ghb.بحث_في_جيتهب(search_query, "repositories", 5)
        ghb.عرض_نتائج_البحث(results, "repositories")
        
    elif cmd == 'انشئ_مشروع' or cmd == 'create_project':
        if not cmd_args:
            from pyarabify import prj
            prj.قائمة_المشاريع()
            return
        project_name = cmd_args[0]
        from pyarabify import prj
        prj.انشئ_مشروع(project_name)
        
    elif cmd == 'اسأل' or cmd == 'ask':
        if not cmd_args:
            print("الاستخدام: pyarabify اسأل <سؤالك>")
            return
        question = ' '.join(cmd_args)
        from pyarabify import hlp
        answer = hlp.اسأل(question)
        print(answer)
        
    elif cmd == 'استورد_مشروع' or cmd == 'import_project':
        if not cmd_args:
            print("الاستخدام: pyarabify استورد_مشروع <اسم_المشروع>")
            return
        project_name = ' '.join(cmd_args)
        from pyarabify import imp
        result = imp.استورد_مشروع(project_name)
        if result.get('success'):
            print("تم الاستيراد بنجاح في: {}".format(result.get('path')))
    
    elif cmd == 'docs' or cmd == 'مستندات':
        if not cmd_args:
            from pyarabify import doc
            doc.قائمة_المستندات()
            return
        library_name = cmd_args[0]
        from pyarabify import doc
        doc.افتح_مستندات(library_name)
    
    elif cmd == 'videos' or cmd == 'فيديوهات':
        if not cmd_args:
            from pyarabify import vid
            vid.قائمة_المواضيع()
            return
        topic = ' '.join(cmd_args)
        from pyarabify import vid
        vid.بحث_فيديوهات(topic)
        
    elif cmd.endswith('.py'):
        from pyarabify import execute_file
        execute_file(cmd, dialect=args_parsed.dialect, show_english=args_parsed.show_english)
    else:
        from pyarabify import execute_file
        execute_file(cmd, dialect=args_parsed.dialect, show_english=args_parsed.show_english)

def show_example(example_type):
    examples = {
        'الحلقات': '''
لكل رقم في نطاق(5):
    اطبع(رقم)
''',
        'الدوال': '''
دالة جمع(أ, ب):
    ارجع أ + ب

النتيجة = جمع(5, 3)
اطبع("النتيجة:", النتيجة)
''',
        'الشروط': '''
العمر = 18
اذا العمر >= 18:
    اطبع("بالغ")
والا:
    اطبع("قاصر")
''',
        'القوائم': '''
الأرقام = [1, 2, 3, 4, 5]
اطبع("الطول:", طول(الأرقام))
لكل رقم في الأرقام:
    اطبع(رقم)
''',
        'الأصناف': '''
صنف طالب:
    دالة __init__(الذات, الاسم):
        الذات.الاسم = الاسم
    
    دالة اهلا(الذات):
        اطبع("مرحباً", الذات.الاسم)

احمد = طالب("أحمد")
احمد.اهلا()
'''
    }
    
    if example_type in examples:
        print("=" * 60)
        print("مثال: {}".format(example_type))
        print("=" * 60)
        print(examples[example_type])
        print("=" * 60)
    else:
        print("مثال غير موجود. الأمثلة المتاحة: الحلقات، الدوال، الشروط، القوائم، الأصناف")

def run_tests():
    print("=" * 60)
    print("اختبار مكتبة pyarabify 2.2.0")
    print("=" * 60)
    
    from pyarabify import execute, to_english, to_arabic
    
    print("\n1. اختبار الترجمة من العربية للإنجليزية...")
    arabic_code = 'اطبع("مرحباً")'
    english_code = to_english(arabic_code)
    print("   العربي: {}".format(arabic_code))
    print("   الإنجليزي: {}".format(english_code))
    print("   النتيجة: نجح")
    
    print("\n2. اختبار الترجمة من الإنجليزية للعربية...")
    english_code = 'print("Hello")'
    arabic_code = to_arabic(english_code)
    print("   الإنجليزي: {}".format(english_code))
    print("   العربي: {}".format(arabic_code))
    print("   النتيجة: نجح")
    
    print("\n3. اختبار تنفيذ كود عربي...")
    code = 'اطبع("اختبار التنفيذ نجح!")'
    result = execute(code)
    print("   النتيجة: {}".format(result['status']))
    
    print("\n4. اختبار المساعد الذكي...")
    from pyarabify import hlp
    answer = hlp.اسأل("ما فائدة range")
    print("   السؤال: ما فائدة range")
    print("   الجواب: {}".format(answer))
    
    print("\n5. اختبار تحويل المعادلات...")
    from pyarabify import mth
    equation = "خمسة زائد ثلاثة"
    result = mth.احسب(equation)
    print("   المعادلة: {}".format(equation))
    print("   النتيجة: {}".format(result))
    
    print("\n" + "=" * 60)
    print("جميع الاختبارات نجحت!")
    print("=" * 60)

if __name__ == '__main__':
    main()
