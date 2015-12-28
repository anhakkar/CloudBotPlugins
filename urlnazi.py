"""
urlnazi.py - URL Nazi plugin for CloudBot

Listens for URL:s on a channel and prints the <title>-element of the page along
with the URL. If the URL does not point to a HTML page, it will print the
content-type of the file. Also creates is.gd links for long urls. If the URL
has already been posted on the channel by another user, it will print the
original poster of the URL and the date the URL was originally posted.

The plugin checks all other regex hooks currently active and does not print
anything if the URL is matched by another plugin. This way it will not
conflict with other scripts with URL regex hooks (youtube, twitch.tv, ...).
It will however remember URL:s matched by other plugins and will print the
original poster if the conflicting plugin is disabled later.

Created by Mikko Kautto <https://github.com/pasuuna>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from sqlalchemy import Table, Column, String, DateTime, PrimaryKeyConstraint
from cloudbot import hook
from cloudbot.util import database
import os
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

url_shortening_limit = 50
url_regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
base_url = 'http://is.gd/create.php?'

table = Table(
    'urlnazi',
    database.metadata,
    Column('network', String(50)),
    Column('channel', String(50)),
    Column('user', String(50)),
    Column('url', String(2083)),
    Column('url_timestamp', DateTime),
    PrimaryKeyConstraint('network', 'channel', 'url')
)

def add_url(db, network, channel, user, url, url_timestamp):
    query = table.insert().values(
        network = network.lower(),
        channel = channel.lower(),
        user = user,
        url = url,
        url_timestamp = url_timestamp
    )
    db.execute(query)
    db.commit()

def find_url(db, network, channel, url):
    query = table.select()\
            .where(table.c.network == network.lower())\
            .where(table.c.channel == channel.lower())\
            .where(table.c.url == url)
    result = db.execute(query).first()
    db.commit()
    return result

@hook.regex(url_regex)
def urlnazi(match, nick, chan, db, conn, bot):
    url = match.group()

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers)
        if r.status_code != requests.codes.ok:
            return url + ': error - HTTP status code ' + str(r.status_code)
    except requests.ConnectionError:
        return url + ": failed to connect"

    nazi = ''
    found_url = find_url(db, conn.name, chan, url)
    if found_url:
        if found_url.user != nick:
            nazi = ' - \x0304OLD! Originally posted by {} on {}'\
                    .format(found_url.user,found_url.url_timestamp.strftime('%d.%m.%Y') + '\x0304')
    else:
        add_url(db, conn.name, chan, nick, url, datetime.now())

    for regex, hook in bot.plugin_manager.regex_hooks:
        if re.search(regex, url) and str(hook).find(os.path.basename(__file__)) == -1:
            return

    if 'text/html' in r.headers['content-type']:
        out = BeautifulSoup(r.text).title.text.strip()
    else:
        out = r.headers['content-type']

    if len(url) > url_shortening_limit:
        url = requests.get(base_url, params={'format': 'simple', 'url': url}).text

    return '{} - {}{}'.format(out, url, nazi)
