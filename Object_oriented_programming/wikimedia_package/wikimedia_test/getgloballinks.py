from bs4 import BeautifulSoup
import urllib.request
import re
import json


html_page = urllib.request.urlopen('https://commons.wikimedia.org/wiki/Commons:Quality_images/Subject/Microscopic') 
soup = BeautifulSoup(html_page, 'lxml')
images = []
data_name = {}

name_list = []
address_list_thumb = []
address_list_original = []


count = 0
for a_ in soup.findAll('a'):
	tmp = a_.get('href')

	if('/wiki/File:' in str(tmp)):
		

		href = tmp


		for link in a_.findAll('img'):

			count += 1

			file_name = (link.get('alt'))
			file_address = (link.get('src'))

			data_name[file_name] = file_address

			name_list.append(file_name)
			address_list_thumb.append(file_address)
			thumb_pix = '/' + file_address.split('/')[-1][0:3]

			#print(thumb_pix)
            
			
			address_list_original.append(file_address.split(thumb_pix)[0].replace('/thumb',''))


json_data = json.dumps(data_name)

with open('data_name.json', 'w') as outfile:
    json.dump(json_data, outfile)

#print(name_list)
print(address_list_original)
