# This file is part of rss2reddit_using_newsfrbot.
# 
# rss2reddit_using_newsfrbot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
# 
# rss2reddit_using_newsfrbot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
# (C) Copyright Yves Quemener, 2012
# (C) Copyright Jean Millerat, 2013

import sources.twitter
import feedparser
import cPickle
import praw

import traceback
import sys
import getpass
import urllib2

from time import *

# How long in seconds does the bot have to wait before checking
# its sources once again ?
NAP_DURATION = 300

# TODO : improve the "database" system that will get corrupted if interrupted and take o(n) time with n=entries already published

reddit = praw.Reddit(user_agent='Rss2Reddit bot, by u/jeanAkaSiggg')
user='rss2redditBot'
print "Password for",user,"?"
passwd=getpass.getpass()
reddit.login(user, passwd)


try:
    already_published = cPickle.load(open("already_published","rb"))
except IOError:
    already_published = set()


while True:
    try:

        twitterFeed = sources.twitter.get()
        
        for d in [('Test201304001', twitterFeed)]:
            for e in d[1]:
                if not e['link'] in already_published:
                    try:
                        print asctime(), "Publishing on",d[0],":", e['title']
                        reddit.submit(d[0], e['title'], url=e['link'])
                        sleep(2) # To comply with reddit's policy : no more than 0.5 req/sec
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
    print asctime(),"Taking a short nap now, for ", NAP_DURATION, " seconds."
    sleep(NAP_DURATION)
