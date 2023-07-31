from vk_api import VkUpload, VkApi
import re
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from api.api_requests import read_token, VKSearch
import bot.bot_interface as keyboard
from bot.bot_interface import CALLBACK_TYPES
import bot.bot_logic as logic
from bot.bot_user_auth import missed_user_data_collector
from database import databases as db
from config import token_soob, group_id

# Устанавливаем соединение.
vk_session = VkApi(token=token_soob, api_version='5.131')
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, group_id=group_id)
upload = VkUpload(vk)
user_token = read_token()
request = VKSearch(token=user_token)
# Объявляем переменные.
matches = []
to_bl_trigger = False
forward_trigger = False
to_bl_permission = True
to_fav_permission = True
counter = 0
offset = 0
current_offset = 0
us_id = 0
favorites = False
settings_change = False
menu_curr = "Main"
res_source = {}
user_info = {}
active_users = {}
bl_list = []
favorites_list = []


# Стартуем.
if __name__ == '__main__':
    for event in longpoll.listen():
        navi = logic.BotVariables()
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_user:
                us_id = logic.get_user_id(event)
                if us_id not in active_users.keys():
                    active_users[us_id] = {}
                    navi.reset_triggers(active_users, us_id)
                    active_users[us_id]['counter'] = 0
                    active_users[us_id][menu_curr] = 'Main'
                # Проверяем/получаем список 'Избранное'
                favorites_list = db.get_favorite(us_id)
                favorites = logic.disable_favorites_button(favorites_list)
                if not active_users[us_id]['first_stage']:
                    # Инициализация. Берем id пользователя.
                    us_id = logic.get_user_id(event)
                    favorites_list = db.get_favorite(us_id)
                    favorites = logic.disable_favorites_button(favorites_list)
                    # Проверяем есть ли он в БД. Если есть, то пропускаем все шаги проверки данных пользователя.
                    if not db.check_user(us_id):
                        user_info = request.get_user(us_id)
                    else:
                        user_info = request.get_user(us_id)
                        active_users[us_id]['third_stage'] = True
                    # Если нет - забираем данные пользователя и проверяем
                    kb = keyboard.intro_keyboard()
                    name = user_info['first_name']
                    msg = f'Здравствуйте {name}! для начала работы нажмите "Начать работу".'
                    keyboard.send_keyboard(vk, us_id, kb, message=msg)
                    active_users[us_id]['first_stage'] = True

                elif event.obj.message['text'] == navi.EXIT:
                    keyboard.stop_chatting(vk, active_users, us_id)
                    active_users[us_id]['menu_curr'] = "Main"
                    active_users[us_id]['counter'] = 0

                elif event.obj.message['text'] != navi.EXIT:
                    us_id = logic.get_user_id(event)
                    active_users[us_id]['first_stage'] = True
                    active_users[us_id]['second_stage'] = True
                if active_users[us_id]['first_stage'] and active_users[us_id]['second_stage'] \
                        and not active_users[us_id]['third_stage']:
                    user_info = request.get_user(us_id)
                    if 'bdate' not in user_info.keys() \
                            or not re.match(navi.REG_EX, user_info['bdate']) \
                            or 'city' not in user_info.keys() or 'sex' not in user_info.keys() or user_info['sex'] == 0:
                        kb = keyboard.pers_data_permission_keyboard()
                        if event.obj.message['text'] != navi.CONFIRM:
                            msg = f'Для работы приложения нам необходимы дополнительные данные,' + \
                                  f'которых нет в вашем профиле.' + \
                                  f'\nВы согласны их предоставить?'
                            keyboard.send_keyboard(vk, us_id, kb, message=msg)
                        if event.obj.message['text'] != navi.EXIT:
                            user_info = missed_user_data_collector(vk, longpoll, us_id, user_info, count=0)
                            # Добавляем параметры поиска пользователя в БД.
                            if user_info is not False:
                                search_params_for_db = request.get_search_params(user_params=user_info)
                                db.add_user(us_id)
                                search_params_for_db['id'] = us_id
                                db.add_setting_search(search_params_for_db)
                            else:
                                kb = keyboard.empty_keyboard()
                                keyboard.send_keyboard(vk, us_id, kb)
                                navi.reset_triggers(active_users, us_id)

                            if user_info is False:
                                navi.reset_triggers(active_users, us_id)
                            else:
                                active_users[us_id]['first_stage'] = True
                                active_users[us_id]['second_stage'] = True
                                active_users[us_id]['third_stage'] = True
                        if event.obj.message['text'] == navi.CONFIRM:
                            active_users[us_id]['third_stage'] = True
                        elif event.obj.message['text'] == navi.EXIT:
                            keyboard.stop_chatting(vk, active_users, us_id)
                    else:
                        db.add_user(us_id)
                        search_params_for_db = request.get_search_params(user_params=user_info)
                        search_params_for_db['id'] = us_id
                        db.add_setting_search(search_params_for_db)
                        active_users[us_id]['third_stage'] = True

                # После всех проверок - выдаем клавиатуру.
                us_id = logic.get_user_id(event)
                if event.obj.message['text'] != '' and active_users[us_id]['first_stage'] \
                        and active_users[us_id]['second_stage'] and active_users[us_id]['third_stage']:
                    if not active_users[us_id]['forth_stage']:
                        kb = keyboard.main_menu_update(dis_fav_button=favorites)
                        message = logic.greeting_message(us_id, user_token=read_token(), user_info=user_info)
                        keyboard.send_keyboard(vk, us_id, kb, message=message)

                        active_users[us_id]['forth_stage'] = True
                    else:
                        # Обрабатываем событие "при настройке фильтров поиска".
                        us_id = logic.get_user_id(event)
                        if vk.messages.getHistory(user_id=us_id, count=2)['items'][1]['text'] \
                                == 'Введите название города:':
                            city = vk.messages.getHistory(user_id=us_id, count=2)['items'][0]['text']
                            keyboard.send_keyboard(vk, us_id, keyboard=keyboard.search_details_keyboard(),
                                                   message='Город изменен')
                            db.update_hometown(us_id, city)
                        elif event.obj.message['text'] not in \
                                [navi.NEXT, navi.PREVIOUS, navi.SEARCH, navi.VIEW_FAVORITES, navi.TO_FAVORITES,
                                 navi.TO_BLACKLIST]:
                            kb = keyboard.choose_keyboard(event.obj.message['text'], dis_fav_button=favorites)
                            keyboard.send_keyboard(vk, us_id, kb)
                        # Сбрасываем все флаги, если пользователь нажал "Окончить сеанс".
                        else:
                            if event.obj.message['text'] == navi.EXIT:
                                keyboard.stop_chatting(vk, active_users, us_id)
                            # Готовимся к выдаче результатов, загружаем результаты, соответствующие критериям поиска.
                            if event.obj.message['text'] == navi.SEARCH:
                                menu_curr = 'New_search'
                                us_id = logic.get_user_id(event)
                                active_users[us_id]['menu_curr'] = menu_curr
                                if settings_change:
                                    db.update_offset(0, us_id)
                                    settings_change = False
                                offset = current_offset
                                if db.check_user(us_id) is False:
                                    res_source[us_id] = logic.provide_search_results(user_params=user_info,
                                                                                     user_token=read_token(),
                                                                                     offset=offset)
                                else:
                                    us_id = logic.get_user_id(event)
                                    black_list = db.get_black_list(us_id)
                                    res_source[us_id] = request.find_match(db.get_params(us_id),
                                                                           black_list=black_list)

                            # Готовим данные по id попавшим в "Избранное".
                            if event.obj.message['text'] == navi.VIEW_FAVORITES:
                                menu_curr = 'Favorites'
                                us_id = logic.get_user_id(event)
                                active_users[us_id]['menu_curr'] = menu_curr
                                list_of_ids = db.get_favorite(us_id)

                                res_source[us_id] = request.get_favorites_by_id(list_of_ids)

                            if event.obj.message['text'] == navi.TO_BLACKLIST:
                                us_id = logic.get_user_id(event)
                                counter = int(active_users[us_id]['counter'])
                                if counter <= len(matches) - 1:
                                    banned_id = matches[counter]['id']
                                else:
                                    banned_id = matches[len(matches) - 1]['id']
                                bl_list = [{"id": banned_id}]
                                for i, v in enumerate(res_source[us_id]):
                                    if int(v['id']) == int(banned_id):
                                        del res_source[us_id][i]
                                to_bl_trigger = True
                            us_id = logic.get_user_id(event)
                            matches = res_source[us_id]
                            # Готовим навигацию по списку совпадений или списку из "Избранного".
                            if us_id in res_source.keys():
                                if event.obj.message['text'] in [navi.SEARCH, navi.VIEW_FAVORITES]:
                                    counter = 0
                                    active_users[us_id]['counter'] = counter
                                elif event.obj.message['text'] == navi.NEXT:
                                    us_id = logic.get_user_id(event)
                                    if us_id in active_users.keys():
                                        counter = int(active_users[us_id]['counter'])
                                    counter, to_bl_trigger, forward_trigger = \
                                        logic.scroll_forward(counter, to_bl_trigger, forward_trigger)
                                    to_bl_permission = True
                                    to_fav_permission = True
                                    active_users[us_id]['counter'] = counter
                                elif event.obj.message['text'] == navi.PREVIOUS:
                                    us_id = logic.get_user_id(event)
                                    if us_id in active_users.keys():
                                        counter = int(active_users[us_id]['counter'])
                                    counter, to_bl_trigger, forward_trigger = \
                                        logic.scroll_backward(counter, matches, to_bl_trigger, forward_trigger)
                                    to_bl_permission = True
                                    to_fav_permission = True
                                    active_users[us_id]['counter'] = counter
                                # Загружаем "умную" клавиатуру.
                                us_id = logic.get_user_id(event)
                                pos = active_users[us_id]['counter']
                                curr = active_users[us_id]['menu_curr']
                                kb = keyboard.forward_backward_navigation(matches, pos, menu_curr=curr)['keyboard']
                                # Формируем сообщения на события "В черный список" и "В избранное".
                                if event.obj.message['text'] == navi.TO_BLACKLIST:
                                    if to_bl_permission:
                                        user_msg = event.obj.message['text']
                                        us_id = logic.get_user_id(event)
                                        message = logic.add_to_black_list(user_msg, us_id, bl_list, 0)
                                        if message is False:
                                            message = 'Запись уже внесена в "Черный список"'
                                        to_bl_permission = False
                                    else:
                                        message = 'Запись уже внесена в "Черный список"'
                                elif event.obj.message['text'] == navi.TO_FAVORITES:
                                    if to_fav_permission:
                                        user_msg = event.obj.message['text']
                                        us_id = logic.get_user_id(event)
                                        matches = res_source[us_id]
                                        message = logic.add_to_favorites(user_msg, us_id, matches,
                                                                         active_users[us_id]['counter'])
                                        if message is False:
                                            message = 'Запись уже внесена в "В избранное"'
                                        to_fav_permission = False
                                    else:
                                        message = 'Запись уже внесена в "В избранное"'
                                    favorites_list = db.get_favorite(us_id)
                                    favorites = logic.disable_favorites_button(favorites_list)
                                else:
                                    message = \
                                        keyboard.forward_backward_navigation(matches,
                                                                             active_users[us_id]['counter'],
                                                                             menu_curr=curr)['info']
                                us_id = logic.get_user_id(event)
                                keyboard.send_keyboard(vk, us_id, kb, message=message)
                                # Загружаем в чат фото.
                                if event.obj.message['text'] not in [navi.TO_FAVORITES, navi.TO_BLACKLIST]:
                                    us_id = logic.get_user_id(event)
                                    keyboard.send_match_photos(vk, us_id, matches,
                                                               counter=active_users[us_id]['counter'])
                                # Основная часть распределенного кода по обработке "offset" - смещения начала поиска.
                                current_offset = logic.get_search_offset(matches, counter)

                                if db.check_user(us_id) and menu_curr != 'Favorites':
                                    db_offset = current_offset
                                    us_id = logic.get_user_id(event)
                                    db.update_offset(current_offset, us_id)
        # Обрабатываем payload
        if event.type == VkBotEventType.MESSAGE_EVENT:
            # Задел на будущее - обработка стандартных callback-кнопок от API VK.
            if event.object.payload.get("type") in CALLBACK_TYPES:
                keyboard.send_default_callback_keyboard(vk, event)
            # Предоставляем callback-кнопки и корректируем параметры фильтров поиска в БД.
            else:
                payload_event = logic.get_payload_event(event)
                settings_change = payload_event['trigger']
                db_response = payload_event['db_response']
                keyboard.switch_inline_keyboard(vk, event, db_response)
