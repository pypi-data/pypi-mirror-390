import webbrowser
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
import json

TUTORIAL_VIDEOS = {
    'python': [
        {'title': 'دورة بايثون كاملة بالعربي', 'url': 'https://www.youtube.com/watch?v=MxYLqE3Ils8'},
        {'title': 'تعلم بايثون من الصفر', 'url': 'https://www.youtube.com/watch?v=gSs18GaBs4M'},
        {'title': 'Python للمبتدئين', 'url': 'https://www.youtube.com/watch?v=eWRfhZUzrAc'},
    ],
    'numpy': [
        {'title': 'شرح NumPy بالعربي', 'url': 'https://www.youtube.com/results?search_query=numpy+arabic+tutorial'},
        {'title': 'NumPy للمبتدئين', 'url': 'https://www.youtube.com/results?search_query=numpy+شرح+بالعربي'},
    ],
    'pandas': [
        {'title': 'شرح Pandas بالعربي', 'url': 'https://www.youtube.com/results?search_query=pandas+arabic+tutorial'},
        {'title': 'تحليل البيانات بـ Pandas', 'url': 'https://www.youtube.com/results?search_query=pandas+شرح+عربي'},
    ],
    'django': [
        {'title': 'دورة Django كاملة', 'url': 'https://www.youtube.com/results?search_query=django+دورة+كاملة'},
        {'title': 'تعلم Django بالعربي', 'url': 'https://www.youtube.com/results?search_query=django+arabic'},
    ],
    'flask': [
        {'title': 'شرح Flask بالعربي', 'url': 'https://www.youtube.com/results?search_query=flask+python+عربي'},
        {'title': 'تطوير تطبيقات Flask', 'url': 'https://www.youtube.com/results?search_query=flask+tutorial+arabic'},
    ],
    'machine_learning': [
        {'title': 'تعلم الآلة بالعربي', 'url': 'https://www.youtube.com/results?search_query=machine+learning+عربي'},
        {'title': 'دورة تعلم الآلة كاملة', 'url': 'https://www.youtube.com/results?search_query=machine+learning+arabic+course'},
    ],
    'data_science': [
        {'title': 'علم البيانات بالعربي', 'url': 'https://www.youtube.com/results?search_query=data+science+عربي'},
        {'title': 'تحليل البيانات Python', 'url': 'https://www.youtube.com/results?search_query=data+analysis+python+arabic'},
    ],
}

def بحث_فيديوهات(topic):
    topic = topic.lower()
    
    if topic in TUTORIAL_VIDEOS:
        videos = TUTORIAL_VIDEOS[topic]
        print("فيديوهات {}:".format(topic))
        print("=" * 60)
        for i, video in enumerate(videos, 1):
            print("{}. {}".format(i, video['title']))
            print("   {}".format(video['url']))
        print("=" * 60)
        return videos
    else:
        search_url = "https://www.youtube.com/results?search_query={}+عربي".format(topic.replace(' ', '+'))
        print("البحث عن فيديوهات {}...".format(topic))
        print("رابط البحث: {}".format(search_url))
        webbrowser.open(search_url)
        return [{'title': 'بحث YouTube', 'url': search_url}]

def افتح_فيديو(topic, index=0):
    topic = topic.lower()
    
    if topic in TUTORIAL_VIDEOS:
        videos = TUTORIAL_VIDEOS[topic]
        if index < len(videos):
            video = videos[index]
            print("فتح فيديو: {}".format(video['title']))
            webbrowser.open(video['url'])
            return {'success': True, 'video': video}
        else:
            print("رقم الفيديو غير صحيح")
            return {'success': False, 'error': 'Invalid index'}
    else:
        بحث_فيديوهات(topic)
        return {'success': True}

def قائمة_المواضيع():
    print("المواضيع المتاحة:")
    print("=" * 60)
    for topic in sorted(TUTORIAL_VIDEOS.keys()):
        print("  - {}".format(topic))
    print("=" * 60)
    return list(TUTORIAL_VIDEOS.keys())

search_videos = بحث_فيديوهات
open_video = افتح_فيديو
list_topics = قائمة_المواضيع
