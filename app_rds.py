from __future__ import unicode_literals
from flask import Flask, session, redirect, request, render_template, jsonify, url_for

import mysql.connector
from mysql.connector import Error
import json
import os
import random
import requests
from dotenv import load_dotenv
load_dotenv()
import crawler as crawler
import readtool as readbility
import cutter as cutter
from flask import Flask
from flask_hashing import Hashing
import pymysql

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
RDSconn.ping(reconnect=True)
print(RDSconn.ping(reconnect=True))


#MySQL
host=os.getenv("host")
password=os.getenv("password")




app = Flask(__name__)
hashing = Hashing(app)

app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Pages


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/content")
def content():
    return render_template("content.html")

@app.route("/liked")
def liked():
    return render_template("liked.html")

@app.route("/folder/<foldername>")
def addfolder(foldername):
    return render_template("folder.html")




# 使用者相關api
@app.route("/api/user", methods=['GET'])
def user_get():

#     # 檢查使用者登入狀態
    if 'username' in session:
        user_ID = session['username']
        
    # 取出id
        RDSconn.ping()
        with RDSconn.cursor() as cursor:
            # 新增資料指令
            command = "SELECT ID FROM user WHERE ID=%s"
            # 執行指令
            cursor.execute(command, (user_ID,))
            # 取得所有資料
            id = cursor.fetchall()
        
            id = int(str(id)[2:len(id)-5])
        #         # 取出使用者姓名
            command = "SELECT username FROM user WHERE ID=%s"
            RDSconn.ping()
            cur=RDSconn.cursor()
            cur.execute(command, (user_ID,))
            name = cur.fetchall()
            name = str(name)[3:len(name)-5]

            successmessage = {
                            "data": {
                                "id": id,
                                "name": name
                            }
                            }

            return json.dumps(successmessage, ensure_ascii=False, indent=2), 200, {"Content-Type": "application/json"}
    else:
        # null 表示未登入
        failmessage = {"data": None}

        return json.dumps(failmessage, ensure_ascii=False), 500, {"Content-Type": "application/json"}

# 註冊


@app.route("/api/user", methods=['POST'])
def user_post():
    try:
        data = request.get_data()
        data = json.loads(data)
        email = data['email']
        name = data['name']
        password = data['password']
        h = hashing.hash_value(password, salt='abcd')
        password_hashed = h   
        RDSconn.ping()
        with RDSconn.cursor() as cursor:
            # 新增資料指令
            command = "SELECT username FROM user where email=%s"
            # 執行指令
            cursor.execute(command, (email,))
            # 取得所有資料
            result_count = len(cursor.fetchall())

        if result_count >= 1:
            failmessage = {
                            "error": True,
                            "message": "重複的 Email"
                            }
            return json.dumps(failmessage, ensure_ascii=False, indent=2), 400, {"Content-Type": "application/json"}
        else:
            RDSconn.ping()
            # 建立Cursor物件
            with RDSconn.cursor() as cursor:
                # 新增資料SQL語法                
                cursor.execute("INSERT INTO user (username,email,password) VALUES (%s, %s, %s)",(name, email, password_hashed))
                RDSconn.commit()
                successmessage = {
                                    "ok": True,
                                    }
                val_hash = hashing.hash_value(password, salt='abcd')
                    
                if hashing.check_value(val_hash, password, salt='abcd'):
                    RDSconn.ping()
                    with RDSconn.cursor() as cursor:
                        # 新增資料指令
                        command = "SELECT ID FROM user WHERE email=%s and password=%s"
                        # 執行指令
                        cursor.execute(command, (email, val_hash))
                        # 取得所有資料
                        result = cursor.fetchall()
                        session['username'] = result[0][0]

                        successmessage = {
                                        "ok": True
                                        }
                        return json.dumps(successmessage, ensure_ascii=False, indent=2), 200, {"Content-Type": "application/json"}
                else:
                        failmessage = {
                            "error": True,
                            "message": "帳號或密碼錯誤"
                        }

                        return json.dumps(failmessage, ensure_ascii=False, indent=2), 400, {"Content-Type": "application/json"}

                
    except:
        failmessage2 = {
            "error": True,
            "message": "伺服器內部錯誤"
        }

        return json.dumps(failmessage2, ensure_ascii=False, indent=2), 500, {"Content-Type": "application/json"}
# 登入


