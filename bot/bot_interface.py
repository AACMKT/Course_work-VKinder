import json
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from api.api_requests import VKSearch, read_token
from bot.bot_logic import BotVariables

CALLBACK_TYPES = ("show_snackbar", "open_link", "open_app")

msg = BotVariables()


def choose_keyboard(req_input, dis_fav_button: bool = False):
    """
    Returns keyboard in dependents on navigation command-message.
    :param req_input: str (keyboard initiating message)
    :param dis_fav_button: bool (marker for enabling or disabling "Просмотреть избранное" button)
    :return: dict (keyboard)
    """
    keyboards = {
        msg.SET_FILTERS: initiate_inline_keyboard(),
        msg.EXIT: empty_keyboard(),
        msg.TO_MAIN_MENU: main_menu_update(dis_fav_button),
    }

    if req_input in keyboards.keys():
        return keyboards[req_input]
    else:
        print(f'Keyboard {req_input} is not found')
        return main_menu_update(dis_fav_button)


def forward_backward_keyboard(menu_curr,
                              bw_color=VkKeyboardColor.NEGATIVE, fw_color=VkKeyboardColor.POSITIVE):
    """
    Keyboard for navigation in search results or favorites.
    :param menu_curr: str (flag for switching keyboard settings between search results and favorites)
    :param bw_color: enum (set the color of the button)
    :param fw_color: enum (set the color of the button)
    :return: dict (keyboard)
    """
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button(label=msg.PREVIOUS, color=bw_color)
    keyboard.add_button(label=msg.NEXT, color=fw_color)
    if menu_curr == "New_search":
        keyboard.add_line()
        keyboard.add_button(label=msg.TO_BLACKLIST, color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button(label=msg.TO_FAVORITES, color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button(msg.TO_MAIN_MENU, color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button(msg.EXIT, color=VkKeyboardColor.PRIMARY)

    return keyboard


def main_menu_update(dis_fav_button: bool = False):
    """
    Returns main menu keyboard.
    :param dis_fav_button: bool (True if there are no records in favorites)
    :return: dict (keyboard)
    """
    if dis_fav_button:
        return main_new_user_keyboard()
    else:
        return main_keyboard()


def intro_keyboard():
    """
    Returns keyboard for initiating dialog with bot.
    :return: dict (keyboard)
    """
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button(label=msg.START, color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button(label=msg.EXIT, color=VkKeyboardColor.PRIMARY)
    return keyboard


def pers_data_permission_keyboard():
    """
    Returns keyboard with request for 'personal info collecting' button, if available user info is insufficient.
    :return: dict (keyboard)
    """
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button(label=msg.CONFIRM, color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button(label=msg.EXIT, color=VkKeyboardColor.PRIMARY)
    return keyboard


def main_new_user_keyboard():
    """
    Main menu keyboard without 'Просмотреть избранное' button.
    :return: dict (keyboard)
    """
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button(label=msg.SEARCH, color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button(msg.SET_FILTERS, color=VkKeyboardColor.SECONDARY, payload={"type": 'search'})
    keyboard.add_line()
    keyboard.add_button(msg.EXIT, color=VkKeyboardColor.PRIMARY)

    return keyboard


def main_keyboard():
    """
    Main menu keyboard with 'Просмотреть избранное' button.
    :return: dict (keyboard)
    """
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button(label=msg.SEARCH, color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button(msg.SET_FILTERS, color=VkKeyboardColor.SECONDARY, payload={"type": 'search'})
    keyboard.add_button(msg.VIEW_FAVORITES, color=VkKeyboardColor.NEGATIVE, payload={"type": 'search'})
    keyboard.add_line()
    keyboard.add_button(msg.EXIT, color=VkKeyboardColor.PRIMARY)

    return keyboard


def search_details_keyboard():
    """
    Returns simplified main menu after missed user personal info collecting process.
    :return: dict (keyboard)
    """
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button(label=msg.SEARCH, color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button(msg.EXIT, color=VkKeyboardColor.PRIMARY)

    return keyboard


def empty_keyboard():
    """
    Returns keyboard without buttons.
    :return: dict (empty keyboard)
    """
    keyboard = VkKeyboard(one_time=True)
    return keyboard.get_empty_keyboard()


def initiate_inline_keyboard():
    """
    Returns specified buttons straight to the chat with current user.
    :return: dict (in-message chat buttons)
    """
    keyboard = VkKeyboard(one_time=False, inline=True)
    keyboard.add_callback_button(label="Изменить 'возраст от' ", color=VkKeyboardColor.POSITIVE,
                                 payload={"type": "age_from_request"})
    keyboard.add_line()
    keyboard.add_callback_button(label="Не менять 'возраст от'", color=VkKeyboardColor.NEGATIVE,
                                 payload={"type": "skip_age_from_change"})

    return keyboard


def get_age_from_change():
    """
    Returns specified buttons straight to the chat with current user.
    :return: dict (in-message chat buttons)
    """
    keyboard = VkKeyboard(one_time=False, inline=True)
    keyboard.add_callback_button(label="Увеличить на 5 лет ", color=VkKeyboardColor.POSITIVE,
                                 payload={"type": "age_from_up"})
    keyboard.add_line()
    keyboard.add_callback_button(label="Уменьшить на 5 лет", color=VkKeyboardColor.SECONDARY,
                                 payload={"type": "age_from_down"})

    return keyboard


def req_age_to_change():
    """
    Returns specified buttons straight to the chat with current user.
    :return: dict (in-message chat buttons)
    """
    keyboard = VkKeyboard(one_time=False, inline=True)
    keyboard.add_callback_button(label="Изменить 'возраст до' ", color=VkKeyboardColor.POSITIVE,
                                 payload={"type": "age_to_request"})
    keyboard.add_line()
    keyboard.add_callback_button(label="Не менять 'возраст до'", color=VkKeyboardColor.NEGATIVE,
                                 payload={"type": "skip_age_to_change"})

    return keyboard


def get_age_to_change():
    """
    Returns specified buttons straight to the chat with current user.
    :return: dict (in-message chat buttons)
    """
    keyboard = VkKeyboard(one_time=False, inline=True)
    keyboard.add_callback_button(label="Увеличить на 5 лет ", color=VkKeyboardColor.POSITIVE,
                                 payload={"type": "age_to_up"})
    keyboard.add_line()
    keyboard.add_callback_button(label="Уменьшить на 5 лет", color=VkKeyboardColor.SECONDARY,
                                 payload={"type": "age_to_down"})

    return keyboard


def req_status_change():
    """
    Returns specified buttons straight to the chat with current user.
    :return: dict (in-message chat buttons)
    """
    keyboard = VkKeyboard(one_time=False, inline=True)
    keyboard.add_callback_button(label="Выбрать статус 'не состоит в браке'", color=VkKeyboardColor.POSITIVE,
                                 payload={"type": "status_not_married"})
    keyboard.add_line()
    keyboard.add_callback_button(label="Выбрать статус 'В активном поиске'  ", color=VkKeyboardColor.NEGATIVE,
                                 payload={"type": "status_in_search"})

    return keyboard


def req_hometown_change():
    """
    Returns specified buttons straight to the chat with current user.
    :return: dict (in-message chat buttons)
    """
    keyboard = VkKeyboard(one_time=False, inline=True)
    keyboard.add_callback_button(label="Изменить город", color=VkKeyboardColor.POSITIVE,
                                 payload={"type": "status_change_city"})
    keyboard.add_line()
    keyboard.add_callback_button(label="Не менять город", color=VkKeyboardColor.NEGATIVE,
                                 payload={"type": "skip_city_change"})

    return keyboard


def send_keyboard(session, user_id, keyboard, message="Обрабатываю запрос"):
    """
    Activates chosen keyboards and sends messages to current user.
    :param session: class 'vk_api.vk_api.VkApiMethod'
    :param user_id: int (active user vk id)
    :param keyboard: dict (required keyboard)
    :param message: str (required message to user)
    """
    if type(keyboard) is not str:
        session.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
            message=message
        )
    else:
        session.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            message="До свидания!"
        )


def send_message(session, user_id, message):
    """
    Sends messages to current user.
    :param session: class 'vk_api.vk_api.VkApiMethod'
    :param user_id: int (active user vk id)
    :param message: str (required message to user)
    """
    try:
        session.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            message=message
        )
    except Exception as exs:
        print(f'Ошибка при отправке сообщения {exs}')


def photos_send(session, user_id, attachment):
    """
    Sends chosen photos to the chat with current user.
    :param session: class 'vk_api.vk_api.VkApiMethod'
    :param user_id: int (active user vk id)
    :param attachment: list (links to photos in special format)
    """
    session.messages.send(
        user_id=user_id,
        random_id=get_random_id(),
        attachment=attachment
    )


def out_of_range_notification(session, user_id):
    """
    Sends message if current user tries to get out of the left border of the search results.
    :param session: class 'vk_api.vk_api.VkApiMethod'
    :param user_id: int (active user vk id)
    :return: str (message to current user)
    """
    session.messages.send(
        user_id=user_id,
        random_id=get_random_id(),
        message='Вы уже вначале списка результатов запроса!!!'
    )


def edit_inline_keyboard(session, event, keyboard):
    """
    Sends to user (by editing previous one) inline (inside the chat) keyboard in accordance with incoming events.
    :param session: class 'vk_api.vk_api.VkApiMethod'
    :param event: class vk longpool event object
    :param keyboard: dict (in-message chat buttons)
    """
    session.messages.edit(
        peer_id=event.obj.peer_id,
        message="'Внимание! Изменение фильтров сбросит историю поиска\nВведите возраст",
        conversation_message_id=event.obj.conversation_message_id,
        keyboard=keyboard.get_keyboard()
    )


def switch_inline_keyboard(session, event, db_response):
    """
    Returns inline buttons and message during missed user's personal info collecting process.
    :param session: class 'vk_api.vk_api.VkApiMethod'
    :param event: class vk longpool event object
    :param db_response: bool (True if params withing the range and False in they are not)
    :return: dict + str (required keyboard + message)
    """
    inline_events = {"age_from_request": [get_age_from_change(), 'Выберите вариант:', 'Empty'],
                     "skip_age_from_change": [req_age_to_change(), 'Желаете изменить "Возраст до"?', 'Empty'],
                     "age_from_up": [req_age_to_change(), 'Возраст от - изменен',
                                     'Выход из допустимых границ. "Возраст от" поднят до "Возраст до" - 2 года'],
                     "age_from_down": [req_age_to_change(), 'Возраст от - изменен',
                                       'Выход из допустимых границ. "Возраст от" снижен до 16 лет'],
                     "age_to_request": [get_age_to_change(), 'Выберите вариант:', 'Empty'],
                     "skip_age_to_change": [req_status_change(), 'Желаете изменить "Статус"?', 'Empty'],
                     "age_to_up": [req_status_change(), 'Возраст до - изменен',
                                   'Выход из допустимых границ. "Возраст до" поднят до 75 лет'],
                     "age_to_down": [req_status_change(), 'Возраст до - изменен',
                                     'Выход из допустимых границ. "Возраст до" снижен до "Возраст от" + 2 года'],
                     "status_not_married": [req_hometown_change(), 'Статус - изменен', 'Empty'],
                     "status_in_search": [req_hometown_change(), 'Статус - изменен', 'Empty'],
                     "status_change_city": [empty_keyboard(), 'Введите название города:', 'Empty'],
                     "skip_city_change": [search_details_keyboard(), 'Фильтры сохранены!', 'Empty']
                     }

    var = event.object.payload.get('type')
    if var in inline_events.keys():
        if inline_events[var][0] != empty_keyboard():
            if db_response is False and inline_events[var][1] != 'Empty':
                message = inline_events[var][2]
            else:
                message = inline_events[var][1]
            session.messages.edit(
                peer_id=event.obj.peer_id,
                message=message,
                conversation_message_id=event.obj.conversation_message_id,
                keyboard=inline_events[var][0].get_keyboard(),
            )
        else:
            session.messages.edit(
                peer_id=event.obj.peer_id,
                message=inline_events[var][1],
                conversation_message_id=event.obj.conversation_message_id,
                keyboard=inline_events[var][0]
            )


def send_default_callback_keyboard(session, event):
    """
    Function for chat functionality expanding purpose. Allows to send to user standard VK API callback buttons.
    :param session: class 'vk_api.vk_api.VkApiMethod'
    :param event: class vk longpool event object
    :return: dict (keyboard with callback buttons)
    """
    session.messages.sendMessageEventAnswer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
        event_data=json.dumps(event.object.payload),
    )


def forward_backward_navigation(search_res_list, counter: int, menu_curr='New_search'):
    """
    Prepare keyboard & message to user in accordance with user actions during navigation in search results or favorites.
    :param search_res_list: list (with dicts, containing info about matches or favorites)
    :param counter: int (current position in the result's list)
    :param menu_curr: str (flag for switching keyboard settings between search results and favorites)
    :return: dict (with message and proper keyboard)
    """
    if menu_curr == 'Favorites' and len(search_res_list) == 0:
        keyboard = main_keyboard()
        info = 'Вы еще никого не добавили в "Избранное"'
        print('Список избранного пуст!')
    else:
        if counter < 0:
            info = 'Вы уже вначале списка результатов запроса!!!'
            counter = 0

        elif 0 <= counter <= len(search_res_list) - 1:
            info = f'Имя: {search_res_list[counter]["first_name"]} \n' + \
                   f'Фамилия: {search_res_list[counter]["last_name"]} \n' + \
                   f'Город: {search_res_list[counter]["city"]}' + \
                   f'\n ссылка: {"https://vk.com/id" + str(search_res_list[counter]["id"])}'
        else:
            info = 'Вы просмотрели все результаты в рамках текущего запроса'
        if len(search_res_list) == 1:
            keyboard = forward_backward_keyboard(menu_curr,
                                                 bw_color=VkKeyboardColor.SECONDARY, fw_color=VkKeyboardColor.SECONDARY)
        elif 0 < counter < len(search_res_list) - 1 and len(search_res_list) != 1:
            keyboard = forward_backward_keyboard(menu_curr,
                                                 bw_color=VkKeyboardColor.NEGATIVE, fw_color=VkKeyboardColor.POSITIVE)
        elif counter == 0 and len(search_res_list) != 1:
            keyboard = forward_backward_keyboard(menu_curr,
                                                 bw_color=VkKeyboardColor.SECONDARY, fw_color=VkKeyboardColor.POSITIVE)
        else:
            keyboard = forward_backward_keyboard(menu_curr,
                                                 bw_color=VkKeyboardColor.NEGATIVE, fw_color=VkKeyboardColor.SECONDARY)

    res = {'info': info, 'keyboard': keyboard}

    return res


def send_match_photos(session, user_id, search_res_list, counter: int = 0):
    """
    Sends photos of the viewing 'match' to the chat with current user.
    :param session: class 'vk_api.vk_api.VkApiMethod'
    :param user_id: int (active user vk id)
    :param search_res_list: list (with dicts, containing info about matches or favorites)
    :param counter: int (current position in the result's list)
    :return: dict
    """
    request = VKSearch(token=read_token())
    if 0 <= counter < len(search_res_list):
        match_id = search_res_list[counter]['id']
        attachments = request.get_photos(match_id)['photos']

        session.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            message='Фото с профиля:',
            attachment=attachments
        )


def stop_chatting(session, triggers_dict: dict, user_id):
    """
    Reset triggers and clear keyboards
    :param session:
    :param triggers_dict: dict (contains active users positional triggers and variables values)
    :param user_id: int (active user vk id)
    """
    kb_ = empty_keyboard()
    send_keyboard(session, user_id, kb_)
    msg.reset_triggers(triggers_dict, user_id)
