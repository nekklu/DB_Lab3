# ЛР №3 MongoDB — задание 9

Скрипт `dashboard_lab3.py` подключается к кластеру шардирования, выводит PRIMARY-узлы шардов и карту шардинга, а затем строит карту Folium с позициями единорогов.

## Порты

- config-сервер — 27020
- shard1 — 27021
- shard2 — 27022
- mongos — 27030

## Запуск

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python dashboard_lab3.py
```

Результат: файл `unicorns_map.html`, открыть в браузере.
