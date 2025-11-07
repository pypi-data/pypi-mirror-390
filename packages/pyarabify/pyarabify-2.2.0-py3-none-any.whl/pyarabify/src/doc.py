import webbrowser

DOCS_LINKS = {
    'python': 'https://docs.python.org/3/',
    'numpy': 'https://numpy.org/doc/stable/',
    'pandas': 'https://pandas.pydata.org/docs/',
    'matplotlib': 'https://matplotlib.org/stable/contents.html',
    'requests': 'https://requests.readthedocs.io/',
    'flask': 'https://flask.palletsprojects.com/',
    'django': 'https://docs.djangoproject.com/',
    'fastapi': 'https://fastapi.tiangolo.com/',
    'tensorflow': 'https://www.tensorflow.org/api_docs',
    'pytorch': 'https://pytorch.org/docs/',
    'scikit-learn': 'https://scikit-learn.org/stable/documentation.html',
    'opencv': 'https://docs.opencv.org/',
    'pillow': 'https://pillow.readthedocs.io/',
    'beautifulsoup': 'https://www.crummy.com/software/BeautifulSoup/bs4/doc/',
    'selenium': 'https://selenium-python.readthedocs.io/',
    'sqlalchemy': 'https://docs.sqlalchemy.org/',
    'asyncio': 'https://docs.python.org/3/library/asyncio.html',
    'threading': 'https://docs.python.org/3/library/threading.html',
    'multiprocessing': 'https://docs.python.org/3/library/multiprocessing.html',
    'json': 'https://docs.python.org/3/library/json.html',
    'csv': 'https://docs.python.org/3/library/csv.html',
    'datetime': 'https://docs.python.org/3/library/datetime.html',
    'math': 'https://docs.python.org/3/library/math.html',
    'random': 'https://docs.python.org/3/library/random.html',
    're': 'https://docs.python.org/3/library/re.html',
    'os': 'https://docs.python.org/3/library/os.html',
    'sys': 'https://docs.python.org/3/library/sys.html',
    'pathlib': 'https://docs.python.org/3/library/pathlib.html',
}

def افتح_مستندات(library_name):
    library_name = library_name.lower()
    
    if library_name in DOCS_LINKS:
        url = DOCS_LINKS[library_name]
        print("فتح مستندات {}...".format(library_name))
        print("الرابط: {}".format(url))
        webbrowser.open(url)
        return {'success': True, 'url': url}
    else:
        print("المكتبة '{}' غير موجودة في القائمة".format(library_name))
        print("المكتبات المتاحة:")
        for lib in sorted(DOCS_LINKS.keys()):
            print("  - {}".format(lib))
        return {'success': False, 'error': 'Library not found'}

def قائمة_المستندات():
    print("المكتبات المتاحة:")
    print("=" * 60)
    for lib in sorted(DOCS_LINKS.keys()):
        print("  - {}".format(lib))
    print("=" * 60)
    print("الاستخدام: pyarabify docs <اسم_المكتبة>")
    return list(DOCS_LINKS.keys())

open_docs = افتح_مستندات
list_docs = قائمة_المستندات
