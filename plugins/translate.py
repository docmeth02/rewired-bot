from re import findall
from urllib2 import Request, urlopen
from urllib import urlencode
from HTMLParser import HTMLParser


class rewiredBotPlugin():
    """Google translate plugin"""
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = ["!translate", "!tr", "!listlang"]
        self.privs = {'!translate': 1, '!tr': 1, '!listlang': 1}
        self.deflang = 'en'
        self.auto = {}
        self.maxurilength = 2048
        self.parent.librewired.subscribe(300, self.checkChat)
        self.parent.librewired.subscribe(301, self.checkChat)

        self.validLang = {
            #https://developers.google.com/translate/v2/using_rest
            'af': 'Afrikaans',
            'sq': 'Albanian',
            'ar': 'Arabic',
            'az': 'Azerbaijani',
            'eu': 'Basque',
            'bn': 'Bengali',
            'be': 'Belarusian',
            'bg': 'Bulgarian',
            'ca': 'Catalan',
            'zh-cn': 'Chinese Simplified',
            'zh_tw': 'Chinese Traditional',
            'hr': 'Croatian',
            'cs': 'Czech',
            'da': 'Danish',
            'nl': 'Dutch',
            'en': 'English',
            'eo': 'Esperanto',
            'et': 'Estonian',
            'tl': 'Filipino',
            'fi': 'Finnish',
            'fr': 'French',
            'gl': 'Galician',
            'ka': 'Georgian',
            'de': 'German',
            'el': 'Greek',
            'gu': 'Gujarati',
            'ht': 'Haitian Creole',
            'iw': 'Hebrew',
            'hi': 'Hindi',
            'hu': 'Hungarian',
            'is': 'Icelandic',
            'id': 'Indonesian',
            'ga': 'Irish',
            'it': 'Italian',
            'ja': 'Japanese',
            'kn': 'Kannada',
            'ko': 'Korean',
            'la': 'Latin',
            'lv': 'Latvian',
            'lt': 'Lithuanian',
            'mk': 'Macedonian',
            'ms': 'Malay',
            'mt': 'Maltese',
            'no': 'Norwegian',
            'fa': 'Persian',
            'pl': 'Polish',
            'pt': 'Portuguese',
            'ro': 'Romanian',
            'ru': 'Russian',
            'sr': 'Serbian',
            'sk': 'Slovak',
            'sl': 'Slovenian',
            'es': 'Spanish',
            'sw': 'Swahili',
            'sv': 'Swedish',
            'ta': 'Tamil',
            'te': 'Telugu',
            'th': 'Thai',
            'tr': 'Turkish',
            'uk': 'Ukrainian',
            'ur': 'Urdu',
            'vi': 'Vietnamese',
            'cy': 'Welsh',
            'yi': 'Yiddish'}

    def run(self, params, *args):
        """!translate: Usage: !translate (lc|auto|default) text
        Translate given text to default language or language
        set by two letter language code (lc). Get all available
        language codes by typing !listlang into chat.
        !translate de Bot is awesome
        translate "Bot is awesome" to german
        !translate auto de
        will enable auto translation for your user. Everything you
        say in chat will be auto translated(to german in this case).
        !translate auto off - stops auto translation for your user.
        !translate default de - change default language for translations
        to german(global default is english).
        ___"""
        command = self.parent.parse_command(args[0][2])
        if command.lower() == 'listlang':
            msg = "\n".join(['%s : %s' % (key, value) for (key, value) in self.validLang.items()])
            self.parent.librewired.sendPrivateMsg(int(args[0][1]), '!translate valid languages:\n%s' % msg)
            return 0

        if not params:
            return "Usage: !translate en Text to translate\n type !listlang for language code list"
        params = params.strip()

        if params.upper()[0:4] == 'AUTO':
            try:
                lang = params[4:].strip().lower()
            except Exception as e:
                self.parent.logger.error("auto translate: %s", e)
                return 0

            if lang == 'disable' or lang == 'off':
                # remove
                try:
                    del(self.auto[int(args[0][1])])
                except Exception as e:
                    self.parent.logger.error("auto translate: %s", e)
                return "auto-translate deactivated"
            if not lang in self.validLang.keys():
                return "No such language: %s" % lang
            if int(args[0][0]) in self.auto and lang:
                # change
                self.auto[int(args[0][1])] = lang
                return "auto-translate to %s" % self.validLang[lang]
            if lang:
                # add
                self.auto[int(args[0][1])] = lang
                return "auto-translate to %s" % self.validLang[lang]
            return 0

        regex = '\A(default|%s){1} (.*)' % '|'.join(self.validLang.keys())
        langparam = findall(regex, params)
        if len(langparam):
            lang, text = langparam[0]
        else:
            if self.deflang:
                lang = self.deflang
            else:
                lang = "auto"
            text = params
            if len(text) > self.maxurilength:
                text = text[:self.maxurilength]

        if lang.lower() == 'default':
            deflang = text.lower().strip()
            if not deflang in self.validLang.keys():
                    return "No such language %s" % deflang
            self.deflang = deflang
            return "Changed default translation language to %s" % self.validLang[deflang]

        return translate(text, to_langage=lang)

    def checkChat(self, chat):
        if not len(self.auto):
            return 0
        msg = chat.msg
        if not int(msg[1]) in self.auto or '!' in msg[2][:1]:
            return 0
        if not int(msg[1]) == self.parent.librewired.id:
            user = self.parent.librewired.userlist[int(msg[1])]
            translation = translate(msg[2], self.auto[int(msg[1])])
            if translation:
                self.parent.librewired.sendChat(int(msg[0]), "%s: %s" % (user.nick, translation), 1)
            return 0
        return 0


def decode(s):
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
    result = decode(result)
    return result
