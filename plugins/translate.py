from urllib2 import Request, urlopen


class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = "!translate"

    def run(self, params, *args):
        if not params:
            # add usag info here
            return 0
        if params.count('[',0,2):
            lang = params[params.find('[', 0, 2) + 1:params.find(']', 1, 5)]
            text = params[params.find(']', 1, 5)+1:]
            text = text.lstrip()
        else:
            lang = "auto"
            text = params
        return translate(text, to_langage=lang)


def translate(to_translate, to_langage="auto", langage="auto"):
    '''Return the translation using google translate
    you must shortcut the langage you define (French = fr, English = en, Spanish = es, etc...)
    if you don't define anything it will detect it or use english by default
    Example:
    print(translate("salut tu vas bien?", "en"))
    hello you alright?'''
    agents = {'User-Agent':"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)"}
    before_trans = 'class="t0">'
    link = "http://translate.google.com/m?hl=%s&sl=%s&q=%s" % (to_langage, langage, to_translate.replace(" ", "+"))
    request = Request(link, headers=agents)
    page = urlopen(request).read()
    result = page[page.find(before_trans)+len(before_trans):]
    result = result.split("<")[0]
    return result
