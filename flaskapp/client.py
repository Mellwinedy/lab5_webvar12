import requests

r = requests.get('http://localhost:5000/')
print('Статус главной:', r.status_code)

try:
    r = requests.get('http://localhost:5000/noise')
    print('Статус /noise:', r.status_code)
    if r.status_code != 200:
        exit(1)
except Exception as e:
    print('Ошибка:', e)
    exit(1)