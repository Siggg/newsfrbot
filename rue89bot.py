import feedparser
import cPickle
import praw

# TODO : improve the "database" system that will get corrupted if interrupted and take o(n) time with n=entries already published

reddit = praw.Reddit(user_agent='Rue89 bot, by u/keepthepace')
reddit.login('keepthepace', 'rttrtt')

already_published = cPickle.load(open("already_published","rb"))

d = feedparser.parse('http://rue89.feedsportal.com/c/33822/f/608948/index.rss')

for e in d["entries"]:
    if not e["link"] in already_published:
        reddit.submit('rue89', e["title"], url=e['link'])
        already_published.add(e["link"])
        cPickle.dump(already_published,open("already_published","w"))

