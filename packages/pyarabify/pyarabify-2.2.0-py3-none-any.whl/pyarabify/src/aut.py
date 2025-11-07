import sys
import subprocess

INSTALLED_PACKAGES = set()

def تثبيت_تلقائي(package_name):
    if package_name in INSTALLED_PACKAGES:
        return True
    
    try:
        print("جاري تثبيت {} تلقائياً...".format(package_name))
        
        cmd = [sys.executable, '-m', 'pip', 'install', package_name, '--quiet']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            INSTALLED_PACKAGES.add(package_name)
            print("تم تثبيت {} بنجاح".format(package_name))
            return True
        else:
            print("فشل تثبيت {}: {}".format(package_name, stderr.decode('utf-8') if stderr else ''))
            return False
    except Exception as e:
        print("خطأ في التثبيت التلقائي: {}".format(e))
        return False

def استيراد_مع_تثبيت(package_name, module_name=None):
    if module_name is None:
        module_name = package_name
    
    try:
        __import__(module_name)
        return True
    except ImportError:
        print("المكتبة {} غير مثبتة".format(package_name))
        if تثبيت_تلقائي(package_name):
            try:
                __import__(module_name)
                return True
            except ImportError:
                return False
        return False

auto_install = تثبيت_تلقائي
import_with_install = استيراد_مع_تثبيت
