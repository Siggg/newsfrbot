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

import feedparser
from urllib2 import Request, urlopen, HTTPError, URLError
import re
from urlparse import urlsplit
import cPickle
from time import asctime, sleep

try:
    knownTweets = cPickle.load(open("knownTweets","rb"))
except IOError:
    knownTweets = dict()

twitterUserIds = ['siggg',
                  'petermortimer',
                  'sbrunet86',
                  'bproust',
                  'sandrineventana',
                  'RosinePK',
                  'pluton86',
                  'MecRouge'
                  ]

def get():
    ret=list()
    feedURLs = ['http://twitter-rss.com/user_timeline.php?screen_name=' + uid for uid in twitterUserIds]
    feedURLs += 'https://script.google.com/macros/s/AKfycbzw8ku5gvJKcWFYHOQS_Dv_6cLECkULNOBaJemN9caSQMl6q7E/exec?action=list&q=petermortimer/di'
    feedURLs += 'https://script.google.com/macros/s/AKfycbzw8ku5gvJKcWFYHOQS_Dv_6cLECkULNOBaJemN9caSQMl6q7E/exec?action=search&q=%23education OR %23edtech lang%3Afr include%3Aretweets&src=typd'
    feeds = [feedparser.parse(url) for url in feedURLs]
    entries = []
    for feed in feeds:
        entries += feed["entries"]
    for e in entries:
        tweet = e["title"]
        tweetUrl = e["link"]
        twittedLinks = re.findall(r'(https?://\S+)',tweet)
        for twittedLink in twittedLinks:
            # what link is this tweet about ?
            sleep(1)
            finalUrl = twittedLink
            try:
                finalUrl = urlopen(twittedLink).geturl()
            except HTTPError, err:
                print asctime(),"HTTPError : Could not open ",twittedLink," ; retrying once with a trick"
                sleep(1)
                req = Request(twittedLink, headers={'User-Agent' : "Reddit bot"})
                try:
                    finalUrl = urlopen(req).geturl()
                    print asctime(),"Successful trick ! for ", twittedLink
                except HTTPError, err:
                    print asctime(),"HTTPError : Could not open ",twittedLink," ; will not retry"
                except:
                    print asctime(),"Could not open ",twittedLink," ; will not retry"
            except:
                print asctime(),"Could not open ",twittedLink," ; will skip."
                continue
            # OK. We know the final url of the link this tweet is about.
            # Have we already seen it ?
            twitterUserId = urlsplit(tweetUrl).path.split('/')[1]
            tweet = {'title':tweet,
                     'link':finalUrl,
                     'tweetUrl': tweetUrl,
                     'twitterUserId': twitterUserId}
            if finalUrl not in knownTweets.keys():
                # final URL has never been seen before
                knownTweets[finalUrl] = {tweetUrl: tweet}
            else:
                # we've already seen this final URL before
                knownTweets[finalUrl][tweetUrl] = tweet
            # Let's remember this tweet.
            cPickle.dump(knownTweets,open("knownTweets","w"))
            # Now how many distinct twitter users have tweeted about this ?
            tweets = knownTweets[finalUrl].values()
            twitterUsers = {}
            for tweet in tweets:
                twitterUsers[tweet['twitterUserId']] = True
            twitterUsers = twitterUsers.keys() 
            if len(twitterUsers)>1:
                # at least 3 twitter users have twitted about this URL
                print asctime(),len(twitterUsers)," user(s) have twitted about ",finalUrl," ; here they are : ",twitterUsers
                for tweet in tweets:
                    print asctime(),"adding tweet",tweet
                    ret.append(tweet)
    return ret
