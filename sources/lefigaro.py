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
            print "Exception reading Le Figaro."
            traceback.print_exc()
            pass
    sys.stdout.write("\n")
    sys.stdout.flush()
    return ret


