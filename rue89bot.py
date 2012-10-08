import feedparser
import cPickle
import praw

from time import *

# TODO : improve the "database" system that will get corrupted if interrupted and take o(n) time with n=entries already published

reddit = praw.Reddit(user_agent='Rue89 bot, by u/keepthepace')
reddit.login('keepthepace', 'rttrtt')

already_published = cPickle.load(open("already_published","rb"))

while True:
    d = feedparser.parse('http://rue89.feedsportal.com/c/33822/f/608948/index.rss')

    for e in d["entries"]:
        if not e["link"] in already_published:
            try:
                reddit.submit('rue89', e["title"], url=e['link'])
                sleep(10) # To comply with reddit's policy : no more than 0.5 req/sec
                already_published.add(e["link"])
                cPickle.dump(already_published,open("already_published","w"))
                print asctime(), e["title"]
            except:
		print "Exception : Reddit offline ? Retrying in 5 minutes"
		sleep(300)
    sleep(300)

