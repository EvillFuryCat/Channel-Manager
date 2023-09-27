# def check_similaritys(db, target_string):
#     # Создание клиента Redis
#     # Получение списка всех ключей
#     keys = db.get_keys()
#     # Проверка каждого ключа
#     for key in keys:
#         # Преобразование ключа из байтов в строку
#         key = key.decode('utf-8')
#         # Получение значения по текущему ключу из Redis
#         stored_string = db.get_data(key)

#         if stored_string is not None:
#             # Преобразование значения из байтов в строку
#             #stored_string = stored_string.decode('utf-8')

#             # Разделение строк на отдельные слова
#             #stored_words = stored_string.split(", ")
#             target_words = target_string.split(", ")
#             print(target_words, "target_words")
#             #print(stored_words, "stored_words")


#             # Проверка наличия совпадений
#             for word in stored_words:
#                 if word in target_words:
#                     return True

#     return False


def check_similarity(db, target_string: str):
    if db.get_data(target_string) is not None:
        return True
    else:
        target_words = target_string.split(", ")
        keys = db.get_keys()
        for target_key in target_words:
            for key in keys:
                key = key.decode("utf-8").split(", ")
                if target_key in key:
                    return True

    return False
