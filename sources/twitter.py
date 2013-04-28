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
import traceback, sys

# How many twitter users must mention a link before it is
# retained as a link worth mentioning
TWITTOS_THRESHOLD = 3

try:
    knownTweets = cPickle.load(open("knownTweets","rb"))
except IOError:
    knownTweets = dict()

try:
    shortLinks = cPickle.load(open("shortLinks","rb"))
except IOError:
    shortLinks = dict()

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
    feedURLs = []
    # feedURLs += ['http://twitter-rss.com/user_timeline.php?screen_name=' + uid for uid in twitterUserIds]
    # Generate your own Twitter RSS feeds by means of a Google Script
    # just follow the instructinos at http://www.labnol.org/internet/twitter-rss-feeds/27931/
    # Please DO NOT use the URLs below but generate your own ones. 
    feedURLs += [ 'https://script.google.com/macros/s/AKfycbzw8ku5gvJKcWFYHOQS_Dv_6cLECkULNOBaJemN9caSQMl6q7E/exec?action=list&q=petermortimer/di' ]
    feedURLs += [ 'https://script.google.com/macros/s/AKfycbzw8ku5gvJKcWFYHOQS_Dv_6cLECkULNOBaJemN9caSQMl6q7E/exec?action=search&q=%23education OR %23edtech lang%3Afr include%3Aretweets&src=typd' ]
    feeds = [feedparser.parse(url) for url in feedURLs]
    entries = []
    for feed in feeds:
        entries += feed["entries"]
    for e in entries:
        tweet = e["title"]
        tweetUrl = e["link"]
        twittedLinks = re.findall(r'(https?://\S+)',tweet)
        for twittedLink in twittedLinks:
            # This may be a shortened or redirected URL
            # e.g. http://t.co/.... or http://bit.ly/....
            # What final URL is this link about ?
            finalUrl = twittedLink
            # Is this a truncated link ?
            if twittedLink[:12] in ["http://t.co/", "https://t.co"]:
                if len(twittedLink) < 18:
                    # truncated !
                    # don't try to dereference it
                    shortLinks[twittedLink] = twittedLink
                    cPickle.dump(shortLinks,open("shortLinks","w"))
            # Not truncated, let's proceed with dereferencing ths link
            if twittedLink in shortLinks.keys():
                # We've already dereferenced this link.
                finalUrl = shortLinks[twittedLink]
            else:
                # Let's dereference this link.
                try:
                    sleep(1)
                    finalUrl = urlopen(twittedLink).geturl()
                except HTTPError, err:
                    print asctime(), "HTTPError : Could not open", twittedLink, "; retrying once with a trick"
                    req = Request(twittedLink, headers={'User-Agent' : "Reddit bot"})
                    try:
                        sleep(1)
                        finalUrl = urlopen(req).geturl()
                        print asctime(), "Successful trick ! for", twittedLink
                    except HTTPError:
                        traceback.print_stack()
                        print sys.exc_info()[0]
                        print asctime(), "HTTPError : Could not open", twittedLink, "; will skip"
                    except:
                        traceback.print_stack()
                        print sys.exc_info()[0]
                        print twittedLink
                        print asctime(), "Could not open link above ; will skip"
                except:
                    traceback.print_stack()
                    print sys.exc_info()[0]
                    print twittedLink
                    print asctime(), "Could not open link above ; will skip."
                    continue
                # Let's remember the final URL for this twittedLink
                shortLinks[twittedLink] = finalUrl
                cPickle.dump(shortLinks,open("shortLinks","w"))
            # OK. We know the final url of the link this tweet is about.
            # Let's model this tweet a bit.
            twitterUserId = urlsplit(tweetUrl).path.split('/')[1]
            tweet = {'title':tweet,
                     'link':finalUrl,
                     'tweetUrl': tweetUrl,
                     'twitterUserId': twitterUserId}
            # Have we already seen this final URL ?
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
            nbOfTwitteUsers = len(twitterUsers)  
            print asctime(), nbOfTwitteUsers, "user(s) have twitted about", finalUrl, "; here they are :", twitterUsers
            if nbOfTwitteUsers >= TWITTOS_THRESHOLD:
                # at least TWITTOS_THRESHOLD twitter users have twitted about this URL
                for tweet in tweets:
                    print asctime(), "adding tweet", tweet
                    ret.append(tweet)
    return ret
