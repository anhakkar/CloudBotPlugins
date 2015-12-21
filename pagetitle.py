"""
pagetitle.py - page title plugin for CloudBot

Listens for urls on a channel and prints the <title>-element of the page along
with the url. Also creates is.gd links for long urls.

The plugin checks all other regex hooks currently active and does not print
anything if the url is matched by another plugin. This way it will not
conflict with other scripts with URL regex hooks (youtube, twitch.tv, ...).

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

from cloudbot import hook
import requests
import re
from bs4 import BeautifulSoup

url_shortening_limit = 50
url_regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
base_url = 'http://is.gd/create.php?'

@hook.regex(url_regex)
def pagetitle(match, bot):
    url = match.group()

    for regex, foo in bot.plugin_manager.regex_hooks:
        if regex != re.compile(url_regex) and re.search(regex,url):
            return

    r = requests.get(url)
    html = BeautifulSoup(r.text)

    if len(url) > url_shortening_limit:
        url = requests.get(base_url, params={"format": "simple", "url": url}).text

    return '{} - {}'.format(html.title.text.strip(), url)
