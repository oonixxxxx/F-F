# F-F

# Создание виртуального окружения
py -m venv venv

# Активация виртуального окружения
venv\Scripts\activate

# Обновление pip до последней версии (рекомендуется)
python -m pip install --upgrade pip

# Установка всех библиотек из requirements.txt
pip install -r requirements.txt

# запуска файла из корневой директории:
python -m app.src.bot.main