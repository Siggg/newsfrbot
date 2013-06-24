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

# How many users from the twitter lists must mention a link before it is
# retained as a link worth mentioning

TWITTOS_THRESHOLD = 3

# Which search queries to you want the bot to monitor for news your lists
# members may retweet ?

queries = [ 'edtech+lang%3Afr',
            'education+numerique+lang%3Afr',
            'formation+numerique+lang%3Afr',
            'apprendre+numerique+lang%3Afr',
            'pedagogie+numerique+lang%3Afr',
            'enseignement+numerique+lang%3Afr',
            'learning+numerique+lang%3Afr' ]

# Which twitter lists will trigger publication by the bot whenever enough
# of their members retweet some link ?

lists = [ 'petermortimer/di',
          'siggg/PedagoRique',
          'cnedinnovation/di-cned' ]

# CAUTION : you MUST follow the instructions on labnol.org so that you get
# YOUR OWN myGoogleScriptID. DO NOT USE the one given below.
#
#   http://www.labnol.org/internet/twitter-rss-feeds/27931/
#
# These instructions will show you how to generate your own Google Script
# and let it to parse Twitter pages using your Twitter user account (and not
# mine...) and generate RSS feeds in return.
# Once your own Google Script is generated, copy the long ID string from
# its URL and paste it as the value of the myGoogleScriptID variable below :

myGoogleScriptID = 'AKfycbzw8ku5gvJKcWFYHOQS_Dv_6cLECkULNOBaJemN9caSQMl6q7E'

# That's it for configuration variables.

try:
    indexedTweets = cPickle.load(open("indexedTweets","rb"))
except IOError:
    indexedTweets = dict() # indexedTweets = {'someTweetUrl': True}

try:
    tweetsIndexedByLinks = cPickle.load(open("tweetsIndexedByLinks","rb"))
except IOError:
    tweetsIndexedByLinks = dict()
    # entry = {'link': 'someTweetUrl', 'title':'someTweetText'}
    # tweetsIndexedByLinks[someLinkUrl] = {someTweetUrl: entry}

try:
    shortLinks = cPickle.load(open("shortLinks","rb"))
except IOError:
    shortLinks = dict() # shortLinks["shortUrl"] = "finalUrl"

TEMPORARILY_SKIPS = []

class Link:

    """ A class of hyperlinks which may have a short URL and
    a final URL once redirected from the short URL. """

    def __init__(self,url):

        self.shortUrl = url.strip()
        # This may be a shortened or redirected URL
        # e.g. http://t.co/.... or http://bit.ly/....
        # What final URL is this link about ?
        self.url = None
        if url not in TEMPORARILY_SKIPS:
            self.dereference()
        if self.url is None:
            self.url = self.shortUrl
    
    def dereference(self):

        """ Sets the final URL of the page we are redirected to when trying
        to access the link URL """

        # Is this a truncated link ?
        shortUrl = self.shortUrl
        if shortUrl[:12] in ["http://t.co/", "https://t.co"] or shortUrl[-1:] == u"…":
            if len(shortUrl) < 18 or shortUrl[-1:] == u"…":
                # truncated !
                # don't try to dereference it
                shortLinks[shortUrl] = shortUrl.strip()
                cPickle.dump(shortLinks,open("shortLinks","wb"))
                return
        # Not truncated, let's proceed with dereferencing ths link
        if shortUrl in [sl.strip() for sl in shortLinks.keys()]:
            # We've already dereferenced this link.
            finalUrl = shortLinks[shortUrl].strip()
        else:
            # Let's dereference this link.
            try:
                sleep(1)
                finalUrl = urlopen(shortUrl).geturl().strip()
            except HTTPError, err:
                print asctime(), \
                      "HTTPError : Could not open", \
                      shortUrl.encode("utf8","replace"), \
                      "; retrying once with a trick"
                req = Request(shortUrl, headers={'User-Agent' : "Reddit bot"})
                try:
                    sleep(1)
                    finalUrl = urlopen(req).geturl()
                    print asctime(), "Successful trick ! for", shortUrl.encode("utf8","replace")
                except HTTPError:
                    # traceback.print_stack()
                    print sys.exc_info()[0]
                    print asctime(), \
                          "HTTPError : Could not open", \
                          shortUrl.encode("utf8","replace"), \
                          "; will skip"
                    TEMPORARILY_SKIPS.append(shortUrl)
                    return
                except:
                    # traceback.print_stack()
                    print sys.exc_info()[0]
                    print shortUrl.encode("utf8","replace")
                    print asctime(), "Could not open link above ; will skip"
                    TEMPORARILY_SKIPS.append(shortUrl)
                    return
            except:
                # traceback.print_stack()
                print sys.exc_info()[0]
                print shortUrl.encode("utf8","replace")
                print asctime(), "Could not open link above ; will skip."
                TEMPORARILY_SKIPS.append(shortUrl)
                return
            # Let's remember the final URL for this twittedLink
            shortLinks[shortUrl] = finalUrl.strip()
            cPickle.dump(shortLinks,open("shortLinks","wb"))
        for uselessSuffix in ["?utm_", "&utm_"]:
            try:
                index = finalUrl.index(uselessSuffix)
                finalUrl = finalUrl[:index]
            except ValueError:
                pass
        self.url = finalUrl.strip()

