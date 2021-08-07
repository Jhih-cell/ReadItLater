import pymysql
# import aws_credentials as rds
import os
from dotenv import load_dotenv
load_dotenv()

password2=os.getenv("password2")
#RDS
db_settings = {
    "host" : "website.cmrrlip8wwqp.us-east-2.rds.amazonaws.com",
    "port" : 3306,
    "user" : "admin",
    "password" : password2,
    "db" : "website",
}
conn = pymysql.connect(**db_settings)
#table creation
cursor=conn.cursor()
create_table="""
CREATE TABLE url (
    url varchar(355),
    title varchar(255),
    des varchar(255),
    pic varchar(255),
    ID int NOT NULL AUTO_INCREMENT,
    email varchar(255),
    user_ID int,
    liked varchar(25),
    PRIMARY KEY (ID),
    FOREIGN KEY (user_ID) REFERENCES user(ID)
)
"""

cursor.execute(create_table)

def insert_details(name,comment):
    cur=conn.cursor()
    cur.execute("INSERT INTO Details (name,comment) VALUES(%s,%s)",(name,comment))
    conn.commit()

# def get_details():
#     cur=conn.cursor()
#     cur.execute("SELECT * FROM Details")
#     details=cur.fetchall()
#     return details
