import requests
from bs4 import BeautifulSoup

from datetime import datetime
import pytz
import os
import shutil

import difflib

def check_now(a,urls):
	url = urls[a]
	# Make a new folder
	os.makedirs('./contents/new/',exist_ok=True)
	# Setup old and new path
	old_file_path = "./contents/old/" + url["name"]
	new_file_path = "./contents/new/" + url["name"]
	# Fetch latest version of the site
	try:
		res_new = requests.get(url["url"], timeout=10).text
		soup_new = BeautifulSoup(res_new, 'html.parser')
	except Exception as e:
		print(e)
		return
	# Save new version to file
	with open(new_file_path, "w") as new:
		new.write(str(soup_new))
	# See if an old version is present
	try:
		old = open(old_file_path, "r")
	except:
		print("Old copy not found. Continue")
		return
	# Open the new version again for comparison
	new = open(new_file_path, "r")
	# Use difflib to find differences between old and new
	diff = difflib.unified_diff(
		old.readlines(),
		new.readlines(),
		fromfile=old_file_path,
		tofile=new_file_path,
		n=0
		)
	# If there is a difference, change status from Same to Updated
	status = "Same"
	for line in diff:
		if url['check'] in line:
			print("Content changed for: "+url["name"])
			print(line)
			status = "Updated"
			break
	
	print(
		"Status ["
		+ url["name"]
		+ "] : " 
		+ status
		)
	# Close open new file
	new.close()
	
	return status
		
	
if __name__ == "__main__":
	'''
	Code to check if a URL has updated
	'''
	
# assuming now contains a timezone aware datetime
tz = pytz.timezone('Asia/Kolkata')
now = datetime.now()
your_now = now.astimezone(tz)

# For KL
today_1 = str(your_now.strftime('%d/%m/%Y'))
print(today_1)

# For PY
today_2 = str(your_now.strftime('%d-%m-%Y'))
print(today_2)

	# Setup URLS
	urls = [
		{
			"name" : "AndamanandNicobarIslands",
			"url" : "https://dhs.andaman.gov.in",
			"check" : 'ISLANDS HEALTH BULLETIN FOR CONTAINMENT OF COVID-19'
		},
		#{
		#	"name" : "Assam" ,
		#	"url" : "https://covid19.assam.gov.in/all-districts/",
		#	"check" : ''
		#},
		{
			"name" : "Chandigarh",
			"url" : "http://chdcovid19.in/",
			"check" : '<div class="col-md-3 form-group">'
		},
		{
			"name" : "DadraandNagarHaveliandDamanandDiu",
			"url" : "https://dddcovid19.in/index",
			"check": 'ContentPlaceHolder1_lbldate'
		},
		{
			"name" : "Haryana",
			"url" : "http://www.nhmharyana.gov.in/page.aspx?id=208",
			"check" : '<a href="/WriteReadData/userfiles/file/'
		},
		{
			"name" : "Kerala",
			"url" : "http://dhs.kerala.gov.in/%E0%B4%A1%E0%B5%86%E0%B4%AF%E0%B4%BF%E0%B4%B2%E0%B4%BF-%E0%B4%AC%E0%B5%81%E0%B4%B3%E0%B5%8D%E0%B4%B3%E0%B4%B1%E0%B5%8D%E0%B4%B1%E0%B4%BF%E0%B4%A8%E0%B5%8D%E2%80%8D/",
			"check": "title=" + today_1
		},
		{
			"name" : "Puducherry",
			"url" : "https://health.py.gov.in/",
			"check": "health.py.gov.in/sites/default/files/" + today_2
		},
		{
			"name" : "Tripura",
			"url" : "https://covid19.tripura.gov.in",
			"check": 'lblActiceCases'
		},
		{
			"name" : "WestBengal",
			"url" : "https://www.wbhealth.gov.in/pages/corona/bulletin",
			"check" : 'href="https://www.wbhealth.gov.in/uploaded_files/corona/'
		},
		{
			"name" : "Gujarat",
			"url" : "https://gujcovid19.gujarat.gov.in/DrillDownCharts.aspx",
			"check" : 'ctl00_body_lblDate'
		},
		{
			"name" : "AndraPradesh",
			"url" : "http://covid19.ap.gov.in/Covid19_Admin/index.html",
			"check" : 'id="ActiveCases"'
		}
	]
	#Setup BOT TOKEN and CHAT ID from environment variable
	MONITOR_BOT_TOKEN = os.environ['MONITOR_BOT_TOKEN']
	CHAT_ID = os.environ['DATA_OPS_CHAT_ID']


	for a in range(len(urls)):
		status = check_now(a,urls)
		if status == "Updated":
				message_call = (
					"https://api.telegram.org/bot"
					+ MONITOR_BOT_TOKEN
					+ "/sendMessage?chat_id="
					+ CHAT_ID
					+ "&text="
					+ urls[a]['name']
					+ " site got updated!\n\n"
					+ "URL: "
					+ urls[a]['url']
					)
				requests.get(message_call)
	# Make the new contents as old
	try:
		shutil.rmtree('./contents/old/')
	except FileNotFoundError:
		pass
	os.rename('./contents/new/','./contents/old/')
