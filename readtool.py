import requests
from readability import Document

def get_content(url):
    response = requests.get(url)
    response.encoding = "utf-8"
    doc = Document(response.text)
    
# print(doc.title())
# 'Example Domain'
    title=doc.title()
    summary=doc.summary()
    content=[title,summary]
    print(content)
    return content
# """<html><body><div><body id="readabilityBody">\n<div>\n    <h1>Example Domain</h1>\n
# <p>This domain is established to be used for illustrative examples in documents. You may
# use this\n    domain in examples without prior coordination or asking for permission.</p>
# \n    <p><a href="http://www.iana.org/domains/example">More information...</a></p>\n</div>
# \n</body>\n</div></body></html>"""
