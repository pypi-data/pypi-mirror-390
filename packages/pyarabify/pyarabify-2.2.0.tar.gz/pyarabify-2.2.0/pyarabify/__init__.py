__version__ = "2.2.0"
__author__ = "MERO"
__telegram__ = "QP4RM"
__github__ = "https://github.com/6x-u"

from .src.prs import ArabicParser
from .src.exe import execute, execute_file
from .src.cvt import to_english, to_arabic
from .src.err import ArabicError

from .src import git
from .src import web
from .src import ghb
from .src import hlp
from .src import mth
from .src import drw
from .src import prj
from .src import spl
from .src import lib
from .src import aut
from .src import edat
from .src import imp
from .src import doc
from .src import vid

from .src.pkg import تحميل, حمل, ثبت, نزل
from .src.aut import تثبيت_تلقائي, استيراد_مع_تثبيت
from .src.edat import enable as edat
from .src.imp import استورد_مشروع, حمل_ملف_من_github, قائمة_المشاريع_الشهيرة
from .src.doc import افتح_مستندات, قائمة_المستندات
from .src.vid import بحث_فيديوهات, افتح_فيديو, قائمة_المواضيع

__all__ = [
    'ArabicParser',
    'execute',
    'execute_file',
    'to_english',
    'to_arabic',
    'ArabicError',
    'git',
    'web',
    'ghb',
    'hlp',
    'mth',
    'drw',
    'prj',
    'spl',
    'lib',
    'aut',
    'edat',
    'imp',
    'doc',
    'vid',
    'تحميل',
    'حمل',
    'ثبت',
    'نزل',
    'تثبيت_تلقائي',
    'استيراد_مع_تثبيت',
    'استورد_مشروع',
    'حمل_ملف_من_github',
    'قائمة_المشاريع_الشهيرة',
    'افتح_مستندات',
    'قائمة_المستندات',
    'بحث_فيديوهات',
    'افتح_فيديو',
    'قائمة_المواضيع'
]
