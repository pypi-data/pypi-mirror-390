import sys
import os
import subprocess
try:
    from urllib.request import urlopen, urlretrieve
except ImportError:
    from urllib2 import urlopen
    from urllib import urlretrieve

def استورد_مشروع(project_name, output_dir="."):
    try:
        search_url = "https://api.github.com/search/repositories?q={}&sort=stars&order=desc".format(project_name)
        
        response = urlopen(search_url)
        data = response.read()
        
        if sys.version_info[0] >= 3:
            data = data.decode('utf-8')
        
        import json
        results = json.loads(data)
        
        if results.get('items') and len(results['items']) > 0:
            repo = results['items'][0]
            repo_url = repo['clone_url']
            repo_name = repo['name']
            
            target_path = os.path.join(output_dir, repo_name)
            
            print("استيراد مشروع: {}".format(repo['full_name']))
            print("الوصف: {}".format(repo.get('description', 'لا يوجد وصف')))
            print("النجوم: {}".format(repo.get('stargazers_count', 0)))
            print("المسار: {}".format(target_path))
            
            cmd = ['git', 'clone', repo_url, target_path]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                print("تم الاستيراد بنجاح!")
                return {
                    'success': True,
                    'path': target_path,
                    'name': repo_name,
                    'full_name': repo['full_name'],
                    'url': repo['html_url']
                }
            else:
                print("فشل الاستيراد: {}".format(stderr.decode('utf-8') if stderr else ''))
                return {'success': False, 'error': 'فشل git clone'}
        else:
            print("لم يتم العثور على مشاريع")
            return {'success': False, 'error': 'لم يتم العثور على مشاريع'}
            
    except Exception as e:
        print("خطأ: {}".format(str(e)))
        return {'success': False, 'error': str(e)}

def حمل_ملف_من_github(repo, file_path, output_path=None):
    try:
        raw_url = "https://raw.githubusercontent.com/{}/main/{}".format(repo, file_path)
        
        if output_path is None:
            output_path = os.path.basename(file_path)
        
        print("تحميل: {}".format(raw_url))
        urlretrieve(raw_url, output_path)
        print("تم التحميل: {}".format(output_path))
        
        return {'success': True, 'path': output_path}
    except Exception as e:
        try:
            raw_url = "https://raw.githubusercontent.com/{}/master/{}".format(repo, file_path)
            urlretrieve(raw_url, output_path)
            print("تم التحميل: {}".format(output_path))
            return {'success': True, 'path': output_path}
        except Exception as e2:
            print("خطأ: {}".format(str(e2)))
            return {'success': False, 'error': str(e2)}

def قائمة_المشاريع_الشهيرة(language="python", count=10):
    try:
        search_url = "https://api.github.com/search/repositories?q=language:{}&sort=stars&order=desc&per_page={}".format(language, count)
        
        response = urlopen(search_url)
        data = response.read()
        
        if sys.version_info[0] >= 3:
            data = data.decode('utf-8')
        
        import json
        results = json.loads(data)
        
        projects = []
        for repo in results.get('items', []):
            projects.append({
                'name': repo['name'],
                'full_name': repo['full_name'],
                'description': repo.get('description', ''),
                'stars': repo.get('stargazers_count', 0),
                'url': repo['html_url']
            })
        
        return projects
    except Exception as e:
        print("خطأ: {}".format(str(e)))
        return []

import_project = استورد_مشروع
download_file = حمل_ملف_من_github
list_popular = قائمة_المشاريع_الشهيرة
