# -*- coding: UTF-8 -*-
from urllib2 import urlopen, HTTPError
from HTMLParser import HTMLParser
#from difflib import get_close_matches
from xml.dom import minidom
from sys import exit
import datetime
import re
import tmdb3
import tvdb_api
tmdb3.set_key('50d210cbe126f116d13b83239d0f18d0')
tmdb3.set_locale('en', 'US')


class rewiredBotPlugin():
    def __init__(self, parent, *args):
        self.parent = parent
        self.defines = "!imdb"
        self.privs = {'!imdb': 1}

    def run(self, params, *args):
        if not params:
            return "Usage: !imdb SearchText"
        params = params.strip()
        chatid = int(args[0][0])
        # find imdbid
        imdbid = 0
        if re.findall(r'(tt[0-9]+)', params):
            imdbid = re.findall(r'(tt[0-9]+)', params)[-1]

        # check for year in search string
        years = re.findall(r'(\d{4})', params)
        if len(years):
            try:
                year = years[-1]
                params = params.replace("(%s)" % year, '')
                params = params.replace(str(year), '')
            except:
                year = None
        else:
            year = None
        params = params.strip()
        if not imdbid:
            tvshow = False
            tvshow = searchTVShow(params, year=year)
            results = searchMovies(params, year=year)
            if not results and not tvshow:
                return "No result: %s" % params
            if tvshow:
                line = "%s (TV Show) - http://www.imdb.com/title/%s" % (tvshow['seriesname'], tvshow['imdb_id'])
                line = html_decode(line)
                if line:
                    self.parent.librewired.sendChat(chatid, line)
                if not results:
                    return 0
            if len(results) > 1:
                count = 0
                for aresult in results:
                    if count >= 10:
                        break
                    imdb = aresult.imdb
                    year = aresult.releasedate
                    if type(aresult.releasedate) == datetime.date:
                        year = aresult.releasedate.strftime("%Y")
                    if imdb:
                        line = "%s (%s) - http://www.imdb.com/title/%s" %\
                               (aresult.title, year, imdb)
                        line = html_decode(line)
                        if line:
                            self.parent.librewired.sendChat(chatid, line)
                    count += 1
                return 0
        else:
            results = [lookupMovie(imdbid)]
        if type(results[-1]) is int:
            #try tvshow
            tvshow = getTVbyIMDB(imdbid)
            if tvshow:
                return outputTVShow(tvshow, chatid, self.parent.librewired)
            return "No results"
        return outputMovie(results[0], chatid, self.parent.librewired)


def outputMovie(results, chatid, librewired, link=True):
    if type(results) is list:
        results = results[0]
    result = formatOutput(results, link)
    data = result['text']
    image = result['image']
    if data and image:
        image = fetchPoster(image)
        if image:
            librewired.sendChatImage(chatid, '%image%\n' + data, image)
            return 0
    librewired.sendChat(chatid, data)
    return 0


def outputTVShow(results, chatid, librewired, link=True):
    result = formatTVOutput(results, link)
    data = result['text']
    #image = result['image']
    image = 0
    if data and image:
        image = fetchPoster(image)
        if image:
            librewired.sendChat(chatid, html_decode(data))
            #librewired.sendChatImage(chatid, '%image%\n' + data, image)
            return 0
    librewired.sendChat(chatid, html_decode(data))
    return 0


def parseResult(aresult):
    result = {}
    fields = ['title', 'year', 'rating', 'imdb_url']
    for afield in fields:
        try:
            result[afield] = str(html_decode(aresult[afield]))
        except:
            print "Nope: %s " % afield
            result[afield] = "n/a"
    return result


def lookupMovie(imdbid):
    try:
        movie = tmdb3.Movie.fromIMDB(imdbid)
    except Exception as e:
        return 0
    if not movie:
        return 0
    return movie


