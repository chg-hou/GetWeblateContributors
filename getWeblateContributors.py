import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from tqdm import tqdm
lang_counter = defaultdict(lambda: defaultdict(lambda: 0)) 
namedict = {}
langdict = {}

project_name = 'dawnlightsearch'
url_mask = "https://hosted.weblate.org/changes/?component=translations&project=" + project_name + "&page=%d"
user_url_excluded = ['/user/chg-hou/']


for page in tqdm(range(1,5000)):
    # page = 1
#     print(page)
    url = url_mask % page

    content = requests.get(url).content.decode('utf8')
    if 'The page you are looking for was not found' in content:
        break
    soup = BeautifulSoup(content, 'html.parser')


    row_list = []
    for class_ in ["stripe-odd","stripe-even"]:
        row_list.extend(soup.find_all("tr",class_=class_))

    for row in row_list:
        tds = row.find_all('td')
        '''
        <td> <span title="2019-09-23T16:41:34+00:00">3 days ago</span></td>,
        <td><a href="/user/Estebastien/" title="Estébastien Robespi"><img class="avatar" src="/avatar/32/Estebastien.png"/> Estebastien</a></td>,
        <td><a href="/translate/dawnlightsearch/translations/fr/?checksum=3e4f5e2ba2fc88d5">New translation</a></td>,
        <td></td>,
        <td><a href="/projects/dawnlightsearch/translations/fr/">DawnlightSearch/Translations - French</a></td>,
        '''
        if len(tds) <=2:
            continue
        try:
            tds[1].a.text
        except:
            continue
#         print(tds[1])
        nickname = tds[1].a.text
        fullname = tds[1].a['title']
        nameurl = tds[1].a['href']
        langname = tds[4].a.text
        langurl = tds[4].a['href']   

        lang = [a for a in langurl.split('/') if a][-1]
        if not nameurl in namedict:
            namedict[nameurl] = [nickname,fullname]
        if not langurl in langdict:
            if '-' in langname:
                langname = langname.split('-')[1].strip()
                langdict[langurl] = [lang, langname]
            else:
                continue            
        lang_counter[langurl][nameurl] += 1
        
        
markdown_text = '|Language|Contributors|\n|-|-|\n'

langkeys = sorted(lang_counter.keys())
for key in langkeys:    
    values = lang_counter[key]
    l = [(a,values[a]) for a in values if a not in user_url_excluded]
    l.sort(key=lambda x: x[1],reverse=True)
    
    langurl = key
    
    if not l:
        continue
    
    lang, langname =  langdict[langurl]               
    markdown_text += f'|{langname} ({lang}) |'
    
    names_list = []
    for nameurl,count in l:
        nickname,fullname = namedict[nameurl]
        names_list.append(f'[{fullname} ({nickname})](https://hosted.weblate.org{nameurl})')
    
    markdown_text += '<br>'.join(names_list) + '|\n'
    
print(markdown_text)