@app.route("/api/user/login", methods=['POST'])
def user_patch():
    try:
        data = request.get_data()
        data = json.loads(data)
        email = data['email']
        password = data['password']
        val_hash = hashing.hash_value(password, salt='abcd')
                    
        if hashing.check_value(val_hash, password, salt='abcd'):
            RDSconn.ping()
            with RDSconn.cursor() as cursor:
                # 新增資料指令
                command = "SELECT ID FROM user WHERE email=%s and password=%s"
                # 執行指令
                cursor.execute(command, (email, val_hash))
                # 取得所有資料
                result = cursor.fetchall()
                session['username'] = result[0][0]

                successmessage = {
                                "ok": True
                                }
                return json.dumps(successmessage, ensure_ascii=False, indent=2), 200, {"Content-Type": "application/json"}
        else:
                failmessage = {
                    "error": True,
                    "message": "帳號或密碼錯誤"
                }

                return json.dumps(failmessage, ensure_ascii=False, indent=2), 400, {"Content-Type": "application/json"}                
    
    except:
        failmessage = {
            "error": True,
            "message": "伺服器內部錯誤"
        }

        return json.dumps(failmessage, ensure_ascii=False, indent=2), 500, {"Content-Type": "application/json"}


# 登出
@app.route("/api/user", methods=['DELETE'])
def signout():
    # 連線到【登出功能網址】，在後端Session 中記錄使用者狀態為未登入
    session.pop('username', None)
    successmessage = {
                    "ok": True
                    }
    return json.dumps(successmessage, ensure_ascii=False, indent=2), 200, {"Content-Type": "application/json"}


@app.route("/api/addlink", methods=['POST'])
def addlink():
        if 'username' in session:
            user_ID = session['username']
            data = request.get_data()
            data = json.loads(data)
            url = data['url']
            
            detail=crawler.get_details(url)
            tilte=detail[0]
            des=detail[1]
            pic=detail[2]
            if pic=='None':
                pic='https://img.icons8.com/ios/100/000000/e-learning-2.png'
            
            RDSconn.ping()
            with RDSconn.cursor() as cursor:
                # 新增資料指令
                command = "SELECT ID FROM url where url=%s AND user_ID=%s"
                # 執行指令
                cursor.execute(command, (url,user_ID))
                # 取得所有資料
                result_count = len(cursor.fetchall())

            if result_count >= 1:
                failmessage = {
                                "error": True,
                                "message": "重複的 url"
                                }
                return json.dumps(failmessage, ensure_ascii=False, indent=2), 400, {"Content-Type": "application/json"}
            else:
                RDSconn.ping()
                cur=RDSconn.cursor()
                cur.execute("INSERT INTO url (url, title, des, pic, user_ID) VALUES (%s,%s,%s,%s,%s)",(url,tilte,des,pic,user_ID))
                RDSconn.commit()
                RDSconn.ping()
                cur=RDSconn.cursor()
                cur.execute("INSERT INTO article (url, user_ID) VALUES (%s,%s)",(url,user_ID))
                RDSconn.commit()
                successmessage = {
                                    "ok": True,
                                    }
                cutter.cutwords(url)
                return json.dumps(successmessage, ensure_ascii=False, indent=2), 200, {"Content-Type": "application/json"}

@app.route("/api/addlink", methods=['GET'])
def renderlink():
    
    if 'username' in session:
        user_ID = session['username']
        RDSconn.ping()
        with RDSconn.cursor() as cursor:
            # 新增資料指令
            command = "SELECT * FROM website.url  WHERE user_ID = %s and foldername is null;"
            # 執行指令
            cursor.execute(command, (user_ID,))
            # 取得所有資料
            content = cursor.fetchall()
        
            data = []
            for i in range(len(content)):
                body = {               
                    "url": content[i][0],
                    "title": content[i][1],
                    "des": content[i][2],
                    "pic": content[i][3],
                    "id":content[i][4],
                    "liked":content[i][7],
                },
                data.append(body)
            
            successmessage = {
                "data": data
            }
            return json.dumps(successmessage, ensure_ascii=False, indent=2), 200, {"Content-Type": "application/json"}
    else:
        failmessage = {"data": None}
        return json.dumps(failmessage, ensure_ascii=False, indent=2), 500, {"Content-Type": "application/json"}
                
