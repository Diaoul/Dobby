# Copyright 2011 Antoine Bertin <diaoulael@gmail.com>
#
# This file is part of Dobby.
#
# Dobby is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Dobby is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Dobby.  If not, see <http://www.gnu.org/licenses/>.
import requests
import json
from urllib import quote


AUTOCOMPLETE_URL = 'http://autocomplete.wunderground.com/aq?query={query}&format={format}&c={country}&h={hurricanes}&cities={cities}'
API_URL = 'http://api.wunderground.com/api/{key}/{features}/q/{query}.{format}'
FEATURES = ['geolookup', 'conditions', 'forecast', 'astronomy', 'radar', 'satellite', 'webcams', 'history',
            'alerts', 'hourly', 'hourly7day', 'forecast7day', 'yesterday', 'autocomplete', 'almanac', 'lang']


def autocomplete(query, country=None, hurricanes=False, cities=True, timeout=5):
    data = {}
    data['query'] = quote(query)
    data['country'] = country or ''
    data['hurricanes'] = 1 if hurricanes else 0
    data['cities'] = 1 if cities else 0
    data['format'] = 'JSON'
    r = requests.get(AUTOCOMPLETE_URL.format(**data), timeout=timeout)
    results = json.loads(r.content)['RESULTS']
    return results

def request(key, features, query, timeout=5):
    data = {}
    data['key'] = key
    data['features'] = '/'.join([f for f in features if f in FEATURES])
    data['query'] = quote(query)
    data['format'] = 'json'
    r = requests.get(API_URL.format(**data), timeout=timeout)
    results = json.loads(_unicode(r.content))
    return results

def _unicode(string):
    """Try to convert a string to unicode using different encodings"""
    fallback = 'utf-8'
    for encoding in ['utf-8', 'latin1']:
        try:
            result = unicode(string, encoding)
            return result
        except UnicodeDecodeError:
            pass
    result = unicode(string, fallback, 'replace') 
    return result 
