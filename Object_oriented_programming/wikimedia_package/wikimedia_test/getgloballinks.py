from bs4 import BeautifulSoup
import urllib.request
import re
import json
from PIL import Image
import requests
from io import BytesIO
import numpy as np


html_page = urllib.request.urlopen('https://commons.wikimedia.org/wiki/Commons:Quality_images/Subject/Sunsets') 
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
print(len(address_list_original))

random_link = np.random.choice(address_list_thumb,100)

new_img = Image.new('RGB', (500,500))

for k, image_link in enumerate(random_link):

	response = requests.get(image_link)
	img = Image.open(BytesIO(response.content))
	img.thumbnail((50,50))
	j = int(k/10)
	i = int(k - (j*10))
	print(k)

	new_img.paste(img, (i*50,j*50))

new_img.save("hola.png")