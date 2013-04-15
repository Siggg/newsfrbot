import sources.rue89
import sources.lemonde
import sources.lefigaro
import feedparser
import cPickle
import praw

import traceback
import sys
import getpass
import urllib2

from time import *

# TODO : improve the "database" system that will get corrupted if interrupted and take o(n) time with n=entries already published

reddit = praw.Reddit(user_agent='Newsfr bot, by u/keepthepace')
user='newsfrbot'
print "Password for",user,"?"
passwd=getpass.getpass()
reddit.login(user, passwd)

already_published = cPickle.load(open("already_published","rb"))

while True:
    try:

        rue89feed = sources.rue89.get()
        lefigarofeed = sources.lefigaro.get()
        lemondefeed = sources.lemonde.get()
        

        for d in [('lefigaro', lefigarofeed), ('lemonde', lemondefeed), ('rue89', rue89feed)]:
            for e in d[1]:
                if not e['link'] in already_published:
                    try:
                        print asctime(), "Publishing on",d[0],":", e['title']
                        reddit.submit(d[0], e['title'], url=e['link'])
                        print d[0], e['title'], e['link']
                        sleep(10) # To comply with reddit's policy : no more than 0.5 req/sec
                        already_published.add(e['link'])
                        cPickle.dump(already_published,open("already_published","w"))
                    except praw.errors.APIException as ex:
                        if ex.error_type=='ALREADY_SUB':
                            already_published.add(e['link'])
                            print "Already published :", e['title']
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
    except:
        print asctime(),"Exception in main program : "
        traceback.print_exc()
    sleep(300)


