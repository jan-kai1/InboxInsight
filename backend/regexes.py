import re

def replaceLinks(text):
    patterns = []
    linkPattern =  r'<([a-zA-Z0-9:/?=&.\-_]+)>'
    linkPattern2 = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    cssCommentPattern = r'/\*.*?\*/'
    cssPattern = r'<style.*?>.*?</style>'
    htmlPattern = r'<.*?>'
    curlyPattern = r'{.*?}'
    csspropPattern = r'[^{};]+:[^{};]+;'
    patterns.append(linkPattern)
    patterns.append(linkPattern2)
    patterns.append(cssCommentPattern)
    patterns.append(cssPattern)
    patterns.append(htmlPattern)
    patterns.append(curlyPattern)
    patterns.append(csspropPattern)
    # combine = patterns.join(f'({pattern})' for pattern in patterns)
    combine  = '|'.join(patterns)
   
    return re.sub(combine, "[link]", text)
