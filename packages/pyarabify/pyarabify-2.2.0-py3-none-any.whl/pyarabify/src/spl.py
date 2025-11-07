import re

def spell_check_ar(word):
    common_mistakes = {
        'اطبغ': 'اطبع',
        'اطبغ': 'اطبع',
        'ادخل': 'ادخال',
        'طبع': 'اطبع',
        'داله': 'دالة',
        'صنف': 'صنف',
        'اذ': 'اذا',
        'لكل': 'لكل',
        'لكلل': 'لكل',
        'استدراد': 'استرداد',
        'استراد': 'استرداد',
    }
    
    if word in common_mistakes:
        return common_mistakes[word]
    return word

def تصحيح_املائي(code):
    words = re.findall(r'[\u0600-\u06FF]+', code)
    corrected_code = code
    
    for word in words:
        corrected = spell_check_ar(word)
        if corrected != word:
            corrected_code = corrected_code.replace(word, corrected)
    
    return corrected_code

def تصحيح(نص):
    return تصحيح_املائي(نص)

صحح = تصحيح_املائي