@app.route("/api/addlinkdel" , methods=['POST'])
def del_article():
    if 'username' in session:
        user_ID = session['username']
        data = request.get_data()
        data = json.loads(data)
        url = data['ID']
        RDSconn.ping()
        # 建立Cursor物件
        with RDSconn.cursor() as cursor:
            # 刪除特定資料指令
            command = "DELETE FROM url WHERE url=%s AND user_ID = %s"
            # 執行指令
            cursor.execute(command, (url,user_ID))
            #儲存變更
            RDSconn.commit()
            RDSconn.ping()
            cur=RDSconn.cursor()
            # 刪除特定資料指令
            command = "DELETE FROM article WHERE url=%s AND user_ID = %s"
            # 執行指令
            cur.execute(command, (url,user_ID))
            #儲存變更
            RDSconn.commit()
            cur2=RDSconn.cursor()
            command = "DELETE FROM keyword WHERE url=%s AND user_ID = %s"
            cur2.execute(command, (url,user_ID))
            RDSconn.commit()
            successmessage = {
                            "ok": True
                            }
            return json.dumps(successmessage, ensure_ascii=False, indent=2), 200, {"Content-Type": "application/json"}


@app.route("/api/getcontent", methods=['POST'])
def sendcontent():
    urldata = request.get_data()
    urldata = json.loads(urldata)
    url = urldata['url']
    if 'username' in session:
        session['url']=url
        successmessage = {
            "nextPage": None,
            "data": "ok"
        }
        return json.dumps(successmessage, ensure_ascii=False, indent=2), 200, {"Content-Type": "application/json"}
    
@app.route("/api/getcontent", methods=['GET'])
def getcontent():
        if 'username' in session:
            url = session['url']
            detail=readbility.get_content(url)
            contentHtml=detail[0]
            title=detail[1]
                        
            data = []            
            body = {
                "title":title,              
                "content": contentHtml,
            },
            data.append(body)

            successmessage = {
                "nextPage": None,
                "data": data
            }
            return json.dumps(successmessage, ensure_ascii=False, indent=2), 200, {"Content-Type": "application/json"}
        
        
@app.route("/api/likedstat",methods=['POST'])
def likedstat():
        data = request.get_data()
        data=json.loads(data)
        articleID=data['ID']
        liked = data['liked']
        RDSconn.ping()
        # 建立Cursor物件
        with RDSconn.cursor() as cursor:
            # 修改資料SQL語法
            command ="UPDATE url SET liked = %s WHERE ID = %s;"
            # 執行指令
            cursor.execute(command, (liked,articleID))
      
            #儲存變更
            RDSconn.commit()
            successmessage={
                "ok":True
            }
            return json.dumps(successmessage,ensure_ascii=False,indent=2),200,{"Content-type":"application/json"}
            
@app.route("/api/likedstat",methods=['GET'])
def likedarticle():
        if 'username' in session:
            user_ID= session['username']
            pageind = int(request.args.get('page'))
            pagenum=0
            RDSconn.ping()
            with RDSconn.cursor() as cursor:
                # 新增資料指令
                command = "SELECT * FROM url WHERE user_ID = %s and liked = 'Y';"
                # 執行指令
                cursor.execute(command, (user_ID,))
                # 取得所有資料
                content = cursor.fetchall()
                data=[]
                for i in range(len(content)):
                    body = {               
                        "url": content[i][0],
                        "title": content[i][1],
                        "des": content[i][2],
                        "pic": content[i][3],
                        "id":content[i][4],
                    },
                    data.append(body)
                # 判斷是否是最後頁
                print("Page", pageind)
            if pageind == 26:
                successmessage = {
                    "nextPage": None,
                    "data": data
                }
                return json.dumps(successmessage, ensure_ascii=False, indent=2), 200, {"Content-Type": "application/json"}
            else:
                successmessage = {
                    "nextPage": pageind+1,
                    "data": data
                }
                return json.dumps(successmessage, ensure_ascii=False, indent=2), 200, {"Content-Type": "application/json"}   
            
@app.route("/api/folder",methods=['POST'])
def addfolderapi():
        if 'username' in session:
            user_ID= session['username']
            data = request.get_data()
            data=json.loads(data)
            foldername=data['name']
            RDSconn.ping()
            with RDSconn.cursor() as cursor:
                cursor.execute("INSERT INTO folder (foldername,user_ID) VALUES (%s,%s)",(foldername,user_ID))
                RDSconn.commit()
                successmessage={
                    "ok":True
                }
                return json.dumps(successmessage,ensure_ascii=False,indent=2),200,{"Content-type":"application/json"}     
        
@app.route("/api/getfolder",methods=['GET'])    
def getfoldername():
        if 'username' in session:
            user_ID= session['username']
            RDSconn.ping()
            with RDSconn.cursor() as cursor:
                # 新增資料指令
                command = "SELECT  DISTINCT website.folder.foldername FROM  website.folder WHERE website.folder.user_ID =  %s;"
                # 執行指令
                cursor.execute(command, (user_ID,))
                # 取得所有資料
                content = cursor.fetchall()
                data=[]
                for i in range(len(content)):
                    body = {               
                        "foldername": content[i][0]
                    },
                    data.append(body)
                successmessage={
                    "data": data
                }
                return json.dumps(successmessage, ensure_ascii=False, indent=2), 200, {"Content-Type": "application/json"}
    

