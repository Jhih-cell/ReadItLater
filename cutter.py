import jieba
import pymysql
import os
from dotenv import load_dotenv
load_dotenv()
import mysql.connector
from flask import session
import pymysql

host=os.getenv("host")
password=os.getenv("password")

#MySQL
# mydb = mysql.connector.connect(
#     host=host,
#     user="root",
#     password=password,
#     database="website",
#     charset="utf8"
# )

#RDS
password2=os.getenv("password2")

db_settings = {
    "host" : "website.cmrrlip8wwqp.us-east-2.rds.amazonaws.com",
    "port" : 3306,
    "user" : "admin",
    "password" : password2,
    "db" : "website",
}
RDSconn = pymysql.connect(**db_settings)

def cutwords(url):
    if 'username' in session:
        user_ID = session['username']
        documents = []
        
        #把 title 找出來
        with RDSconn.cursor() as cursor:
            # 新增資料指令
            command = "SELECT title FROM url where url =%s"
            # 執行指令
            cursor.execute(command, (url,))
            # 取得所有資料
            result = cursor.fetchall()
            
            title = "".join(result[0])
        
            documents.append(("".join(result[0])).replace(' ',''))
            # print(documents)

        
            # 新增資料指令
            command = "SELECT url FROM keyword where url =%s AND user_ID =%s"
            # 執行指令
            cursor.execute(command, (url,user_ID))
            # 取得所有資料
            result1 = cursor.fetchall()
            
            if len(result1)<1:

                # 把分詞 keyword 找出來
                for sentence in documents:
                    title_list = jieba.lcut(sentence)
                    # print(title_list[2])
                    cutwords = title_list
                for i in cutwords:
                    
                    cursor.execute("INSERT INTO keyword (keyword,user_ID,title,url) VALUES (%s,%s,%s,%s);",(i,user_ID,title,url))
                    RDSconn.commit()
            
            
            

        


        
