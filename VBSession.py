from VBCore import *
import urllib
from datetime import date, timedelta

oml = OxybetMatchList()
vmz = []

def sync_list():
    #TODO: add argument for days_ahead
    oml.clear()
    urls = make_urls(2)
    for url in urls:    
        data = wget(url)
        oml.feed(data)
    oml.manage_table()

def sync_matches():
    for match in oml.table:
        baseurl = match['link']
        data = wget(baseurl)
        raw_odds = OxybetOddsTable()
        raw_odds.feed(data)
            
        if raw_odds.table.has_key('Stoiximan'):
            testmatch = Match(match,raw_odds.table)
            if testmatch.isvaluable:
                testmatch.print_attrs()
                vmz.append(testmatch)

def wget(baseurl):
    if baseurl.startswith(u'http://'):
        for attempt in range(10):
            try:
                page = urllib.urlopen(baseurl)
                break
            except IOError:
                pass
        data = page.read()
    else:
        page = open(baseurl)
        data = page.read()
    data = data.decode('cp1253')
    return data

def make_urls(days_ahead=1):
    #TODO:fix post-midnight dates
    urls = []
    for d in range(days_ahead):
        cur_dat = (date.today() + timedelta(d)).strftime('%Y%m%d')
        params = urllib.urlencode({'spoid':1,'modid':1,'cur_dat':cur_dat})
        url = '?'.join(('http://www.oxybet.com/odds_comparison.asp',params))
        urls.append(url)
    return urls

'''def debug1():
    data = wget('c:/users/basil/documents/python/mlhtml_for_realmadr.html')
    ml = OxybetMatchList()
    ml.feed(data)
    ml.manage_table()
    
    data = wget('c:/users/basil/documents/python/realmadr.html')
    rawodds = OxybetOddsTable()
    rawodds.feed(data)
    
    testmatch = Match(ml.table[222], rawodds.table)'''

#TODO: def print_human_readable()