@app.route("/api/addlinkbyfolder",methods=['POST'])
def addlinkbyfolder():
    if 'username' in session:
        user_ID = session['username']
        data=request.get_data()
        data=json.loads(data)
        foldername=data['foldername']
        url=data['url']
        RDSconn.ping()
        with RDSconn.cursor() as cursor:
                cursor.execute("INSERT INTO folder (foldername,user_ID,url) VALUES (%s,%s,%s)",(foldername,user_ID,url))
                RDSconn.commit()
        RDSconn.ping()
        with RDSconn.cursor() as cursor:
                # 修改資料SQL語法
                command ="UPDATE url SET foldername = %s WHERE url = %s;"
                # 執行指令
                cursor.execute(command, (foldername,url))      
                #儲存變更
                RDSconn.commit()
               
        
                successmessage={
                    "ok":True
                }
                return json.dumps(successmessage,ensure_ascii=False,indent=2),200,{"Content-type":"application/json"}     

@app.route("/api/addlinkbyfolder/<folder>",methods=['GET'])
def addlinkbyfolder_getcontent(folder):
        if 'username' in session:
            user_ID = session['username']
            pageind = 0
            # pagenum=0
            RDSconn.ping()
            with RDSconn.cursor() as cursor:
                # 新增資料指令
                command = "SELECT * FROM website.folder JOIN website.url ON website.folder.user_ID=website.url.user_ID AND website.folder.url = website.url.url WHERE  website.folder.user_ID = %s AND website.folder.foldername = %s ;"
                # 執行指令
                cursor.execute(command,(user_ID,folder))
                # 取得所有資料
                content = cursor.fetchall()            
                data = []
                for i in range(len(content)):
                    body = {               
                        "url": content[i][4],
                        "title": content[i][5],
                        "des": content[i][6],
                        "pic": content[i][7],
                        "id":content[i][8],
                        "liked":content[i][11],
                    },
                    data.append(body)
                # 判斷是否是最後頁
                print("Page", pageind)
                if pageind == 26:
                    successmessage = {
                        "nextPage": None,
                        "data": data
                    }
                    return json.dumps(successmessage, ensure_ascii=False, indent=2), 200, {"Content-Type": "application/json"}
                else:
                    successmessage = {
                        "nextPage": pageind+1,
                        "data": data
                    }
                    return json.dumps(successmessage, ensure_ascii=False, indent=2), 200, {"Content-Type": "application/json"} 
             
@app.route("/api/findoption", methods=['GET'])
def findoption():

    key = (request.args.get('srckey'))
    if 'username' in session:
        user_ID = session['username']          
        RDSconn.ping()
        with RDSconn.cursor() as cursor:
            # 新增資料指令
            command ="SELECT * FROM keyword WHERE keyword = %s AND user_ID = %s AND title is not null;"
            # 執行指令
            cursor.execute(command,(key,user_ID))
            # 取得所有資料
            content = cursor.fetchall()
            
    
            data = []
            for i in range(len(content)):
                body = {               
                    "url": content[i][5],
                    "title": content[i][4],
                },
                data.append(body)

            successmessage = {
                "data": data
            }
            return json.dumps(successmessage, ensure_ascii=False, indent=2), 200, {"Content-Type": "application/json"} 
    
@app.route("/api/renderselected",methods=['GET'])
def renderselected():
    link=request.args.get('link')
    if 'username' in session:
        user_ID = session['username']
        RDSconn.ping()
        with RDSconn.cursor() as cursor:
            # 新增資料指令
            command ="SELECT * FROM website.url  WHERE user_ID = %s AND url= %s ;"
            # 執行指令
            cursor.execute(command,(user_ID,link))
            # 取得所有資料
            content = cursor.fetchall()
        
            data = []
            for i in range(len(content)):
                body = {               
                    "url": content[i][0],
                    "title": content[i][1],
                    "des": content[i][2],
                    "pic": content[i][3],
                    "id":content[i][4],
                    "liked":content[i][7],
                },
                data.append(body)
        
            successmessage = {
                "data": data
            }
            return json.dumps(successmessage, ensure_ascii=False, indent=2), 200, {"Content-Type": "application/json"}

@app.route("/0920")
def home():
    return render_template("home.html")

app.run(host="0.0.0.0",port=3000)