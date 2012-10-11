import feedparser
import cPickle
import praw

import traceback
import sys
import getpass

from time import asctime

# TODO : improve the "database" system that will get corrupted if interrupted and take o(n) time with n=entries already published

reddit = praw.Reddit(user_agent='Rue89 bot, by u/keepthepace')
user='newsfrbot'
print "Password for",user,"?"
passwd=getpass.getpass()
reddit.login(user, passwd)

already_published = cPickle.load(open("already_published","rb"))

while True:
    rue89feed = feedparser.parse('http://rue89.feedsportal.com/c/33822/f/608948/index.rss')
    lemondefeed = feedparser.parse('http://www.lemonde.fr/rss/une.xml')
    lefigarofeed = feedparser.parse('http://rss.lefigaro.fr/lefigaro/laune?format=xml')

    for d in [('rue89', rue89feed), ('lemonde', lemondefeed), ('lefigaro', lefigarofeed)]:
    for e in d[1]["entries"]:
        if not e["link"] in already_published:
            try:
                print asctime(), "Publishing on",d[0],":", e["title"]
                reddit.submit(d[0], e["title"], url=e['link'])
                sleep(10) # To comply with reddit's policy : no more than 0.5 req/sec
                already_published.add(e["link"])
                cPickle.dump(already_published,open("already_published","w"))
            except praw.errors.APIException as ex:
                if ex.error_type=='ALREADY_SUB':
                    already_published.add(e["link"])
                    print "Already published :", e["title"]
                    cPickle.dump(already_published,open("already_published","w"))
                else:
                    print asctime(),"Exception : Reddit offline ? Retrying in 5 minutes"
                    traceback.print_stack()
                    print ex.error_type
                    print ex.message
                    print ex.field
                    print ex.response
                    print "_", sys.exc_info()[0]
                    sleep(300)
    sleep(300)
