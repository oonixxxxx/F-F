import os 
import json 
from openai import OpenAI 
from typing import Dict 

import secret as ss
import DB_alchemy as db 


client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=ss.API_TOKEN,
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
                            время начала: _time,
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






