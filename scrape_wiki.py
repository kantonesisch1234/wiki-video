import wikipediaapi
import wikitextparser as wtp
import requests
import urllib.parse
from opencc import OpenCC
import json
from text_preprocessing import *

wiki = wikipediaapi.Wikipedia('zh')

def s2t(text):
    cc = OpenCC('s2t')
    return cc.convert(text)

def get_sections_data(title):
    page = wiki.page(title)
    results = get_image_data(title)
    sections = [{'title':None, 'level':0, 'content':page.summary, 'main_image_url':get_wiki_main_image(title)}]
    for section in page.sections:
        sections.append({'title':section.title, 'level':1,'content':section.text})
        for subsection in section.sections:
            sections.append({'title':subsection.title, 'level':2,'content':subsection.text})
            for subsubsection in subsection.sections:
                sections.append({'title':subsubsection.title,'level':3,'content':subsubsection.text})
    
    
    if len(sections) == len(results):
        for idx,result in enumerate(results):
            sections[idx]['images'] = result['images']
    elif len(sections) != len(results):
        result_titles = [clean_str(result['title']) for result in results]
        for section in sections:
            try:
                idx = result_titles.index(clean_str(section['title']))
            except:
                continue
            section['images'] = results[idx]['images']
    return sections
        
#     return remove_repeated_img_from_sections(sections)

def clean_str(string):
    if not string:
        return string
    else:
        return s2t(string.strip())

def get_image_data(title):
    r = requests.get(
        'https://zh.wikipedia.org/w/api.php',
        params={
            'action': 'parse',
            'page': wiki.page(title).displaytitle,
            'contentmodel': 'wikitext',
            'prop': 'wikitext',
            'format': 'json'
        }
    )

    data = wtp.parse(r.json()['parse']['wikitext']['*'])
    results = []
    for section in data.sections:
    #     print(f"section title: {section.title}")
        images = [
            {   "metadata": t.text.split("|"),
                "title": t.title[5:],
                "api_url": f"https://zh.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote_plus(t.title)}&prop=imageinfo&iiprop=url&format=json"
            }
            for t in wtp.parse(section.contents).wikilinks
            if t.title.startswith("File")
        ]
#         print(section.title)

        for image in images:
            number = list(requests.get(image["api_url"]).json()['query']['pages'].keys())[0]
            image["url"] = requests.get(image["api_url"]).json()[
                "query"]["pages"][number]["imageinfo"][0]["url"]
#             print(requests.get(image["api_url"]).json())
        results.append({
            "title": section.title,
            "images": images
        })
    
    return results

def get_wiki_main_image(title):
    url = 'https://zh.wikipedia.org/w/api.php'
    data = {
        'action' :'query',
        'format' : 'json',
        'formatversion' : 2,
        'prop' : 'pageimages|pageterms',
        'piprop' : 'original',
        'titles' : wiki.page(title).displaytitle
    }
    try:
        response = requests.get(url, data)
        json_data = json.loads(response.text)
        return json_data['query']['pages'][0]['original']['source'] if len(json_data['query']['pages']) >0 else 'Not found'
    except:
        return None
    
def remove_repeated_img_from_sections(sections):
    sections_copy = sections.copy()
    for idx1,section in enumerate(sections_copy):
        try:
            if section['level'] == 1:
                images_list = section['images']
                for idx2,section2 in enumerate(sections_copy):
                    if idx2 > idx1 and section2['level'] > 1:
                        images_list = [x for x in images_list if x not in section2['images']]
                    if section2['level'] == 1:
                        sections_copy[idx1]['images'] = images_list
                        break
        except Exception as e:
            print("Some errors occured for removing repeated images.")
            print(e)
    for idx1,section in enumerate(sections_copy):
        try:
            if section['level'] == 2:
                images_list = section['images']
                for idx2,section2 in enumerate(sections_copy):
                    if idx2 > idx1 and section2['level'] > 2:
                        images_list = [x for x in images_list if x not in section2['images']]
                    if section2['level'] == 2:
                        sections_copy[idx1]['images'] = images_list
                        break
        except Exception as e:
            print("Some errors occured for removing repeated images.")
            print(e)
    return sections_copy

def find_parent_section(sections, section_title):
    section_titles = [section['title'] for section in sections]
    section_levels = [section['level'] for section in sections]
    idx = section_titles.index(section_title)
    level = sections[idx]['level']
    for idx2 in range(idx,0,-1):
        if section_levels[idx2] < level:
            return sections[idx2]['title']
    return 'summary'
    