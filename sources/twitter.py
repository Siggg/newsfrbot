# This Python file uses the following encoding: utf-8
#
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
    alreadyProcessed = cPickle.load(open("alreadyProcessed","rb"))
except IOError:
    alreadyProcessed = set()

try:
    knownTweets = cPickle.load(open("knownTweets","rb"))
except IOError:
    knownTweets = dict()

try:
    shortLinks = cPickle.load(open("shortLinks","rb"))
except IOError:
    shortLinks = dict()

TEMPORARILY_SKIPS = []

class Link:
    def __init__(self,url):
        self.shortUrl = url
        # This may be a shortened or redirected URL
        # e.g. http://t.co/.... or http://bit.ly/....
        # What final URL is this link about ?
        self.url = None
        if url not in TEMPORARILY_SKIPS:
            self.dereference()
        if self.url is None:
            self.url = self.shortUrl
    
    def dereference(self):
        """ sets the final URL of the page we are redirected to when trying
        to access the link URL """
        # Is this a truncated link ?
        link = self.shortUrl
        if link[:12] in ["http://t.co/", "https://t.co"] or link[-1:] == u"…":
            if len(link) < 18 or link[-1:] == u"…":
                # truncated !
                # don't try to dereference it
                shortLinks[link] = link
                cPickle.dump(shortLinks,open("shortLinks","w"))
                return
        # Not truncated, let's proceed with dereferencing ths link
        if link in shortLinks.keys():
            # We've already dereferenced this link.
            finalUrl = shortLinks[link]
        else:
            # Let's dereference this link.
            try:
                sleep(1)
                finalUrl = urlopen(link).geturl()
            except HTTPError, err:
                print asctime(), \
                      "HTTPError : Could not open", \
                      link, \
                      "; retrying once with a trick"
                req = Request(link, headers={'User-Agent' : "Reddit bot"})
                try:
                    sleep(1)
                    finalUrl = urlopen(req).geturl()
                    print asctime(), "Successful trick ! for", link
                except HTTPError:
                    # traceback.print_stack()
                    print sys.exc_info()[0]
                    print asctime(), \
                          "HTTPError : Could not open", \
                          link, \
                          "; will skip"
                    TEMPORARILY_SKIPS.append(link)
                    return
                except:
                    # traceback.print_stack()
                    print sys.exc_info()[0]
                    print link
                    print asctime(), "Could not open link above ; will skip"
                    TEMPORARILY_SKIPS.append(link)
                    return
            except:
                # traceback.print_stack()
                print sys.exc_info()[0]
                print link
                print asctime(), "Could not open link above ; will skip."
                TEMPORARILY_SKIPS.append(link)
                return
            # Let's remember the final URL for this twittedLink
            shortLinks[link] = finalUrl
            cPickle.dump(shortLinks,open("shortLinks","w"))
        try:
            index = finalUrl.index("?utm_")
            finalUrl = finalUrl[:index]
        except ValueError:
            pass
        self.url = finalUrl
                        
class Tweet:
    def __init__(self, entry):
        self.url = entry["link"]
        self.text = entry["title"]
        self.userId = urlsplit(self.url).path.split('/')[1]
        self.alreadyProcessed = self.url in alreadyProcessed
        if not self.alreadyProcessed:
            linkUrls = re.findall(r'(https?://\S+)', self.text)
            self.links = [Link(url) for url in linkUrls]
            for link in self.links:
                # Have we already seen this link ?
                # This link was tweeted at this URL with that tweet
                if link.url not in knownTweets.keys():
                    # this URL has never been seen before
                    knownTweets[link.url] = {self.url: self}
                else:
                    # we've already seen this final URL before
                    knownTweets[link.url][self.url] = self
                # Let's remember this tweet.
                cPickle.dump(knownTweets,open("knownTweets","w"))
            

def get():
    ret=list()
    TEMPORARILY_SKIPS = []

    # Generate your own Twitter RSS feeds by means of a Google Script.
    #
    # PLEASE DO NOT use the googleScriptID below but follow the inscriptions
    # below to generate your own one (copy it from the URL of the script you
    # will have generated). Follow the instructions at
    #
    #   http://www.labnol.org/internet/twitter-rss-feeds/27931/
    #
    
    googleScriptID = 'AKfycbzw8ku5gvJKcWFYHOQS_Dv_6cLECkULNOBaJemN9caSQMl6q7E'

    queries = [ 'edtech+lang%3Afr',
                'education+numerique+lang%3Afr',
                'formation+numerique+lang%3Afr',
                'apprendre+numerique+lang%3Afr',
                'pedagogie+numerique+lang%3Afr',
                'enseignement+numerique+lang%3Afr',
                'learning+numerique+lang%3Afr' ]
    
    scriptPrefix = 'https://script.google.com/macros/s/' \
                    + googleScriptID \
                    + '/exec?action='
    
    nonListFeeds = [ scriptPrefix
                    + 'search&q='
                    + query
                    + '+include%3Aretweets&src=typd'
                    for query in queries ]
    
    # First, we'll extract links from non-list tweets.
    # Then, we'll parse list tweets and check the links they include.
    
    # Let's access and parse these feeds, and extract their entries
    entries = []
    for feedURL in nonListFeeds:
        sleep(2)
        feed = feedparser.parse(feedURL)
        entries += feed.entries
    # Let's process each entry from these feeds
    for entry in entries:
        # Let's have a look at each tweet and have their links checked for
        # future reference via knownTweets
        tweet = Tweet(entry)

    # Now let's examine tweets from the lists and check their links
                    
    lists = [ 'petermortimer/di',
              'siggg/PedagoRique' ]
    
    listFeeds = [ scriptPrefix
                 + 'list&q='
                 + l
                 for l in lists ]
    
    entries = []
    for feedURL in listFeeds:
        sleep(2)
        feed = feedparser.parse(feedURL)
        entries += feed.entries
    for entry in entries:
        tweet = Tweet(entry)
        if not tweet.alreadyProcessed:
            for link in tweet.links:
                # Now how many distinct twitter users have tweeted about this ?
                tweets = knownTweets[link.url].values()
                twitterUsers = {}
                for tweet in tweets:
                    twitterUsers[tweet.userId] = True
                twitterUsers = twitterUsers.keys()
                nbOfTwitteUsers = len(twitterUsers)  
                print asctime(), \
                      nbOfTwitteUsers, \
                      "user(s) have twitted about", \
                      link.url, \
                      "; here they are :", \
                      twitterUsers
                if nbOfTwitteUsers >= TWITTOS_THRESHOLD:
                    # At least TWITTOS_THRESHOLD twitter users have twitted
                    # about this URL.
                    for tweet in tweets:
                        print asctime(), "adding tweet", tweet.text
                        ret.append((link,tweet))
    return ret
