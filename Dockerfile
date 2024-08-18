FROM python:3.10

# Устанавливаем рабочую директорию
WORKDIR /src

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем весь код проекта

