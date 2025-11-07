import subprocess
import sys

def run_git_command(command, *args):
    try:
        cmd = ['git', command] + list(args)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if sys.version_info[0] >= 3:
            stdout = stdout.decode('utf-8')
            stderr = stderr.decode('utf-8')
        
        return stdout if process.returncode == 0 else stderr
    except Exception as e:
        return str(e)

def ادفع_إلى_المستودع(*args):
    return run_git_command('push', *args)

def استنسخ_مستودع(url, *args):
    return run_git_command('clone', url, *args)

def اسحب_التحديثات(*args):
    return run_git_command('pull', *args)

def احصل_على_الحالة(*args):
    return run_git_command('status', *args)

def اضف_للتتبع(*files):
    return run_git_command('add', *files)

def احفظ_التغييرات(message, *args):
    return run_git_command('commit', '-m', message, *args)

def انشئ_فرع(branch_name, *args):
    return run_git_command('branch', branch_name, *args)

def بدل_الفرع(branch_name, *args):
    return run_git_command('checkout', branch_name, *args)

def ادمج_الفرع(branch_name, *args):
    return run_git_command('merge', branch_name, *args)

def سجل_التغييرات(*args):
    return run_git_command('log', *args)

def الفروقات(*args):
    return run_git_command('diff', *args)

def انشئ_وسم(tag_name, *args):
    return run_git_command('tag', tag_name, *args)

def الغ_التغييرات(*args):
    return run_git_command('reset', *args)

def خبئ_التغييرات(*args):
    return run_git_command('stash', *args)

def اعد_التطبيق(*args):
    return run_git_command('rebase', *args)

def اختر_التغييرات(commit_hash, *args):
    return run_git_command('cherry-pick', commit_hash, *args)

def ارجع_التغييرات(commit_hash, *args):
    return run_git_command('revert', commit_hash, *args)

def جلب_التحديثات(*args):
    return run_git_command('fetch', *args)

def الفروع_البعيدة(*args):
    return run_git_command('remote', *args)

def اظهر_التفاصيل(*args):
    return run_git_command('show', *args)

ادفع = ادفع_إلى_المستودع
ارسل = ادفع_إلى_المستودع
رفع = ادفع_إلى_المستودع
استنسخ = استنسخ_مستودع
انسخ_مستودع = استنسخ_مستودع
اسحب = اسحب_التحديثات
جلب_تحديثات = اسحب_التحديثات
حالة = احصل_على_الحالة
وضع = احصل_على_الحالة
اضف_ملف = اضف_للتتبع
تتبع = اضف_للتتبع
احفظ = احفظ_التغييرات
سجل = احفظ_التغييرات
فرع = انشئ_فرع
فرع_جديد = انشئ_فرع
انتقل_الفرع = بدل_الفرع
دمج = ادمج_الفرع
ادمج = ادمج_الفرع
السجل = سجل_التغييرات
التاريخ = سجل_التغييرات
قارن = الفروقات
الاختلافات = الفروقات
وسم = انشئ_وسم
علامة = انشئ_وسم
الغاء = الغ_التغييرات
ارجع = الغ_التغييرات
خبأ = خبئ_التغييرات
احفظ_مؤقتاً = خبئ_التغييرات
اعادة_الأساس = اعد_التطبيق
اختر = اختر_التغييرات
تراجع = ارجع_التغييرات
جلب = جلب_التحديثات
المستودعات_البعيدة = الفروع_البعيدة
تفاصيل = اظهر_التفاصيل
