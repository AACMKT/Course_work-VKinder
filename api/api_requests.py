import vk_api
import datetime as dt
from config import token_vk


def read_token():
    """
    Blank function, allows to change token receiving method without crushing entire program, by changing this function.
    :return: token -> str
    """
    token = token_vk
    return token


class VKSearch:
    """
    VK API requests class
    """

    def __init__(self, token=None):
        self.token = token

    def auth(self):
        """
        Establish VK session, using personal token.
        :return: active VK session or error message
        """
        try:
            vk_session = vk_api.VkApi(token=self.token)
        except vk_api.AuthError as error_msg:
            print(error_msg)
            return

        return vk_session

    def get_user(self, user_id=None):
        """
        Gets params of user, specified by ID (or token owner if ID is not provided), by VK API method 'users.get'.
        :param user_id: int (vk id of user, whose data is being determined)
        :return: dict (user general personal data such as birth_day, name, last name, home town, etc)
        """
        vk_session = self.auth()
        vk = vk_session.get_api()
        fields = 'country, city, sex, relation, bdate, books, music'
        if user_id is not None:
            result = vk.users.get(user_ids=user_id, fields=str(fields))
        else:
            result = vk.users.get(fields=str(fields))

        return result[0]

    @staticmethod
    def get_age(birthdate):
        birth_year = dt.datetime.strptime(birthdate, '%d.%m.%Y').year
        age = dt.datetime.now().year - birth_year

        return age

    # Параметр пол
    @staticmethod
    def get_partner_sex(sex):
        sex = int(sex)
        if sex == 1:
            p_sex = 2
        elif sex == 2:
            p_sex = 1
        else:
            print('specify user sex')
            p_sex = 0

        return p_sex

    def get_search_params(self, user_params: dict = None, user_id=None, offset: int = 0):
        """
        Function coverts user params, received by VK API 'users.get' method into params for 'users.search' method.
        :param user_params: dict
        :param user_id: int (vk id of current user)
        :param offset: int (determines position where last 'users.search' session has been finished
        :return: dict (params for 'users.search' method, based on current user personal data)
        """
        if user_params is None:
            user_params = self.get_user(user_id)
        else:
            user_params = user_params
        match_search_req = {}
        if 'sex' in user_params.keys():
            user_sex = user_params['sex']
        else:
            user_sex = 0
        if 'bdate' in user_params.keys():
            birth_date = user_params['bdate']
            age = self.get_age(birth_date)
            if user_sex == 1:
                match_search_req['age_from'] = age - 5
                match_search_req['age_to'] = age + 10
            elif user_sex == 2:
                match_search_req['age_from'] = age - 10
                match_search_req['age_to'] = age + 5
            else:
                match_search_req['age_from'] = age - 5
                match_search_req['age_to'] = age + 5
        else:
            match_search_req['age_from'] = 25
            match_search_req['age_to'] = 45

        match_search_req['sex'] = self.get_partner_sex(user_sex)
        if 'country' in user_params.keys():
            match_search_req['country'] = user_params['country']['id']
        if 'city' in user_params.keys():
            if type(user_params['city']) is dict:
                match_search_req['hometown'] = user_params['city']['title']
            else:
                match_search_req['hometown'] = user_params['city']
        match_search_req['count'] = 10
        match_search_req['offset'] = offset
        match_search_req['status'] = 6
        match_search_req['has_photo'] = 1
        match_search_req['sort'] = 1
        match_search_req['fields'] = 'country, city, sex, relation, bdate, books, music'

        return match_search_req

    def find_match_with_photos_count(self, request, black_list=None, offset: int = 0, search_iters: int = 1):
        """
        Returns info about found matches with minimum 3 photos in their profiles.
        :param request: dict (with search params)
        :param black_list: list (of blocked id's)
        :param offset: int (current search offset)
        :param search_iters: int (allows to provide more search results for one session, if increase)
        :return: list (with dicts, which contain found matches info)
        """
        if black_list is None:
            black_list = []
        vk_session = self.auth()
        vk = vk_session.get_api()
        matches_list = []
        if offset != 0:
            request['offset'] = offset
        request['offset'] = offset
        counter = offset
        for i in range(search_iters):
            matches, errors = vk_api.vk_request_one_param_pool(
                vk_session,
                'users.search',  # Метод
                key='user_id',  # Изменяющийся параметр
                values=[i],
                default_values={**request})
            for el in matches[i]['items']:
                counter += 1
                if el['id'] not in black_list:
                    if not el['is_closed'] and 'city' in el.keys():
                        if el['city']['title'] == request['hometown']:
                            photos = vk.photos.get(owner_id=el['id'], album_id='profile', count=3)
                            if photos['count'] >= 3:
                                el['offset'] = request['offset'] + counter
                                el['city'] = el['city']['title']
                                matches_list.append(el)
            request['offset'] += len(matches[i]['items'])

        return matches_list

    def find_match(self, request, black_list=None, offset: int = 0, search_iters: int = 1):
        """
        Returns info about found matches with links with at least 1 photo in their profiles.
        :param request: dict (with search params)
        :param black_list: list (of blocked id's)
        :param offset: int (current search offset)
        :param search_iters: int (allows to provide more search results for one session, if increase)
        :return: list (with dicts, which contain found matches info)
        """
        if black_list is None:
            black_list = []
        vk_session = self.auth()
        matches_list = []
        if offset != 0:
            request['offset'] = offset
        counter = 0
        for i in range(search_iters):
            matches, errors = vk_api.vk_request_one_param_pool(
                vk_session,
                'users.search',
                key='user_id',
                values=[i],
                default_values={**request})
            for el in matches[i]['items']:
                counter += 1
                if str(el['id']) not in black_list:
                    if not el['is_closed'] and 'city' in el.keys():
                        if el['city']['title'] == request['hometown']:
                            el['offset'] = request['offset'] + counter
                            el['city'] = el['city']['title']
                            matches_list.append(el)
            request['offset'] += len(matches[i]['items'])

        return matches_list

    def get_photos(self, owner_id, amount: int = 3):
        """
        Creates links to profile photos of the provided vk id owner.
        :param owner_id: int (id of the found much, whom photos should be shown)
        :param amount: int (max amount of photos to be returned)
        :return: dict (id of photos owner and list of links to photos in special format)
        """
        vk_session = self.auth()
        vk = vk_session.get_api()
        photos = vk.photos.get(owner_id=owner_id, album_id='profile', extended=1, count=3)['items']
        sort_res = sorted(photos, key=lambda x: x['comments']['count'] + x['likes']['count'])
        sort_res = sort_res[:amount]
        best_size_photos = []
        if len(sort_res) > 0:
            for el in sort_res:
                best_size_photos.append(f'photo{owner_id}_{el["id"]}')
        result = {'owner_id': owner_id, 'photos': best_size_photos}

        return result

    def get_favorites_by_id(self, list_of_ids):
        """
        Gets personal data of provided vk id's owners by VK API 'users.get' method.
        :param list_of_ids: list (vk id's of persons, marked by user as favorites)
        :return: list (with dicts, contain favorites personal data)
        """
        vk_session = self.auth()
        vk = vk_session.get_api()
        fields = 'country, city, sex, relation, bdate, books, music'
        result = vk.users.get(user_ids=list_of_ids, fields=fields)
        for i, el in enumerate(result):
            el['offset'] = i
            try:
                el['city'] = el['city']['title']
            except Exception as exs:
                el['city'] = "Нет данных"
                print(f'Ошибка при идентификации города для id из списка "Избранное": {exs}')

        return result
