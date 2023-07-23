from vk_api.bot_longpoll import VkBotEventType
from api.api_requests import VKSearch
import database.databases as db
import re
import datetime as dt


def greeting_message(user_id, user_token, user_info=None) -> str:
    """
    Prepares "greeting message" with search filters details.
    :param user_id: int (active user vk id)
    :param user_token: str (vk user's personal token)
    :param user_info: dict (user params, received by VK API 'users.get')
    :return: str
    """
    request = VKSearch(token=user_token)
    response = {}
    try:
        response = db.get_params(user_id)

    except Exception:
        try:
            response = request.get_search_params(user_params=user_info)
        except Exception as exs:
            print(f'Ошибка при запросе параметров поиска: {exs}')

    if "status" in response.keys():
        if int(response["status"]) == 6:
            status = "В активном поиске"
        elif int(response["status"]) == 1:
            status = "Не состоит в браке"
        else:
            status = "Не учитывать"
    else:
        status = "Не определен"

    if "sex" in response.keys():
        if int(response["sex"]) == 1:
            sex = "женский"
        elif int(response["sex"]) == 2:
            sex = "мужской"
        else:
            sex = "не указан"
    else:
        sex = "не определен"

    if len(response) > 0:
        msg = f'Приветствую!\nВнимательно проверьте критерии поиска!\nвозраст от: {response["age_from"]}\n' + \
              f'возраст до: {response["age_to"]}\nгород: {response["hometown"]}\nстатус отношений: {status}\n' + \
              f'пол: {sex}\nВы можете поменять некоторые критерии, нажав "Настроить фильтры"'
    else:
        msg = f'Не удалось определить все параметры поиска. Могут быть ошибки при выполнении запросов.\n' + \
              f'Вы можете указать некоторые критерии вручную, нажав "Настроить фильтры"'

    return msg


def get_user_id(pool_event):
    """
    Provides active user id, depending on what event type is tracking.
    :param pool_event: class vk longpool event object
    :return: int (bot active user id)
    """
    if pool_event.type == VkBotEventType.MESSAGE_NEW:
        user_id = pool_event.obj.message['from_id']
    elif pool_event.type == VkBotEventType.MESSAGE_EVENT:
        user_id = pool_event.object.user_id
    elif pool_event.type == VkBotEventType.MESSAGE_REPLY:
        user_id = None
    else:
        user_id = None
        print(f'ERROR EVENT {pool_event}')
    return user_id


def provide_search_results(user_params=None, user_id=None, user_token=None, black_list=None, offset=0):
    """
    Provides list with dict, contain matches personal data.
    :param user_params: dict (user params, received by VK API 'users.get')
    :param user_id: int (active user vk id)
    :param user_token: str (vk user's personal token)
    :param black_list: list (of blocked id's)
    :param offset: int (search offset)
    :return: list (with dicts)
    """
    request = VKSearch(token=user_token)
    if user_params is not None:
        params = request.get_search_params(user_params=user_params)
    else:
        params = request.get_search_params(user_id=user_id)
    matches = request.find_match(params, black_list=black_list, offset=offset)

    return matches


def get_birth_date(event):
    """
    Compares imputed date with pattern and converts it into proper format, if required.
    :param event: class vk longpool event object
    :return: str (date in format dd.mm.yyyy)
    """
    response = event.obj.message['text']
    try:
        char = ['/', '_', '-', '\\', ' ', ',', 'ю', ':', 'б']
        for s in char:
            response = response.replace(s, '.')
        pattern = r'(\d{2})[.]+(\d{2})[.]+(\d{2,4})'
        date = re.search(pattern, str(response))
        day = date.group(1)
        month = date.group(2)
        year = date.group(3)

        if int(month) > 12:
            if int(day) <= 12:
                temp = day
                day = month
                month = temp
            else:
                raise Exception
        if str(month)[0] == '0':
            month = month[1]
        if len(year) < 4:
            if int(year[-2:]) >= 47:
                year = '19' + str(year[-2:])
            else:
                year = '20' + str(year[-2:])
        if (int(year) > int(dt.datetime.now().year) - 15) or (int(year) < 1947):
            print(f'Ошибка ввода года: {year} - за допустимым диапазоном')
            raise Exception
        date = f'{day}.{month}.{year}'

        return date

    except Exception:
        print('Не получилось распознать дату или дата выходит за допустимый диапазон. Повторите ввод.')

        return 'Fail'


