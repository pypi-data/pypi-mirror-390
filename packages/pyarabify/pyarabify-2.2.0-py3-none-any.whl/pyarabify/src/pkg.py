import subprocess
import sys

def تحميل(package_name):
    try:
        print("جاري تحميل المكتبة: {}...".format(package_name))
        
        if sys.version_info[0] >= 3:
            cmd = [sys.executable, '-m', 'pip', 'install', package_name]
        else:
            cmd = ['pip', 'install', package_name]
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if sys.version_info[0] >= 3:
            stdout = stdout.decode('utf-8')
            stderr = stderr.decode('utf-8')
        
        if process.returncode == 0:
            print("تم تحميل المكتبة بنجاح: {}".format(package_name))
            return True
        else:
            print("فشل تحميل المكتبة: {}".format(stderr))
            return False
    except Exception as e:
        print("خطأ في التحميل: {}".format(e))
        return False

def حمل(package_name):
    return تحميل(package_name)

def ثبت(package_name):
    return تحميل(package_name)

def نزل(package_name):
    return تحميل(package_name)

def استورد_وحمل(package_name):
    return تحميل(package_name)

def تثبيت_مكتبة(package_name):
    return تحميل(package_name)
