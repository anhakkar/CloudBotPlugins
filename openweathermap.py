"""
openweathermap.py - openweathermap.org plugin for CloudBot

Requires an openweathermap api key.

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
import json
import datetime

default_city = 'Helsinki,Finland'
base_url = 'http://api.openweathermap.org/data/2.5/'
weather_api = base_url + 'weather?q='

description_translations = {
    200:'ukkosta ja kevyttä sadetta',
    201:'ukkosta ja sadetta',
    202:'ukkosta ja rankkasadetta',
    210:'kevyttä ukkosta',
    211:'ukkosta',
    212:'voimakasta ukkosta',
    221:'ukkoskuuroja',
    230:'ukkosta ja kevyttä tihkusadetta',
    231:'ukkosta ja tihkusadetta ',
    232:'ukkosta ja voimakasta tihkusadetta',
    300:'kevyttä tihkusadetta',
    301:'tihkusadetta',
    302:'voimakasta tihkusadetta',
    310:'kevyttä tihkusadetta ja sadetta',
    311:'tihkusadetta ja sadetta',
    312:'voimakasta tihkusadetta ja sadetta',
    321:'tihkusadekuuroja',
    500:'kevyttä sadetta',
    501:'kohtalaista sadetta',
    502:'voimakasta sadetta',
    503:'rankkasadetta',
    504:'erittäin voimakasta rankkasadetta',
    511:'jäätävää sadetta',
    520:'kevyitä sadekuuroja',
    521:'sadekuuroja',
    522:'voimakkaita sadekuuroja',
    600:'kevyttä lumisadetta',
    601:'lumisadetta',
    602:'voimakasta lumisadetta',
    611:'räntää',
    621:'lumikuuroja',
    701:'utua',
    711:'savua',
    721:'autereinen ilma',
    731:'hiekka-/pölypyörteitä',
    741:'sumua',
    800:'taivas on kirkas',
    801:'muutamia pilviä',
    802:'hajanaisia ​​pilviä',
    803:'rikkinäisiä pilviä',
    804:'pilvistä',
    900:'tornado',
    901:'trooppinen myrsky',
    902:'hurrikaani',
    903:'kylmää',
    904:'kuumaa',
    905:'tuulista',
    906:'rakeita',
    950:'tyyntyvää',
    951:'tyyntä',
    952:'kevyttä tuulta',
    953:'lempeää tuulta',
    954:'kohtalaista tuulta',
    955:'raikasta tuulta',
    956:'voimakasta tuulta',
    957:'ajoittain navakkaa',
    958:'navakkaa tuulta',
    959:'erittäin navakkaa tuulta',
    960:'myrsky',
    961:'hirmumyrsky',
    962:'hurrikaani'
}

def winddirection(degrees):
    if (348.75 <= degrees and degrees <= 360) or (0 <= degrees and degrees <= 11.25):
        return 'pohjoisesta'
    elif 11.25 < degrees and degrees <= 33.75:
        return 'pohjoiskoillisesta'
    elif 33.75 < degrees and degrees <= 56.25:
        return 'koillisesta'
    elif 56.25 < degrees and degrees <= 78.75:
        return 'itäkoillisesta'
    elif 78.75 < degrees and degrees <= 101.25:
        return 'idästä'
    elif 101.25 < degrees and degrees <= 123.75:
        return 'itäkaakosta'
    elif 123.75 < degrees and degrees <= 146.25:
        return 'kaakosta'
    elif 146.25 < degrees and degrees <= 168.75:
        return 'eteläkaakosta'
    elif 168.75 < degrees and degrees <= 191.25:
        return 'etelästä'
    elif 191.25 < degrees and degrees <= 213.75:
        return 'etelälounaasta'
    elif 213.75 < degrees and degrees <= 236.25:
        return 'lounaasta'
    elif 236.25 < degrees and degrees <= 258.75:
        return 'länsilounaasta'
    elif 258.75 < degrees and degrees <= 281.25:
        return 'lännestä'
    elif 281.25 < degrees and degrees <= 303.75:
        return 'länsiluoteesta'
    elif 303.75 < degrees and degrees <= 326.25:
        return 'luoteesta'
    elif 326.25 < degrees and degrees < 348.75:
        return 'pohjoisluoteesta'
    else:
        return

@hook.on_start()
def load_key(bot):
    global apikey
    apikey = bot.config.get('api_keys', {}).get('weather_api', None)

@hook.command('weather')
def weather(text):
    city = text.strip()
    if not city:
        city = default_city

    result = requests.get(weather_api, params={'q': city, 'appid': apikey}).json()

    city_name = str(result['name'])
    temperature = str(round(result['main']['temp'] - 273.15, 1))
    weather_description = description_translations[int(result['weather'][0]['id'])]
    wind_speed = str(result['wind']['speed'])
    wind_direction = winddirection(result['wind']['deg'])
    sunrise = datetime.datetime.fromtimestamp(int(result['sys']['sunrise'])).strftime('%H:%M')
    sunset = datetime.datetime.fromtimestamp(int(result['sys']['sunset'])).strftime('%H:%M')

    out = '{}: Lämpötila Herra Jesaja {}°, {}, tuuli {}m/s {}. Aurinko nousee klo. {} ja laskee klo. {}.'
    return out.format(city_name, temperature, weather_description, wind_speed, wind_direction, sunrise, sunset)
