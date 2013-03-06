from includes.botfunctions import regmatch, regexclude
from urllib2 import Request, urlopen
from urllib import urlencode
from HTMLParser import HTMLParser


class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = "!translate"
        self.privs = {'!translate': 1}
        self.deflang = None
        self.maxurilength = 2048

    def run(self, params, *args):
        if not params:
            return "Usage: !translate [_EN_] Text to translate"
        params = params.strip()
        if params.upper()[0:8] == '!DEFAULT':
            try:
                default = params[8:]
                default = default.strip()
                self.deflang = default
                return "Changed default translation language to " + self.deflang
            except:
                return 0
        lang = regmatch(params, self.parent.config['paramDelimiter'])
        if lang:
            text = regexclude(params, self.parent.config['paramDelimiter'])
        else:
            if self.deflang:
                lang = self.deflang
            else:
                lang = "auto"
            text = params
            if len(text) > self.maxurilength:
                text = text[:self.maxurilength]
        return translate(text, to_langage=lang)


def html_decode(s):
    codes = [
        ["'", '&#39;'],
        ['&', '&amp;'],
        ['<', '&lt;'],
        ['>', '&gt;'],
        ['"', '&quot;']]
    for code in codes:
        s = s.replace(code[1], code[0])
    return s


def translate(to_translate, to_langage="auto", langage="auto"):
    agents = {'User-Agent': "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; \
              .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)"}
    before_trans = 'class="t0">'
    link = "http://translate.google.com/m?" + urlencode({'hl': to_langage, 'sl': langage, 'q': to_translate})
    try:
        request = Request(link, headers=agents)
        page = urlopen(request).read()
    except:
        return "Sorry, Google Translate returned an error."
    result = page[page.find(before_trans) + len(before_trans):]
    result = result.split("<")[0]
    try:
        parser = HTMLParser()
        result = parser.unescape(result)
    except:
        pass
    return html_decode(result)
