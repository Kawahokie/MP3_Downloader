import os
import requests
from time import time as timer
from multiprocessing.pool import ThreadPool
from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath
import lxml.html

import tkinter as tk
from tkinter import *

# book_url = 'https://ipaudio.club/wp-content/uploads/GOLN/Ready%20Player%20One/01.mp3'
# base_url = 'https://dailyaudiobooks.com/agatha-christie-and-then-there-were-none-audiobook/'

root = Tk()
root.geometry("400x610")
root.title(" Audiobook Downloader ")

def getBookURL(url):
    url = url.replace("\n", "")
    url = url.replace(" ", "")
    url.rstrip('/')
    r = requests.get(url)
    tree = lxml.html.fromstring(r.text)
    for link in tree.findall(".//a"):
        url123 = link.get("href")
        if url123.endswith(".mp3"):
            break
    return(url123)

def getAB_BookURL(url):
    url = url.replace("\n", "")
    url = url.replace(" ", "")
    url.rstrip('/')
    urlList = []
    r = requests.get(url)
    for line in r.text.splitlines():
        if line.find('"chapter_link_dropbox": "') != -1:
            urlList.append("".join("https://files.audiobookss.com/audio/"+line[45:-2]))
    urlList.pop(0)
    
    val = urlList[0]
    num_Titles = len(urlList)
    book_Name = val[36:(val.find("\\"))] # Get book title from URL
    book_Name = book_Name.replace(" ","_")
    book_Name = book_Name.replace("-","_")

    urlCount = 0
    for val in urlList:
        while(val.find('\\') != -1):
            val = val[:val.find('\\')]+val[val.find('\\')+1:]   
        urlList[urlCount]=val
        urlCount += 1

    for count in range(1, num_Titles+1):
        filename="".join([str(count),"_",book_Name,".mp3"])
        urls.append([filename,urlList[count-1]])
    return (num_Titles)   

def url_checker(url):
	try:
		#Get Url
		get = requests.get(url, stream=True)
		# if the request succeeds 
		if get.status_code == 200:
			return(True)
		else:
			return(False)
	#Exception
	except requests.exceptions.RequestException as e:
        # print URL with Errs
		raise SystemExit(False)

def parse_url(url_to_get):
    global book_Name
    global leading_Zero
    global base_url
    title_num = PurePosixPath(unquote(urlparse(url_to_get).path)).parts[-1]
    if title_num[0] == "0":
        leading_Zero = True
    else:
        leading_Zero = False

    book_Name = PurePosixPath(unquote(urlparse(url_to_get).path)).parts[-2]
    book_Name = book_Name.replace(" ","_")

    base_url = url_to_get.split('/')
    base_url.pop()
    base_url = '/'.join(base_url)
    return base_url

def fetch_url(entry):
    path, uri = entry
    if not os.path.exists(path):
        r = requests.get(uri, stream=True)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
    return path

def build_url_list():
    for count in range(1, num_Titles+1):
        if(count<10 and leading_Zero):
            filename="".join([str(count),"_",book_Name,".mp3"]) 
            url_dl = "".join([base_url,"/","0",str(count),".mp3"])
        else:
            filename="".join([str(count),"_",book_Name,".mp3"])
            url_dl = "".join([base_url,"/",str(count),".mp3"])
        urls.append([filename,url_dl])
    return

def buildAB_url_list(urlList):
    val = urlList[0]
    book_Name = val[36:(val.find("\\"))] # Get book title from URL
    book_Name = book_Name.replace(" ","_")
    book_Name = book_Name.replace("-","_")

    for count in range(1, num_Titles+1):
        filename="".join([str(count),"_",book_Name,".mp3"])
        urls.append([filename,urlList[count-1]])
    return

def do_stuff(base_url):
    global urls
    global num_Titles
    global good_URL
    global AB_Books

    if base_url.find("audiobookss.com") != -1:
        AB_Books = True
        urls = []
        start = timer()
        num_Titles = getAB_BookURL(base_url)
        
        # buildAB_url_list(urlList) # Create Name / URL list

        print(f"Time to scan links: {timer() - start}")
        print("Links found: "+str(num_Titles)+" - Starting download.")
        Output.insert(END, f"Time to scan links: {timer() - start}" + '\n')
        Output.update()
        Output.insert(END, "Links found: "+str(num_Titles)+"\n...Starting download..." + '\n\n')
        Output.update()
    else:
        book_url = getBookURL(base_url)
        AB_Books = False
        base_url = parse_url(book_url)
        good_URL = True
        urls = []
        num_Titles = 1

        start = timer()
        while(good_URL):
            url_dl = ""
            if(num_Titles<10 and leading_Zero):
                url_dl = "".join([base_url,"/","0",str(num_Titles),".mp3"])
            else:
                url_dl = "".join([base_url,"/",str(num_Titles),".mp3"])
            
            good_URL = url_checker(url_dl)
            if good_URL:
                num_Titles += 1
        num_Titles -= 1
        print(f"Time to scan links: {timer() - start}")
        print("Links found: "+str(num_Titles)+" - Starting download.")
        Output.insert(END, f"Time to scan links: {timer() - start}" + '\n')
        Output.update()
        Output.insert(END, "Links found: "+str(num_Titles)+"\n...Starting download..." + '\n\n')
        Output.update()
        build_url_list() # Create Name / URL list

    start = timer()
    results = ThreadPool(8).imap_unordered(fetch_url, urls)
    dl_Count = 0
    for path in results:
        dl_Count += 1
        print(str(dl_Count) +"/" + str(num_Titles) + " - " + path)
        Output.insert(END, str(dl_Count) +"/" + str(num_Titles) + " - " + path + '\n')
        Output.update()
    Output.insert(END, f"Time to download files: {timer() - start}" + '\n\n')
    Output.insert(END, "Done!" + '\n\n')
    print(f"Time to download files: {timer() - start}")

def Close():
    root.destroy()
 
def Take_input():
    INPUT = inputtxt.get("1.0", "end-1c")
    do_stuff(INPUT)
     
lab1 = Label(text = "Valid sites\nhttps://dailyaudiobooks.com/\nhttps://goldenaudiobooks.com/\nhttps://audiobookss.com/")
lab2 = Label(text = "Enter URL: ")
inputtxt = Text(root, height = 3,
                width = 45,
                bg = "light yellow")
 
Output = Text(root, height = 23,
              width = 45,
              bg = "light cyan")
 
Display = Button(root, height = 2,
                 width = 20,
                 text ="Download",
                 command = lambda:Take_input())
                 
Exit = Button(root, height = 2,
                 width = 20,
                 text ="Exit",
                 command = lambda:Close())
 
lab1.pack()
lab2.pack()
inputtxt.pack()
Display.pack()
Exit.pack()
Output.pack()
 
mainloop()

#######################################
# # Old Method
# import requests
# from http import client

# urlSession = requests.Session()
# base_url = "https://ipaudio5.com/wp-content/uploads/STARR/star/Allegiant/"
# book_Name = "Allegiant"
# leading_Zero = False
# num_Titles = 9

# for count in range(1, num_Titles+1):
#     if(count<10 and leading_Zero):
#         url = "".join([base_url,"0",str(count),".mp3"])
#     else:
#         url = "".join([base_url,str(count),".mp3"])
#     print("Requesting ", url)
#     response = urlSession.get(url)
#     print(response.status_code)
#     filename="".join([str(count),"_",book_Name,".mp3"])
#     with open(filename, 'wb') as f:
#         f.write(response.content)
