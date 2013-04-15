import feedparser
from urllib import urlopen

def get():
    ret=list()
    feed = feedparser.parse('http://www.rue89.com/feed/google-editors-pick')
    for e in feed["entries"]:
        ret.append({'title':e["title"], 'link':e["link"]})
    return ret
