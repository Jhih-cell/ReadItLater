# import urllib.request as req
# url="https://zi.media/@yidianzixun/post/JB8jYk"
# request=req.Request(url, headers={
#     "User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36"
# })
# with req.urlopen(request) as response:
#     data=response.read().decode("utf-8")
# import bs4
# root = bs4.BeautifulSoup(data,"html.parser")
# print(root.p.string)
from urllib.request import urlopen
import requests
import re
from bs4 import BeautifulSoup


def get_details(url):
    try:
        response = requests.get(url)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find_all("title", limit=1)==[]:
            title="Notitle"
        else:
            title = soup.find_all("title", limit=1)
            title = str(title[0].string)
        
        #des
        if str(soup.find(attrs= {"property":"og:description"})) == "None" :
            if soup.find(attrs= {"name":"description"}) == None:
                if soup.find("main")==None:
                    des=str(soup.find("p"))
                else:
                    des=str(soup.find("main").select("p")[0])
            else:
                des =  str(soup.find(attrs= {"name":"description"})['content'])

        else:
            des =  str(soup.find(attrs= {"property":"og:description"})['content'])
            print("og")
        #pic article
        if soup.find(attrs= {"property":"og:image"}) ==None:
            
            # pic = soup.find("img")['src']            
            pic = soup.find("img", {"src": re.compile('.ico$')})
            print(pic)
            
        else:
            pic = str(soup.find(attrs= {"property":"og:image"})['content'])
            
        
        
        pic=str(pic)
        
        content = [title,des,pic]
        # print(content)
        return content
    except IndexError:
        pass

def get_content(url):
#     # 送出網址, 這次我送出的是網址列的網址, 回應則是一個網頁的形式
#     response = urlopen("https://tabelog.com/tw/tokyo/rstLst/?SrtT=rt")
# #     # 把回應丟到解析器
#     html = BeautifulSoup(response)
#     # 你可以把它印出來, 不過由於篇幅關係, 我就不把得到的網頁印出了
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    
    return soup.body.prettify()

