import folium
from pymongo import MongoClient

MONGOS_URI = "mongodb://localhost:27030"
SHARD_URIS = {
    "shard1": "mongodb://localhost:27021/?directConnection=true",
    "shard2": "mongodb://localhost:27022/?directConnection=true",
}
OUTPUT_FILE = "unicorns_map.html"

# а) Подключение к маршрутизатору mongos и к реплика-сетам шардов
mongos = MongoClient(MONGOS_URI, serverSelectionTimeoutMS=5000)
shard_nodes = {name: MongoClient(uri, serverSelectionTimeoutMS=5000) for name, uri in SHARD_URIS.items()}

# б) hello — PRIMARY узел каждого реплика-сета шарда
primaries = {}
print("Реплика-сеты шардов:")
for name, client in shard_nodes.items():
    hello = client.admin.command("hello")
    primaries[name] = hello["primary"]
    print(f"  {name}: setName={hello['setName']}, PRIMARY={hello['primary']}")

# б) Карта шардинга (аналог sh.status())
print("\nШарды кластера:")
for s in mongos.admin.command("listShards")["shards"]:
    print(f"  {s['_id']}: {s['host']}")

meta = mongos.config.collections.find_one({"_id": "learn.unicorns"})
print(f"\nКлюч шардирования learn.unicorns: {meta['key']}")
print("Чанки:")
for c in mongos.config.chunks.find({"uuid": meta["uuid"]}):
    print(f"  {c['min']} -> {c['max']} на {c['shard']}")

# в) Координаты GeoJSON Point единорогов (через mongos)
unicorns = list(mongos.learn.unicorns.find({"loc": {"$exists": True}}, {"name": 1, "loc": 1}))


def find_shard(doc_id):
    for name, client in shard_nodes.items():
        if client.learn.unicorns.find_one({"_id": doc_id}, {"_id": 1}):
            return name
    return "не найден"


# г) Интерактивная карта Folium
m = folium.Map(location=[55.75, 37.62], zoom_start=11, tiles="Esri.WorldStreetMap")
for u in unicorns:
    lon, lat = u["loc"]["coordinates"]  # MongoDB хранит [lon, lat]
    shard = find_shard(u["_id"])
    popup = (f"<b>{u['name']}</b><br>"
             f"Шард: {shard}<br>"
             f"Узел реплики (PRIMARY): {primaries.get(shard)}")
    folium.Marker(
        [lat, lon],  # Folium ожидает [lat, lon] — инверсия осей
        popup=folium.Popup(popup, max_width=300),
        tooltip=u["name"],
        icon=folium.Icon(color="purple"),
    ).add_to(m)

m.save(OUTPUT_FILE)
print(f"\nКарта сохранена в {OUTPUT_FILE} ({len(unicorns)} маркеров)")