def get_city(event):
    """
    Compares imputed city with pattern and converts it into proper format, if required.
    :param event: class vk longpool event object
    :return: str (date in format dd.mm.yyyy)
    """
    response = event.obj.message['text']
    pattern1 = r'^[a-zA-Zа-яА-Я-]*\Z'
    try:
        if re.search(pattern1, response) is not None and len(response) > 2:
            response = response.capitalize()
            print(response)

            return response
        else:
            raise Exception

    except Exception:
        print('Похоже на ошибку ввода. Повторите ввод.')

        return 'Fail'


def get_sex(event):
    """
    Receives gender info and returns 'Fail' (if input is incorrect), 1 or 2, according to VK API requirements.
    :param event: class vk longpool event object
    :return: str (date in format dd.mm.yyyy)
    """
    response = event.obj.message['text']
    pattern1 = r'[мМmM]\w*'
    pattern2 = r'[жЖfF]\w*'

    if re.search(pattern1, response) is not None:
        return 2
    elif re.search(pattern2, response) is not None:
        return 1
    else:
        print('Похоже на ошибку ввода. Повторите ввод.')
        return 'Fail'


def get_search_offset(search_res_list, counter):
    """
    Returns actual search offset (current position in search results).
    :param search_res_list: list (with matches personal info dicts)
    :param counter: int (position of currently viewing record in search_res_list)
    :return: int (next search initial offset)
    """
    if len(search_res_list) > 0:
        if 0 <= counter < len(search_res_list):
            offset = search_res_list[counter]['offset']
        elif counter < 0:
            offset = search_res_list[0]['offset']
        else:
            offset = search_res_list[len(search_res_list) - 1]['offset']
    else:
        offset = 0

    return int(offset)


def add_to_black_list(event_text, user_id, matches, counter):
    match = matches[counter]
    if 0 < counter <= len(matches) - 1:
        counter = counter
    elif counter < 0:
        counter = 0
    else:
        counter = len(matches) - 1
    match = matches[counter]
    option = {
        'В черный список': ["Запись внесена в черный список",
                            "При попытке добавления записи в 'Черный список', произошла ошибка",
                            db.add_black_list(match, user_id)]
    }
    if event_text in option.keys():
        try:
            var = option[event_text][2]
            if var is False:
                message = 'Такая запись уже существует в списке!'
            else:
                message = option[event_text][0]

        except Exception as exs:
            message = option[event_text][1]
            print(f'Ошибка при добавлении: {exs}')
        return message
    else:
        return False


def add_to_favorites(event_text, user_id, matches, counter):
    """
    Adds chosen record to favorites and provides user with corresponding message.
    :param event_text: str (event text has to be 'В избранное', otherwise - error message)
    :param user_id: int (active user vk id)
    :param matches: list (with matches personal info dicts)
    :param counter: int (position of currently viewing record in search_res_list)
    :return: str (message to user)
    """
    if 0 < counter <= len(matches) - 1:
        counter = counter
    elif counter < 0:
        counter = 0
    else:
        counter = len(matches) - 1
    match = matches[counter]
    option = {
        'В избранное': ["Запись успешно добавлена в избранное",
                        "При попытке добавления записи в 'Избранное', произошла ошибка",
                        db.add_favorite(match, user_id)],
    }
    if event_text in option.keys():
        try:
            var = option[event_text][2]
            if var is False:
                message = 'Такая запись уже существует в списке!'
            else:
                message = option[event_text][0]

        except Exception as exs:
            message = option[event_text][1]
            print(f'Ошибка при добавлении: {exs}')
        return message
    else:
        return False


def disable_favorites_button(favorites_list):
    if len(favorites_list) > 0:
        return False
    else:
        return True
