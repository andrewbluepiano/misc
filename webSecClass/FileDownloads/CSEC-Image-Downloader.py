#Author: Andrew Afonso
from bs4 import BeautifulSoup
import csv
import socket
import ssl
import re
import threading
import time
import os

regsearch = r'[A-Z]{4}-\d{3}'
threads = []

def sendmsg(target, port, request):
    output = b''
    sockone = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockobj = ssl.wrap_socket(sockone)
    sockobj.connect((target, port))
    sockobj.send(request.encode())
    while 1==1:
        response = sockobj.recv(4096)
        if not response:
            break
        #print(response)
        output+=response
    sockobj.close()
    return output

def getimage(target, port, request, username):
    image = sendmsg(target, port, request).split(b'\r\n\r\n')[1]
    f = open(os.getcwd() + "/imagedownloads/" + username +".jpg", 'wb')
    f.write(image)
    f.close()


def main():
    if not os.path.exists("imagedownloads"):
        os.mkdir("imagedownloads")
    website=sendmsg("rit.edu", 443, "GET /computing/directory?term_node_tid_depth=4919 HTTP/1.1\r\nHost: www.rit.edu\r\n\r\n")
    soup = BeautifulSoup(website, 'html.parser')
    imageurls = soup.find_all("img", class_="card-img-top")
    imagetargetURL = imageurls[0]['data-src'][8:21]
    print(imagetargetURL)
    imagepaths = []
    for i in range(0, len(imageurls)):
        imgtarget = "GET "
        imagepath = str(imageurls[i]['data-src'][21:])
        username = str(imageurls[i]['data-src'][64:70])
        print(username)
        imgtarget += imagepath
        imgtarget += " HTTP/1.1\r\nHost: www.rit.edu\r\n\r\n"
        t = threading.Thread(target=getimage, args=(imagetargetURL, 443, imgtarget, username))
        threads.append(t)
        t.start()
#print(imgtarget)

    #print( soup.prettify())


if __name__ == "__main__":
    main()
