# This file is part of newsfrbot.
# 
# Newsfrbot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
# 
# Newsfrbot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
# (C) Copyright Yves Quemener, 2012

from BeautifulSoup import BeautifulSoup
from urllib import urlopen
import feedparser
import traceback
import sys
from time import sleep


def get():
    
    THRESHOLD = 100 # Number of minimum comments to publish the article

    print "Reading Le Figaro"
    ret=list()
    feed = feedparser.parse('http://rss.lefigaro.fr/lefigaro/laune?format=xml')
    for e in feed["entries"]:
        # Find the number of comments on this entry
        arts = urlopen(e["link"]).read()
        sleep(2) # To not be too hard on the website
        art = BeautifulSoup(arts)
        try:
            c = int(art.find(property="og:count")["content"])
            if c>THRESHOLD:
                sys.stdout.write("O")
                sys.stdout.flush()
                ret.append({'title':e["title"], 'link':e["link"]})
            else:
                sys.stdout.write(".")
                sys.stdout.flush()
        except: 
            sys.stdout.write("E")
            sys.stdout.flush()
            pass
    sys.stdout.write("\n")
    sys.stdout.flush()
    return ret


