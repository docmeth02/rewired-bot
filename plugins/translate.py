from includes.botfunctions import regmatch, regexclude
from urllib2 import Request, urlopen
from urllib import urlencode
from HTMLParser import HTMLParser


class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = ["!translate", "!tr"]
        self.privs = {'!translate': 1}
        self.deflang = 'en'
        self.auto = {}
        self.maxurilength = 2048
        self.parent.librewired.subscribe(300, self.checkChat)
        self.parent.librewired.subscribe(301, self.checkChat)

    def run(self, params, *args):
        if not params:
            return "Usage: !translate [_EN_] Text to translate"
        params = params.strip()
        if params.upper()[0:7] == '!DEFAULT':
            try:
                default = params[7:]
                default = default.strip()
                self.deflang = default
                return "Changed default translation language to " + self.deflang
            except:
                return 0
        if params.upper()[0:4] == 'AUTO':
            #(['1', '544', '!tr auto de'],)
            try:
                lang = params[4:].strip()
            except Exception as e:
                self.parent.logger.error("auto translate: %s", e)
                return 0
            if int(args[0][0]) in self.auto and lang:
                # change
                self.auto[int(args[0][1])] = lang
                return "Changed auto-translate to '%s'" % lang
            if lang:
                # add
                self.auto[int(args[0][1])] = lang
                return "auto-translate to '%s' activated" % lang
            # remove
            try:
                del(self.auto[int(args[0][1])])
            except Exception as e:
                self.parent.logger.error("auto translate: %s", e)
            return "auto-translate deactivated"

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

    def checkChat(self, chat):
        if not len(self.auto):
            return 0
        msg = chat.msg
        if not int(msg[1]) in self.auto or '!' in msg[2][:1]:
            return 0
        if not int(msg[1]) == self.parent.librewired.id:
            translation = translate(msg[2], self.auto[int(msg[1])])
            if translation:
                self.parent.librewired.sendChat(int(msg[0]), translation)
            return 0
        return 0


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
        return 0
    result = page[page.find(before_trans) + len(before_trans):]
    result = result.split("<")[0]
    try:
        parser = HTMLParser()
        result = parser.unescape(result)
    except:
        pass
    return html_decode(result)
