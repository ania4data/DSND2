from bs4 import BeautifulSoup
import urllib.request
import re
import json
from PIL import Image
import requests
from io import BytesIO
import numpy as np
from tqdm import tqdm


html_page = urllib.request.urlopen('https://commons.wikimedia.org/wiki/Commons:Quality_images/Technical/Exposure') 
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
print(address_list_thumb)
print(len(address_list_thumb))

#random_link = np.random.choice(address_list_thumb,100)
random_index = list(np.random.choice(range(len(address_list_thumb)), 100))

#random_link = address_list_thumb[random_index[:]]


new_img = Image.new('RGB', (600,600))


for k in tqdm(range(100)):

	#print('here')
	image_link = address_list_thumb[random_index[k]]
	#print(image_link)
	#print('here')
	response = requests.get(image_link)
	img = Image.open(BytesIO(response.content))
	#print(img.width,img.height)

	ratio=img.width/img.height

	if(ratio<1.0):
		new_height=int(60/ratio)
		img_resize=img.resize((60,new_height))
	else:
		new_width=int(60*ratio)
		img_resize=img.resize((new_width,60))

	#img_resize.save('{}.png'.format(k))
	center_y=int(img_resize.width/2.)
	center_x=int(img_resize.height/2.)


	upper = center_y- 30   # PIL  real x,is not actually along width, width->y   height->x
	left = center_x - 30
	lower = center_y + 30
	right = center_x + 30


	img_resize_crop=img_resize.crop((upper,left,lower,right))


	#img_resize_crop.thumbnail((60,60), Image.ANTIALIAS)
	j = int(k/10)
	i = int(k - (j*10))
	#print(k)

	new_img.paste(img_resize_crop, (i*60,j*60))

	#k += 1
	# if(k%10 == 0):
	# 	print('{}/100'.format(k))

new_img.save("hola.png")