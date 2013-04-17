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

import feedparser
from urllib import urlopen

def get():
    ret=list()
    feed = feedparser.parse('http://www.rue89.com/feed/google-editors-pick')
    for e in feed["entries"]:
        ret.append({'title':e["title"], 'link':e["link"]})
    return ret
