# Author: Andrew Afonso
# Description: A script for tracking the attack progress of the simple XSS worm from attack.js
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import csv

def main():
	# For tracking the infection details
    tracking = {}
    
    # Create a session and get a cookie for the attacker account
    login = requests.post(
        'http://csec380-core.csec.rit.edu:86/login.php',
        headers={'Host': 'csec380-core.csec.rit.edu:86', 'Content-Type': 'application/x-www-form-urlencoded' },
        data={'email': 'ara1494@armbook.com', 'password': 'password'}
    )
	
	# Get the contents of the profile which the worm posts infection information to.
    timeline = requests.get('http://csec380-core.csec.rit.edu:86/timeline.php?id=119',cookies=login.cookies)

	
	# Parse the infection timeline website
    soup = BeautifulSoup(timeline.text, 'html.parser')
    soup = soup.find("div", {"id": "posts"})
    for tag in soup.select('img'):
        tag.decompose()
        
    for name, date in zip(soup.select('a'), soup.select('p') ):
        if "New friend (infection)" in date.text and name.text != "Andrew A":
            thedate = date.text.split("New friend (infection) on: ")[1].split(" GMT")[0]
            datetime_object = datetime.strptime(thedate, '%a %b %d %Y %X')
            if name.text not in tracking or tracking.get(name.text) > datetime_object:
                tracking[name.text] = datetime_object


	# Write the details of the infection to a CSV file
    with open('testfile.csv', mode='w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["User", "Infection date"])
        for key, val in tracking.items():
            writer.writerow([key, val.strftime('%x %X')])
#            writer.writerow([key, val.strftime('%b %d %Y %X')])

if __name__ == "__main__":
    main()