class Tweet:

    """ A class of tweets whith links which can be processed for publication
    if they are famous enough. """

    def __init__(self, entry):

        """ Instantiates a tweet from an RSS entry representing a tweet. """

        self.entry=entry
        self.url = entry["link"].strip()
        self.text = entry["title"]
        print
        print self.text.encode("utf8","replace")[:80]
        self.userId = urlsplit(self.url).path.split('/')[1]

    def alreadyIndexed(self):

        result = self.url in [url.strip() for url in indexedTweets.keys()]
        if result == True:
            print "(already indexed)"
	else:
	    print "(never indexed so far)"
        return result

    def validLinks(self):

        """ Returns links extracted from the tweet and filters out links
        not worth exploring (invalid URLs, ...) """

        links = []
        for url in re.findall(r'(https?://\S+)', self.text):
            url = url.strip()
            if url is None:
                continue
            if len(url) <= 12 or url[-1:] == u"…":
                continue
            if url[:12] in ["http://t.co/", "https://t.co"] and len(url) < 18:
                continue
            if url[:16] in ["http://paper.li/"]:
                continue
            links.append(Link(url))
        return links

    def indexByLinks(self):

        """ Indexes valid links from the tweet, marks this tweet as indexed in
        the indexedTweets file and stores the tweet indexed by its links in the
        tweetsIndexedByLinks file. """

        if self.alreadyIndexed() == True:
            return

        self.links = self.validLinks()
        print len(self.links), "valid links"
        for link in self.links:
            # Have we already seen this link ?
            # This link was tweeted at this URL with that tweet
            dictEntry = {"link": self.url, "title": self.text}
            if link.url not in tweetsIndexedByLinks.keys():
                # this link URL has never been seen before
                tweetsIndexedByLinks[link.url] = {self.url: dictEntry}
            else:
                # we've already seen this final URL before
                tweetsIndexedByLinks[link.url][self.url] = dictEntry
            # Let's remember this tweet.
            cPickle.dump(tweetsIndexedByLinks,open("tweetsIndexedByLinks","wb"))

        print asctime(), \
              len(self.links), \
              "links indexed in new tweet :", \
              self.text.encode("utf8","replace")
        indexedTweets[self.url] = True
        assert(self.alreadyIndexed())
        cPickle.dump(indexedTweets,open("indexedTweets","wb"))

    def linksToPublish(self):

        """ Returns (link, self) for each valid link from this tweet if only if
        it meets such criteria as the number of persons who have twitted about it
        before. """

        if self.alreadyIndexed() == True:
            return [] # we only publish the first time we index the links
        self.indexByLinks()
        linksToPublish = []
        for link in self.links:
            # Now how many distinct twitter users have tweeted about this link ?
            tweetEntries = tweetsIndexedByLinks[link.url].values()
            if len(tweetEntries) == 1:
                continue # First time this link is twitted, let's skip it
            convergingTweets = [Tweet(entry) for entry in tweetEntries]
            twitterUsers = {}
            for convergingTweet in convergingTweets:
                twitterUsers[convergingTweet.userId] = True
            twitterUsers = twitterUsers.keys()
            nbOfTwitteUsers = len(twitterUsers)  
            print asctime(), \
                  nbOfTwitteUsers, \
                  "user(s) have twitted about", \
                  link.url.encode("utf8","replace"), \
                  "; here they are :", \
                  twitterUsers
            if nbOfTwitteUsers >= TWITTOS_THRESHOLD:
                # At least TWITTOS_THRESHOLD twitter users have twitted
                # about this URL.
                for convergingTweet in convergingTweets:
                    print asctime(), "about to publish tweet", convergingTweet.text.encode("utf8","replace")
                    linksToPublish.append((link,convergingTweet))
        return linksToPublish

def get():
    TEMPORARILY_SKIPS = []

    scriptPrefix = 'https://script.google.com/macros/s/' \
                    + myGoogleScriptID \
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
    print asctime(), len(entries), "entries in our OUT-OF-lists feeds"
    # Let's process each entry from these feeds
    for entry in entries:
        # Let's have a look at each tweet and have their links checked for
        # future reference via tweetsIndexedByLinks
        tweet = Tweet(entry)
        tweet.indexByLinks()

    # Now let's examine tweets from the lists and check their links
                    
    listFeeds = [ scriptPrefix
                 + 'list&q='
                 + l
                 for l in lists ]
    
    listEntries = []
    for feedURL in listFeeds:
        sleep(2)
        feed = feedparser.parse(feedURL)
        listEntries += feed.entries
    print asctime(), len(listEntries), "entries in our lists feeds"
    if len(listEntries) == 0:
        print "\n".join(listFeeds)
    ret=list()
    for listEntry in listEntries:
        tweet = Tweet(listEntry)
        ret += tweet.linksToPublish()
    return ret