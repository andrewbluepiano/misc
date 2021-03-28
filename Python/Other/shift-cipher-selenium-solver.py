# Author: Andrew Afonso
# Description: Program to solve a CTF question for a web based CTF. 
# Description: Correctly consecucitively solves shift ciphers provided on a web page, then enters the plaintext. 
###
# Requirements:
# selenium
# nltk
# numpy
from selenium import webdriver
from selenium.webdriver.common.touch_actions import TouchActions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from nltk.corpus import words
import time
import sys
import string
from numpy import *
import re

alphabet = "abcdefghijklmnopqrstuvwxyz"
regex = re.compile('[^a-z\s]')
myid = ""
browser = webdriver.Chrome(executable_path=r"C:\Users\Andrew Afonso\AppData\Local\Programs\chromedriver.exe")
browser.get('')

time.sleep(1)
button1 = browser.find_element_by_xpath("/html/body/site-nav/div/nav/div/div/ul/li[2]/div/div/button")
button1.click()
time.sleep(2)
login_form = browser.find_element_by_xpath("/html/body/site-help-modal/div/div/div/div[2]/resume-session-form/div/input")
login_form.send_keys(myid)
button2 = browser.find_element_by_xpath("/html/body/site-help-modal/div/div/div/div[2]/resume-session-form/button")
button2.click()
time.sleep(2)

therow = browser.find_element_by_xpath("//*[@id='hackerchallenge-challenge-list']/div[2]/div")
box = browser.find_element_by_xpath("//*[@id='hackerchallenge-challenge-list']/div[2]/div/challenge-card[4]/div/div")
action = ActionChains(browser)
touchactions = TouchActions(browser)
action.move_to_element(therow).perform()
action.move_to_element(box).perform()
time.sleep(1)
touchactions.tap(box)
button3 = browser.find_element_by_xpath("//*[@id='hackerchallenge-challenge-list']/div[2]/div/challenge-card[4]/div/div/div/div[2]/div/button")
button3.click()
time.sleep(1)

count = 0

def issolved(maybethis):
    count = 0
    maybethis = regex.sub('', maybethis)
    thewords = maybethis.split(" ")
    thewords.sort(key=len) 
    thewords.reverse()
    top = 5
    if len(thewords) < 5:
        top = len(thewords)
    for x in range(0,top):
        if thewords[x] in words.words():
            count += 1
        elif len(thewords[x]) > 5 and thewords[x][len(thewords[x])-2:] == "ed":
            if thewords[x][:len(thewords[x])-2] in words.words():
                count += 1
        elif len(thewords[x]) > 5 and thewords[x][len(thewords[x])-3:] == "ing":
            if thewords[x][:len(thewords[x])-3] in words.words():
                count += 1
        elif len(thewords[x]) > 3 and thewords[x][len(thewords[x])-1] == "s":
            if thewords[x][:len(thewords[x])-1] in words.words():
                count += 1
    if count > 1:
        return True
    else:
        return False

def getTranslatedMessage(message, key):
    # if mode[0] == 'd':
        # key = -key
    translated = ''

    for symbol in message:
        if symbol in alphabet:
            num = ord(symbol)-96
            num = ((num - key) % 26) + 96
            translated += chr(num)
        else:
            translated += symbol
    return translated
    
oldhold = ""

while count<50:
    ciphtext = browser.execute_script("return SuperRot_getEncryptedMessage();")
    if ciphtext == oldhold:
        while ciphtext == oldhold:
            ciphtext = browser.execute_script("return SuperRot_getEncryptedMessage();")
    oldhold = ciphtext
    ans = ""
    letters = dict.fromkeys(string.ascii_lowercase, 0)
    print(ciphtext)  
    ticker = 0
    solved=0
    top = ""
    middle = ""
    bottom = ""
    for letter in letters:
        countlocal = ciphtext.count(letter)
        letters[letter] = countlocal
        if ticker == 0:
            top = letter
            middle = letter
            bottom = letter
            ticker = 1
        elif countlocal >= letters.get(top):
            bottom = middle
            middle = top
            top = letter
        elif countlocal >= letters.get(middle):
            bottom = middle
            middle = letter
        elif countlocal >= letters.get(bottom):
            bottom = letter
    
    shifts = [(ord(top)-ord('e')) % 26, (ord(top)-ord('a')) % 26, (ord(top)-ord('t')) % 26, (ord(top)-ord('o')) % 26, (ord(top)-ord('i')) % 26,  (ord(middle)-ord('e')) % 26, (ord(bottom)-ord('e')) % 26, (ord(middle)-ord('o')) % 26, (ord(bottom)-ord('o')) % 26, (ord(middle)-ord('i')) % 26, (ord(bottom)-ord('i')) % 26, (ord(middle)-ord('a')) % 26, (ord(bottom)-ord('a')) % 26, (ord(middle)-ord('t')) % 26, (ord(bottom)-ord('t')) % 26]
    
    #print("mid let: " + middle)
    #print("Shift one: " + str(shifttwo))
    for tester in shifts:
        solution = getTranslatedMessage(ciphtext, tester)
        if issolved(solution):
            print("Found It: " + solution)
            print(browser.execute_script("return SuperRot_submit(arguments[0]);", solution))
            count+=1
            break
