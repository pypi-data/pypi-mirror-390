import sys
import json

if sys.version_info[0] >= 3:
    import urllib.request as urllib_request
    import urllib.parse as urllib_parse
else:
    import urllib2 as urllib_request
    import urllib as urllib_parse

def بحث_في_جيتهب(كلمة_البحث, نوع="repositories", النتائج=10):
    try:
        كلمة_مشفرة = urllib_parse.quote(كلمة_البحث.encode('utf-8') if sys.version_info[0] < 3 else كلمة_البحث)
        
        رابط = "https://api.github.com/search/{}?q={}&per_page={}".format(نوع, كلمة_مشفرة, النتائج)
        
        طلب = urllib_request.Request(رابط)
        طلب.add_header('Accept', 'application/vnd.github.v3+json')
        
        استجابة = urllib_request.urlopen(طلب, timeout=10)
        البيانات = json.loads(استجابة.read().decode('utf-8') if sys.version_info[0] >= 3 else استجابة.read())
        
        return البيانات
    except Exception as e:
        print("خطأ في البحث: {}".format(e))
        return None

def عرض_نتائج_البحث(البيانات, نوع="repositories"):
    if not البيانات or 'items' not in البيانات:
        print("لا توجد نتائج")
        return
    
    print("\n" + "="*80)
    print("عدد النتائج: {}".format(البيانات.get('total_count', 0)))
    print("="*80 + "\n")
    
    for رقم, عنصر in enumerate(البيانات['items'], 1):
        print("النتيجة رقم {}:".format(رقم))
        print("-" * 80)
        
        if نوع == "repositories":
            print("الاسم: {}".format(عنصر.get('name', '')))
            print("المالك: {}".format(عنصر.get('owner', {}).get('login', '')))
            print("الوصف: {}".format(عنصر.get('description', 'لا يوجد وصف')))
            print("النجوم: {}".format(عنصر.get('stargazers_count', 0)))
            print("الفروع: {}".format(عنصر.get('forks_count', 0)))
            print("اللغة: {}".format(عنصر.get('language', 'غير محدد')))
            print("الرابط: {}".format(عنصر.get('html_url', '')))
            print("تاريخ الإنشاء: {}".format(عنصر.get('created_at', '')))
            print("آخر تحديث: {}".format(عنصر.get('updated_at', '')))
            
        elif نوع == "users":
            print("اسم المستخدم: {}".format(عنصر.get('login', '')))
            print("النوع: {}".format(عنصر.get('type', '')))
            print("الرابط: {}".format(عنصر.get('html_url', '')))
            
        elif نوع == "code":
            print("الملف: {}".format(عنصر.get('name', '')))
            print("المسار: {}".format(عنصر.get('path', '')))
            print("المستودع: {}".format(عنصر.get('repository', {}).get('full_name', '')))
            print("الرابط: {}".format(عنصر.get('html_url', '')))
            
        print("\n")

def تفاصيل_المستودع(اسم_المستودع):
    try:
        رابط = "https://api.github.com/repos/{}".format(اسم_المستودع)
        
        طلب = urllib_request.Request(رابط)
        طلب.add_header('Accept', 'application/vnd.github.v3+json')
        
        استجابة = urllib_request.urlopen(طلب, timeout=10)
        البيانات = json.loads(استجابة.read().decode('utf-8') if sys.version_info[0] >= 3 else استجابة.read())
        
        print("\n" + "="*80)
        print("تفاصيل المستودع: {}".format(البيانات.get('full_name', '')))
        print("="*80)
        print("الاسم: {}".format(البيانات.get('name', '')))
        print("المالك: {}".format(البيانات.get('owner', {}).get('login', '')))
        print("الوصف: {}".format(البيانات.get('description', 'لا يوجد وصف')))
        print("النجوم: {}".format(البيانات.get('stargazers_count', 0)))
        print("المتابعين: {}".format(البيانات.get('watchers_count', 0)))
        print("الفروع: {}".format(البيانات.get('forks_count', 0)))
        print("المشاكل المفتوحة: {}".format(البيانات.get('open_issues_count', 0)))
        print("اللغة الرئيسية: {}".format(البيانات.get('language', 'غير محدد')))
        print("الحجم: {} KB".format(البيانات.get('size', 0)))
        print("الرخصة: {}".format(البيانات.get('license', {}).get('name', 'غير محدد') if البيانات.get('license') else 'غير محدد'))
        print("تاريخ الإنشاء: {}".format(البيانات.get('created_at', '')))
        print("آخر تحديث: {}".format(البيانات.get('updated_at', '')))
        print("آخر دفع: {}".format(البيانات.get('pushed_at', '')))
        print("الرابط: {}".format(البيانات.get('html_url', '')))
        print("رابط الاستنساخ: {}".format(البيانات.get('clone_url', '')))
        print("="*80 + "\n")
        
        return البيانات
    except Exception as e:
        print("خطأ في جلب التفاصيل: {}".format(e))
        return None

بحث_مستودعات = lambda استعلام, عدد=10: بحث_في_جيتهب(استعلام, "repositories", عدد)
بحث_مستخدمين = lambda استعلام, عدد=10: بحث_في_جيتهب(استعلام, "users", عدد)
بحث_كود = lambda استعلام, عدد=10: بحث_في_جيتهب(استعلام, "code", عدد)
ابحث_في_جيتهب = بحث_في_جيتهب
ابحث_مستودعات = بحث_مستودعات
معلومات_المستودع = تفاصيل_المستودع
