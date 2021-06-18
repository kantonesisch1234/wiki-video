import requests
from bs4 import BeautifulSoup
import json
import os
import sys
        
def download_image_from_word(word,directory,attempts=10):
    url = "https://images.search.yahoo.com/search/images?p=" + word

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    div_list = soup.find("div", class_="sres-cntr").find_all("li")
    img_links_length = min(attempts, len(div_list))
    img_links = [json.loads(div_list[i]['data'])['iurl'] for i in range(img_links_length)][:img_links_length]

    for idx,img_link in enumerate(img_links):
        try:
            response = requests.get(img_link)
            img_file_type = '.jpg'
            file = open(os.path.join(directory, 'main_image' + img_file_type), "wb")
            file.write(response.content)
            file.close()
            print("Image downloading for " + word + " successful at " + str(idx+1) +". attempt.")
            break
            
        except Exception as e:
            print(e)
            print("Error downloading image for " + word +" at " + str(idx+1) + "attempt.")
  