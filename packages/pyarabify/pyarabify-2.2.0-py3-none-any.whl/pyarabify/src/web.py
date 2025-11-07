import webbrowser
import sys

try:
    import urllib.request as urllib_request
    import urllib.error as urllib_error
except ImportError:
    import urllib2 as urllib_request
    import urllib2 as urllib_error

def افتح_رابط(url, new=0, autoraise=True):
    try:
        if not url.startswith(('http://', 'https://', 'file://', 'ftp://')):
            url = 'https://' + url
        return webbrowser.open(url, new=new, autoraise=autoraise)
    except Exception as e:
        print("خطأ في فتح الرابط: {}".format(e))
        return False

def الحصول(url, timeout=30):
    try:
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'https://' + url
        
        if sys.version_info[0] >= 3:
            response = urllib_request.urlopen(url, timeout=timeout)
            content = response.read().decode('utf-8')
        else:
            response = urllib_request.urlopen(url, timeout=timeout)
            content = response.read()
        
        return content
    except Exception as e:
        print("خطأ في الحصول على المحتوى: {}".format(e))
        return None

def تحميل(url, filename=None, timeout=30):
    try:
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'https://' + url
        
        if filename is None:
            filename = url.split('/')[-1]
            if not filename:
                filename = 'downloaded_file'
        
        if sys.version_info[0] >= 3:
            urllib_request.urlretrieve(url, filename)
        else:
            response = urllib_request.urlopen(url, timeout=timeout)
            with open(filename, 'wb') as f:
                f.write(response.read())
        
        print("تم التحميل: {}".format(filename))
        return filename
    except Exception as e:
        print("خطأ في التحميل: {}".format(e))
        return None

def احصل_على_محتوى(url, **kwargs):
    return الحصول(url, **kwargs)

def نزل(url, **kwargs):
    return تحميل(url, **kwargs)

def حمل(url, **kwargs):
    return تحميل(url, **kwargs)

def احصل(url, **kwargs):
    return الحصول(url, **kwargs)

def افتح_URL(url, **kwargs):
    return افتح_رابط(url, **kwargs)

def تصفح(url, **kwargs):
    return افتح_رابط(url, **kwargs)

def افتح_موقع(url, **kwargs):
    return افتح_رابط(url, **kwargs)

def افتح_في_متصفح(url, **kwargs):
    return افتح_رابط(url, **kwargs)

def افتح_في_نافذة_جديدة(url):
    return افتح_رابط(url, new=1)

def افتح_في_تبويب_جديد(url):
    return افتح_رابط(url, new=2)

افتح_في_نفس_النافذة = افتح_رابط
افتح_رابط_ويب = افتح_رابط
عرض_موقع = افتح_رابط
زر_موقع = افتح_رابط
اذهب_الى = افتح_رابط
انتقل_الى = افتح_رابط
استرجع = الحصول
جلب_محتوى = الحصول
