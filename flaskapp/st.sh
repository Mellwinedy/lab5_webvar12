#!/bin/bash

# Запускаем Gunicorn в фоне, запоминаем его PID
gunicorn --bind 127.0.0.1:5000 wsgi:app & APP_PID=$!

# Ждём, пока сервер стартует
sleep 25

# Запускаем клиент-тест
echo "start client"
python3 client.py
APP_CODE=$?

# Убиваем сервер
sleep 5
echo "kill $APP_PID"
kill -TERM $APP_PID

# Возвращаем код клиента — если тест упал, Travis увидит ошибку
echo "app code $APP_CODE"
exit $APP_CODE