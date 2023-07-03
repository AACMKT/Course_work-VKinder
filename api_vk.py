import requests
import datetime as dt
from pprint import pprint
import time

with open('vk_token.txt', 'r') as file_object:
    token_vk = file_object.readline().strip()

version = 5.131

age_delta_min = 15
age_delta_max = 2


class VkSearch:

    def __init__(self, token, ver):
        self.url = 'https://api.vk.com/method/'
        self.auth = {
            'access_token': token,
            'v': ver
        }

    def get_user_id(self):
        pass

    "Данные пользователя"

    def get_user_params(self):
        url = self.url + 'users.get'
        fields = {
            "fields": "country, city, education, sex, bdate"
        }

        request = requests.get(url, params={**self.auth, **fields}).json()
        res = request['response']
        return res

    def basic_search_params(self, age_min, age_max):
        user_data = self.get_user_params()[0]
        params = {}
        if 'bdate' in user_data.keys():
            birth_year = dt.datetime.strptime(user_data['bdate'], '%d.%m.%Y').year
            age = dt.datetime.now().year - birth_year

            params['age_from'] = age - age_min
            params['age_to'] = age + age_max

        if user_data['sex'] == 1:
            params['sex'] = 2
        elif user_data['sex'] == 2:
            params['sex'] = 1
        elif user_data['sex'] == 0:
            pass

        if 'country' in user_data.keys():
            params['country'] = user_data['country']['id']
        if 'city' in user_data.keys():
            params['hometown'] = user_data['city']['title']

        params['count'] = 1
        params['offset'] = 0
        params['status'] = 6
        params['has_photo'] = 1
        params['sort'] = 1
        params['fields'] = 'photo_id, relation, city, bdate, sex, followers_count'

        return params

    "Поиск по запросу с контролем частоты обращений к api"

    @staticmethod
    def get_request(url, auth, params):
        while True:
            request = requests.get(url, params={**auth, **params}).json()
            "если запрос вернул ошибку 'Too many requests per second'"
            if 'error' in request and request['error']['error_code'] == 6:
                time.sleep(0.33)
            else:
                break
        return request

    @staticmethod
    def search_for_best_photos(js_file: dict, amount=3) -> dict:
        res = js_file['response']['items']
        sort_res = sorted(res, key=lambda x: x['comments']['count'] + x['likes']['count'])
        sort_res = sort_res[:amount]
        best_size_photos = []
        if len(sort_res) > 0:
            for el in sort_res:
                size = {}
                scale = {'s': 0, 'm': 1, 'x': 2, 'o': 3, 'p': 4, 'q': 5, 'r': 6, 'y': 7, 'z': 8, 'w': 9}
                for s in el['sizes']:
                    size = {**size, **{s['type']: scale[s['type']]}}
                max_size = max(size, key=size.get)
                for best_size in el['sizes']:
                    if best_size['type'] == str(max_size):
                        best_size_photos.append(best_size['url'])

            res = {'owner_id': str(id), 'photos': best_size_photos}
            return res
        else:
            return {'owner_id': 1, 'photos': ['No_photos']}

    "Подбор по параметрам"

    def find_match(self):
        url = self.url + 'users.search'
        params = self.basic_search_params(15, 0)
        resp = []
        offset = 0
        while len(resp) < 10:
            # request = requests.get(url, params={**self.auth, **params}).json()
            request = self.get_request(url, self.auth, params)
            check_photos_amount_params = {'owner_id': str(request['response']['items'][0]['id']),
                                          'album_id': 'profile'}
            if request['response']['items'][0]['is_closed'] or 'relation' not in request['response']['items'][0].keys() \
                    or 'city' not in request['response']['items'][0].keys():
                offset += 2
                params['offset'] = offset
            elif len(self.get_request(self.url + 'photos.get', self.auth,
                                      check_photos_amount_params)['response']['items']) > 2:
                offset += 1
                params['offset'] = offset
                resp.append(request['response']['items'][0])
            else:
                offset += 2
                params['offset'] = offset
                # resp.append(request['response']['items'][0])
        return resp

    def get_photos(self, own_id, album='profile', num_of_photos=3):
        url = self.url + 'photos.get'
        params = {
            'owner_id': str(own_id),
            'album_id': str(album),
            'photo_sizes': 0,
            'extended': 1,
            'offset': 0,
        }
        request = self.get_request(url, self.auth, params)
        if request.get('error'):
            print(request['error']['error_msg'])

        else:
            res = self.search_for_best_photos(request, num_of_photos)
            return res

    def search_result(self):
        res_json = []
        matches = self.find_match()
        for el in matches:
            photos = self.get_photos(el['id'])['photos']
            # if len(photos) < 3:
            #     amount = 3 - len(photos)
            #     wall_photos = self.get_photos(el['id'], 'wall', num_of_photos=amount)['photos']
            #     if 'No_photos' not in wall_photos:
            #         photos.append(wall_photos)

            birth_year = dt.datetime.strptime(el['bdate'], '%d.%m.%Y').year
            age = dt.datetime.now().year - birth_year

            res_json.append({'first_name': el['first_name'],
                             'last_name': el['last_name'],
                             'age': age,
                             'city': el['city']['title'],
                             'relation': el['relation'],
                             'link': f'https://vk.com/id{el["id"]}',
                             'best_photos': photos})

        return res_json


# 481271573
# 702419612
# 574450796
# 287142503


if __name__ == '__main__':
    info = VkSearch(token_vk, version)
    # pprint(info.get_photos(287142503))
    # pprint(info.find_match())
    pprint(info.search_result())
    # pprint(info.get_user_params())
    # pprint(info.basic_search_params(15, 5))
