import os 
import json 
from openai import OpenAI 
from typing import Dict
import ast
import json 

from app.src.database.secret import API_TOKEN
import DB_alchemy as db

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=API_TOKEN,
)

async def get_user_tasks_and_prefs(user_id: int) -> tuple:
    prefs = await db.get_user_prefs(user_id)  
    tasks = await db.get_user_tasks(user_id) 

    return prefs, tasks


async def ask_qwen_to_sort_tasks(user_id: int) -> Dict[str, any]:
    #await db.init_db()

    prefs, tasks = await get_user_tasks_and_prefs(user_id)
    prod_time = prefs#.get("productivity_time", "UNFIND prod_time")
    notes = prefs#.get("notes", "UNFIND notes")


    # КОСТЫЛЬ 
    #
    task_list = []
    #if tasks:
    #   task_list.append(dict(tasks))

    if not task_list:
       task_list = [
          {"title": "Прочитать статью", "priority": 2},
          {"title": "Сделать задачу", "priority": 1},
          {"title": "Написать письмо", "priority": 3}
        ]

    #print("Tasks")
    #for task in task_list:
     #   print("\t", task)


    messages=[
        {
            "role": "system",
            "content": """
            Ты — персональный ассистент по планированию задач. 
            Пользователь предоставляет свои предпочтения по времени продуктивности и список задач.
            Ты должен отсортировать задачи по приоритету и соответствию времени суток, учитывая его биоритм"""
        },
        {
            "role": "user",  # сообщение от пользователя
               "content": f"""
                    Вот мои настройки продуктивности:
                    - Время пиковой продуктивности: {prod_time}
                    - Дополнительные заметки: {notes}

                    Вот задачи в формате JSON:
                    {json.dumps(task_list, ensure_ascii=False, indent=2)}
                    Отсортируй задачи по приоритету и соответствию времени дня.
                    Пожалуйста, отсортируй задачи по времени дня и приоритету, учитывая мою продуктивность.
                    Верни результат в формате JSON, где каждая задача содержит поля:
                        название задачи: 
                       x     время начала: _time,
                            время окончания: _time
                    Ответ должен быть только валидный JSON, без дополнительного текста.
                """
            }
        ]

    completion = client.chat.completions.create(
        model="Qwen/Qwen3-VL-30B-A3B-Instruct:novita",
        messages=messages,
        temperature=0.3  # хочу четкие ответы с большой вероятностью правильного ответа 
    )

    # completion - объект ответа, choices - все возможные ответы модели
    # message.content - поле, в котором содержится текст ответа модели 
    response_text = completion.choices[0].message.content
    print("Ответ от Qwen:")
    print(response_text)

    try:
        cleaned_response = response_text.strip()
        sorted_tasks = json.loads(cleaned_response)
        print("JSON succefuly PARSED")
        return sorted_tasks 
    except json.JSONDecodeError as e:
        print(f"ERROR of parsing: {e}")
        return None 

import json
import re

def save_to_json(answer_text, output_filename='answer.json'):
    """
    Пытается сохранить answer_text как JSON в файл.
    
    Поддерживает:
      - уже распарсенный dict/list
      - строку с чистым JSON
      - строку в блоке ```json ... ```
    
    Возвращает:
      - True, если успешно сохранено
      - False, если не удалось
    """
    if answer_text is None:
        print("❌ Ответ пуст (None)")
        return False

    # Если уже Python-объект (dict/list) — сразу сохраняем
    if isinstance(answer_text, (dict, list)):
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(answer_text, f, ensure_ascii=False, indent=2)
            print(f"✅ Успешно сохранено в {output_filename}")
            return True
        except Exception as e:
            print(f"❌ Ошибка при сохранении объекта: {e}")
            return False

    # Если это не строка — нечего парсить
    if not isinstance(answer_text, str):
        print(f"❌ Неподдерживаемый тип данных: {type(answer_text)}")
        print(f"Значение: {repr(answer_text)}")
        return False

    # Очистка от markdown-блоков: ```json ... ``` или просто ```
    cleaned = answer_text.strip()
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1).strip()
    else:
        # Если нет блока — используем как есть
        pass

    if not cleaned:
        print("❌ Пустая строка после очистки")
        return False

    # Попытка распарсить как JSON
    try:
        data = json.loads(cleaned)
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON успешно сохранён в {output_filename}")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Не удалось распарсить JSON: {e}")
        print(f"Сырой текст: {repr(cleaned)}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

if __name__ == "__main__":
    ask_qwen_to_sort_tasks