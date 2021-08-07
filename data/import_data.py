import json
import pymysql
import os

# 資料庫參數設定
db_settings = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "***",
    "db": "traveldt",
    "charset": "utf8"
}

# 建立Connection物件
conn = pymysql.connect(**db_settings)
# 建立Cursor物件
with conn.cursor() as cursor:
    command = "INSERT INTO traveldt(id, name, category, description, address, transport, mrt, latitude, longitude, images) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    with open("taipei-attractions.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    Llist = data["result"]["results"]  # 得到一個列表

    for location in Llist:
        # 篩選圖片格式
        
        list2 = []
        img = (location["file"].replace(".JPG", ".jpg")).replace(
            ".jpghttp", ".jpg__s__http").replace(
            ".pnghttp", ".png__s__http").split("__s__")
        for i in range(len(img)):
            if os.path.splitext(img[i])[1] == ".jpg" or os.path.splitext(img[i])[1] == ".png":
                # print (img[i])
                list2.append(img[i])
        list2=",".join(list2)
        # return list2
        cursor.execute(
            command, (location["_id"], location["stitle"], location["CAT2"], location["xbody"],
                      location["address"], location["info"], location["MRT"], location["latitude"], location["longitude"], list2)
        )
    conn.commit()