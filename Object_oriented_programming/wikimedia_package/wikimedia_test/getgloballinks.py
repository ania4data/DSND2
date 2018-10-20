from bs4 import BeautifulSoup
import urllib.request
import re
import json
from PIL import Image
import requests
from io import BytesIO
import numpy as np
from tqdm import tqdm


html_page = urllib.request.urlopen('https://commons.wikimedia.org/wiki/Commons:Quality_images/Subject/Microscopic') 
soup = BeautifulSoup(html_page, 'lxml')
images = []
data_name = {}

name_list = []
address_list_thumb = []
address_list_original = []
file_address_list = []

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
			file_address = 'https://commons.wikimedia.org/wiki/File:' + file_address.split('/')[-2]
			file_address_list.append(file_address)
			thumb_pix = '/' + file_address.split('/')[-1][0:3]       
			
			address_list_original.append(file_address.split(thumb_pix)[0].replace('/thumb',''))


json_data = json.dumps(data_name)

with open('data_name.json', 'w') as outfile:
    json.dump(json_data, outfile)

#print(file_address_list)
#print(address_list_thumb)
#print(len(address_list_thumb))

# need to return address_thumb  address_original and address file


#   get collage png, need to get author, license better in dataframe!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

random_index = list(np.random.choice(range(len(address_list_thumb)), 100))

new_img = Image.new('RGB', (600,600))


for k in tqdm(range(100)):


	image_link = address_list_thumb[random_index[k]]

	response = requests.get(image_link)
	img = Image.open(BytesIO(response.content))

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



new_img.save("photo_output.png")


#   get author name
#'https://commons.wikimedia.org/wiki/File:Daucus_carota_subsp._maximus_MHNT.BOT.2007.40.407.jpg'   #'https://commons.wikimedia.org/wiki/File:Pond_Water_Under_the_Microscope.jpg'

author_name_list = []
source_list = []
license_link_list = []
license_code_list = []

for url_test in file_address_list:


#url_test = file_address_list[0]  

	html_page = urllib.request.urlopen(url_test)


	soup = BeautifulSoup(html_page, 'lxml')


	count=0
	for img in soup.findAll('tr'):
		text=str(img.get('style'))
		if(((text == "vertical-align: top") or (text == 'valign="top"'))): #and (str(img.get('id') == "fileinfotpl_aut")
			count += 1

			td_list = img.findAll('td')

			for item in td_list:

				if(item.get('id') == "fileinfotpl_src"):

					src_name = str(td_list[1]).strip().split('>')[2][:-6]
					if('<' in src_name or (len(src_name) == 0)):
						src_name = None

				if(item.get('id') == "fileinfotpl_aut"):
					auth_name = str(td_list[1]).strip().split('>')[2][:-3]
					if('<' in auth_name or (len(auth_name) == 0)):
						auth_name = None

	print(url_test)
	print(auth_name)
	print(src_name)

	author_name_list.append(auth_name)
	source_list.append(src_name)

	for img in soup.findAll('span'):
		text=img.get('class')

		if('licensetpl' in str(text)):


			if('licensetpl_link"' in str(img)):

				license_link = str(img).split('>')[1][:-7]
				if('<' in license_link or (len(license_link) == 0)):
					license_link = None				

			if('licensetpl_short' in str(img)):

				license_code = str(img).split('>')[1][:-6]
				if('<' in license_code or (len(license_code) == 0)):
					license_code = None

	print(license_link)
	print(license_code)

	license_link_list.append(license_link)
	license_code_list.append(license_code)

print(len(author_name_list),len(source_list),len(license_link_list),len(license_code_list))	