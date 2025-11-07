LIBRARY_MAPPINGS = {
    "numpy": {
        "array": "مصفوفة",
        "zeros": "اصفار",
        "ones": "احاد",
        "arange": "نطاق_مصفوفة",
        "linspace": "فضاء_خطي",
        "reshape": "اعد_التشكيل",
        "dot": "نقطة",
        "sum": "مجموع",
        "mean": "متوسط",
        "std": "انحراف_معياري",
        "max": "اكبر",
        "min": "اصغر",
    },
    "pandas": {
        "DataFrame": "جدول_بيانات",
        "Series": "سلسلة",
        "read_csv": "اقرأ_csv",
        "read_excel": "اقرأ_excel",
        "head": "راس",
        "tail": "ذيل",
        "describe": "وصف",
        "groupby": "جمع_حسب",
        "merge": "دمج",
        "concat": "ربط",
    },
    "matplotlib.pyplot": {
        "plot": "ارسم",
        "scatter": "نثر",
        "bar": "اعمدة",
        "hist": "مدرج_تكراري",
        "pie": "دائري",
        "xlabel": "عنوان_س",
        "ylabel": "عنوان_ص",
        "title": "عنوان",
        "legend": "اسطورة",
        "show": "اعرض",
        "savefig": "احفظ_صورة",
    },
    "requests": {
        "get": "احصل",
        "post": "ارسل",
        "put": "ضع",
        "delete": "احذف",
        "request": "طلب",
        "Session": "جلسة",
    },
    "json": {
        "loads": "حمل_نص",
        "dumps": "افرغ_نص",
        "load": "حمل",
        "dump": "افرغ",
    },
    "os": {
        "path": "مسار",
        "listdir": "قائمة_المجلد",
        "mkdir": "انشئ_مجلد",
        "rmdir": "احذف_مجلد",
        "remove": "احذف",
        "rename": "اعد_تسمية",
        "getcwd": "احصل_مجلد_العمل",
        "chdir": "غير_المجلد",
    },
    "datetime": {
        "datetime": "تاريخ_وقت",
        "date": "تاريخ",
        "time": "وقت",
        "timedelta": "فرق_زمني",
        "now": "الان",
        "today": "اليوم",
    },
    "random": {
        "randint": "رقم_عشوائي_صحيح",
        "random": "عشوائي",
        "choice": "اختيار",
        "shuffle": "خلط",
        "sample": "عينة",
    },
    "math": {
        "sqrt": "جذر",
        "pow": "اس",
        "ceil": "سقف",
        "floor": "ارضية",
        "sin": "جيب",
        "cos": "جيب_تمام",
        "tan": "ظل",
        "pi": "باي",
        "e": "ثابت_اويلر",
    },
}

def get_library_mappings():
    return LIBRARY_MAPPINGS

def احصل_على_ترجمات_المكتبات():
    return LIBRARY_MAPPINGS

ترجمات_المكتبات = LIBRARY_MAPPINGS
