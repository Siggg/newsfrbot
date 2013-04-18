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
import sys
from time import sleep
import traceback

def get():
    
    THRESHOLD = 10 # Number of minimum comments to publish the article

    print "Reading Le Monde"
    ret=list()
    """feed = feedparser.parse("http://rss.lemonde.fr/c/205/f/3050/index.rss")
    for e in feed["entries"]:
        # Finds the url of the comment page
        sleep(2) # To not be too hard on the website
        arts = urlopen(e["link"]).read()
        art = BeautifulSoup(arts)
        c=0
        try:
            for a in art.findAll("div"):
                if a.has_key("data-aj-uri"):
                    if "Reaction" in a["data-aj-uri"]:
                        # Finds the number of comments
                        coms = urlopen("http://lemonde.fr/"+a["data-aj-uri"]).read()
                        com = BeautifulSoup(coms)
                        elem = com.find(itemprop="InteractionCount")
                        if elem:
                            c = int(elem.text.rstrip(')').lstrip('('))
                        break

            if c>THRESHOLD:
                sys.stdout.write(str(c)+" ")
                sys.stdout.flush()
                ret.append({'title':e["title"], 'link':e["link"]})
            else:
                sys.stdout.write("("+str(c)+") ")
                sys.stdout.flush()
                
        except: 
            sys.stdout.write("E ")
            sys.stdout.flush()
            traceback.print_exc()
            pass            
    sys.stdout.write("\n")
    sys.stdout.flush()"""
    
    s=urlopen("http://www.lemonde.fr/rss/").read()
    soup=BeautifulSoup(s)
    newurl = "http://lemonde.fr"+soup.find(id="les-plus-commentes-2j").first()["uri"]
    s=urlopen(newurl).read()
    soup=BeautifulSoup(s.decode("latin1"))
    arts = soup.findAll("a")
    for a in arts:
        if not a.has_key('title'):
            sys.stdout.write("O")
            sys.stdout.flush()
            ret.append({'title':a.renderContents().decode("utf8"), 'link':u"http://lemonde.fr/"+a["href"]})
    sys.stdout.write("\n")
    return ret


