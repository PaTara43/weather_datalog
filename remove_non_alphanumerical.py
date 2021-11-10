import json
import unicodedata

with open('city.list.json') as json_file:
    city_list = json.load(json_file)
    len_city_list = len(city_list)


def shave_marks(txt):
    """This method removes all diacritic marks from the given string"""
    norm_txt = unicodedata.normalize('NFD', txt)
    shaved = ''.join(c for c in norm_txt if not unicodedata.combining(c))
    return unicodedata.normalize('NFC', shaved)


for i in range(len_city_list):
    # print(city_list[i]['name'])
    city_list[i]['name'] = shave_marks(city_list[i]['name'])
    # print(city_list[i]['name'])

with open('city.list.json', 'w') as outfile:
    json.dump(city_list, outfile)

