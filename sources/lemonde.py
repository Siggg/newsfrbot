from BeautifulSoup import BeautifulSoup
from urllib import urlopen
import feedparser
import sys
from time import sleep

def get():
    
    THRESHOLD = 10 # Number of minimum comments to publish the article

    print "Reading Le Monde"
    ret=list()
    feed = feedparser.parse("http://rss.lemonde.fr/c/205/f/3050/index.rss")
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


