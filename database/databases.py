import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker
from config import database, user, password
from database.models import User, Favorite, BlackList, SettingSearch, create_tables

# создаем движок
DSN = f'postgresql://{user}:{password}@localhost:5432/{database}'
engine = sq.create_engine(DSN)

Session = sessionmaker(bind=engine)
session = Session()


def check_user(id_vk: int) -> bool:
    """Проверка только через переменную id_vk"""
    result = session.query(User).filter(
        User.id == id_vk).all()
    return bool(result)


def add_user(id_vk: int) -> bool:
    """Добавляем в User, поверка через переменную id_vk"""
    result = session.query(User).filter(
        User.id == id_vk).all()
    if not result:
        model = {"id": id_vk}
        session.add(User(**model))
        session.commit()
    return bool(result)


def add_favorite(info: dict, id_vk) -> bool:
    """Добавляем в Favorite, плюс проверка на наличие в таблице"""
    result = session.query(Favorite.id).filter(
        Favorite.id == int(info['id']),
        Favorite.ID_vk_users == int(id_vk)).all()
    if not result:
        model = {"id": info['id'],
                 "ID_vk_users": id_vk}
        session.add(Favorite(**model))
        session.commit()
    else:

        return False


def add_black_list(info: dict, id_vk) -> bool:
    """Добавляем в Black_list, плюс проверка на наличие в таблице"""
    result = session.query(BlackList.id).filter(
        BlackList.id == int(info['id']),
        BlackList.ID_vk_users == int(id_vk)).all()
    if not result:
        model = {"id": info['id'],
                 "ID_vk_users": id_vk}
        session.add(BlackList(**model))
        session.commit()
    else:

        return False


def add_setting_search(info: dict) -> list:
    """добавляем в Setting_search, по умолчанию offset = 1,
    возвращает offset, если id есть в бд"""
    result = session.query(SettingSearch.id, SettingSearch.offset).filter(
        SettingSearch.id == int(info['id'])).all()
    if not result:
        model = {"id": info['id'],
                 "age_from": info['age_from'],
                 "age_to": info['age_to'],
                 "sex": info['sex'],
                 "hometown": info['hometown'],
                 "status": info['status']}
        session.add(SettingSearch(**model))
        session.commit()
    else:
        res = [i.offset for i in result]

        return res


def get_black_list(id_vk: int) -> list:
    """получаем список из black_list"""
    try:
        request = session.query(BlackList.id).filter(
            BlackList.id == id_vk).all()
        res = [i.id for i in request]
    except Exception as exs:
        res = []
        print(f"Ошибка получения значений из табл. BlackList: {exs}")

    return res


def update_offset(info: int, vk_id: int):
    """перезаписывает offset"""
    session.query(SettingSearch).filter(
        SettingSearch.id == vk_id).update(
        {"offset": info})
    session.commit()


def get_params(vk_id: int) -> dict:
    """Возвращаем параметры поиска,"""
    request = session.query(SettingSearch).filter(
        SettingSearch.id == vk_id)
    for item in request:
        params = {"id": item.id,
                  "age_from": item.age_from,
                  "age_to": item.age_to,
                  "hometown": item.hometown,
                  "status": item.status,
                  "sex": item.sex,
                  "offset": item.offset,
                  'fields': 'country, city, sex, relation, bdate, books, music'}

        return params


def get_favorite(vk_id: int) -> list:
    """Возвращаем избранное в виде списка"""
    request = session.query(Favorite).filter(
        Favorite.ID_vk_users == vk_id)
    items = [i.id for i in request]

    return items


def get_age_from(vk_id: int) -> list:
    """Получаем возраст age_from"""
    request = session.query(SettingSearch.age_from).filter(
        SettingSearch.id == vk_id)
    result = [i.age_from for i in request]

    return result


def increase_age_from(vk_id: int):
    """увеличиваем возраст age_from"""
    age_to = get_age_to(vk_id)
    result = get_age_from(vk_id)
    if age_to[0] - result[0] - 7 >= 0:
        session.query(SettingSearch).filter(
            SettingSearch.id == vk_id).update({"age_from": result[0] + 5})
        not_limited = True
    else:
        session.query(SettingSearch).filter(
            SettingSearch.id == vk_id).update({"age_from": age_to[0] - 2})
        not_limited = False
    session.commit()

    return not_limited


def reduce_age_from(vk_id: int):
    """уменьшаем возраст age_from"""
    result = get_age_from(vk_id)
    if result[0] >= 21:
        session.query(SettingSearch).filter(
            SettingSearch.id == vk_id).update({"age_from": result[0] - 5})
        not_limited = True
    else:
        session.query(SettingSearch).filter(
            SettingSearch.id == vk_id).update({"age_from": 16})
        not_limited = False
    session.commit()

    return not_limited


def get_age_to(vk_id: int) -> list:
    """получаем возраст age_to"""
    request = session.query(SettingSearch.age_to).filter(
        SettingSearch.id == vk_id)
    result = [i.age_to for i in request]

    return result


def increase_age_to(vk_id: int):
    """Увеличиваем возраст age_to на 5,
    если равен age_from увеличиваем относительно его."""
    result = get_age_to(vk_id)
    if result[0] + 5 <= 75:
        print('here')
        session.query(SettingSearch).filter(
            SettingSearch.id == vk_id).update({"age_to": result[0] + 5})
        not_limited = True
    else:
        print('not here')
        session.query(SettingSearch).filter(
            SettingSearch.id == vk_id).update({"age_to": 75})
        not_limited = False
    session.commit()

    return not_limited


def reduce_age_to(vk_id: int):
    """уменьшаем возраст age_to на 5,
    если равен age_from приравниваем к нему"""
    age_from = get_age_from(vk_id)
    result = get_age_to(vk_id)
    if age_from[0] <= result[0] - 7:
        session.query(SettingSearch).filter(
            SettingSearch.id == vk_id).update({"age_to": result[0] - 5})
        not_limited = True
    else:
        session.query(SettingSearch).filter(
            SettingSearch.id == vk_id).update({"age_to": age_from[0] + 2})
        not_limited = False
    session.commit()

    return not_limited


def update_hometown(vk_id: int, city: str):
    """Изменяем город"""
    session.query(SettingSearch).filter(
        SettingSearch.id == vk_id).update(
        {"hometown": city})
    session.commit()


def get_status(vk_id: int) -> list:
    """запрос статуса"""
    request = session.query(SettingSearch.status).filter(
        SettingSearch.id == vk_id)
    result = [i.status for i in request]

    return result


def update_status_to_in_active_search(vk_id: int):
    """Меняем статус на в "активном поиске"(6)"""
    session.query(SettingSearch).filter(
        SettingSearch.id == vk_id).update(
        {"status": 6})
    session.commit()

    return True


def update_status_not_married(vk_id: int):
    """Меняем статус на "не состоит в браке"(1)"""
    session.query(SettingSearch).filter(
        SettingSearch.id == vk_id).update(
        {"status": 1})
    session.commit()

    return True


session.close()

if __name__ == '__main__':
    Session = sessionmaker(bind=engine)
    session = Session()

    create_tables(engine)

    session.close()