def formatOutput(movie, link=True):
    try:
        text = ""
        year = movie.releasedate
        releasedate = movie.releasedate
        if type(movie.releasedate) == datetime.date:
            year = movie.releasedate.strftime("%Y")
            releasedate = movie.releasedate.strftime("%Y")
        text += "%s (%s) | Ratings: %s/10\n" % (movie.title, year, movie.userrating)
        text += "Runtime: %s minutes. | Released: %s\n" % (movie.runtime, releasedate)
        directors, actors = ([], [])
        for aperson in movie.crew:
            if aperson.job == 'Director':
                directors.append(aperson.name)
        for aperson in movie.cast:
            if len(actors) >= 5:
                break
            actors.append(aperson.name)
        if directors:
            text += "Directors: %s" % html_decode(concatList(directors, ' / '))
        if directors and actors:
            text += ' | '
        if actors:
            text += "Actors: %s" % html_decode(concatList(actors, ' / '))
        if actors or directors:
            text += "\n"
        text += "Plot: %s" % movie.overview
        if movie.imdb and link:
            text += "\nLink: http://www.imdb.com/title/%s" % movie.imdb
    except Exception as e:
        print e
        text = 0

    image = None
    if movie.poster:
        try:
            size = movie.poster.sizes()[0]
            image = movie.poster.geturl(size)
        except Exception as e:
            print "Poster Nope: %s" % e
            image = None
    return {'text': html_decode(text), 'image': image}


def fetchPoster(url):
    if not url:
        return 0
    try:
        typ = url[len(url)-3:len(url)]
        imagedata = urlopen(url).read()
        if imagedata:
            return {'data': imagedata, 'type': typ}
    except:
        print "Fetch Fail"
        return 0


def concatList(list, delimiter):
    text = ""
    for aitem in list:
        text += html_decode(aitem) + str(delimiter)
    return text[0:len(text) - len(delimiter)]


def html_decode(s):
    try:
        s = unicode(s, 'replace')
    except Exception as e:
        pass
    try:
        s = s.encode('UTF-8', 'xmlcharrefreplace')
    except Exception as e:
        print "Error when trying to convert string to utf-8"
        return 0
    codes = [
        ["'", '&#39;'],
        ['&', '&amp;'],
        ['<', '&lt;'],
        ['>', '&gt;'],
        ['"', '&quot;']]
    for code in codes:
        s = s.replace(code[1], code[0])
    try:
        parser = HTMLParser()
        result = parser.unescape(s)
    except:
        pass
    return s


def searchMovies(title, year=None):
    try:
        results = tmdb3.searchMovie(title, year=year, locale=tmdb3.get_locale())
    except Exception as e:
        print "NOPE: %s" % e
        return 0

    if not len(results):
        return 0
    return results


def searchTVShow(title, year=None):
        tvapi = tvdb_api.Tvdb()
        searchtitle = title
        if year:
            searchtitle += " (%s)" % year
        try:
            show = tvapi[str(searchtitle)]
        except Exception as e:
            return 0
        return show


def getTVbyIMDB(imdid):
    tvapi = tvdb_api.Tvdb()
    data = tvapi._loadUrl('http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=%s' % imdid)
    if data:
        try:
            xml = minidom.parseString(data)
            tvdbid = xml.getElementsByTagName('id')
            tvdbid = int(tvdbid[-1].firstChild.data.strip())
            show = tvapi[tvdbid]
        except:
            print "IMDB -> TV FAIL"
            return 0

    return show


def formatTVOutput(show, link=True):
    try:
        text = ""
        text += "%s | %s | Status: %s\n" % (show['seriesname'], show['firstaired'][:4], show['status'])
        text += "Runtime: %s minutes. | Released: %s\n" % (show['runtime'], show['firstaired'])
        actors = []
        for aperson in show['actors'].split('|'):
            if len(aperson.strip()):
                if len(actors) >= 5:
                    break
                actors.append(aperson.strip())
        text += "Actors: %s\n" % concatList(actors, ' / ')
        text += "Plot: %s" % show['overview']
        if 'imdb_id' in show and link:
            text += "\nLink: http://www.imdb.com/title/%s" % show['imdb_id']
    except Exception as e:
        print e
        text = "Failed"

    try:
        image = show['poster']
    except:
        image = None
    return {'text': html_decode(text), 'image': image}
