import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama
import json
import time
import urllib3
import re
import datefinder
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
import lxml.html
import validators
nlp = en_core_web_sm.load()
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Index
import uuid
import os
import datetime
import pycountry
#-----------------------------------------------------------------------------------------------------------------------
# init the colorama module
colorama.init()
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW
# initialize the set of links (unique links)
internal_urls = set()
external_urls = set()
permitted_urls=set()
urllib3.disable_warnings()
#-----------------------------------------------------------------------------------------------------------------------
# number of urls visited so far will be stored here
max_urls=999999
test=False
config={}
headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent':  'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Cookie': 'PHPSESSID=r2t5uvjq435r4q7ib3vtdjq120',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Keep-Alive': '300',
    'Accept-Language': 'en-us,en;q=0.5',
    'Accept-Encoding': 'gzip,deflate',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'Server': 'Apache/2'

}
#-----------------------------------------------------------------------------------------------------------------------
def openCrawlerConfig(webSiteEntity):
    crawlerConfig = open('crawlerDatasetConfig.json',"r")
    crawlerConfig = json.loads(r''+crawlerConfig.read())
    NewConfig={
        "permitted_urls_rules":crawlerConfig[webSiteEntity]['permitted_urls_rules'],
        "denied_urls_rules":crawlerConfig[webSiteEntity]['denied_urls_rules'],
        "keep_parameters":crawlerConfig[webSiteEntity]['keep_parameters'],
        "page_counter": crawlerConfig[webSiteEntity]['page_counter'],
        "features":crawlerConfig[webSiteEntity]['features'],
        "seed":crawlerConfig[webSiteEntity]['seed'],
        "decision_model":crawlerConfig[webSiteEntity]['decision_model'],
        "equal_crawled_features": crawlerConfig[webSiteEntity]['equal_crawled_features'],
        "allArray": crawlerConfig[webSiteEntity]['allArray']
    }
    print("The new configurations have been set!")
    return NewConfig
#-----------------------------------------------------------------------------------------------------------------------
def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)
#-----------------------------------------------------------------------------------------------------------------------
def removeURLparameters(url):
    parsed_href = urlparse(url)
    # remove URL GET parameters, URL fragments, etc.
    url = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
    return url
#-----------------------------------------------------------------------------------------------------------------------
def get_all_website_links(url):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    urls = set()
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    soup=""
    cnt=0
    while soup=='':
        try:
            soup = BeautifulSoup(requests.get(url,verify=True, timeout=5, headers=headers).content, "html.parser",from_encoding="iso-8859-1")
            break
        except:
            print("Connection refused by the server...")
            time.sleep(0.2)
            cnt=cnt+1

            if cnt==20:
                return urls
            continue
    cnt=0

    for a_tag in soup.findAll("a"):

        href = a_tag.attrs.get("href")

        if href == "" or href is None:
            # href empty tag
            continue

        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        if config["keep_parameters"]=="False":
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

        if not is_valid(href):
            # not a valid URL
            continue

        if domain_name not in href:
            continue

        if href in internal_urls:
            # already in the set
            continue

        accessPermitted=True
        for condition in config["denied_urls_rules"]:
            if (len(re.findall(condition, href))>0):
                accessPermitted=False
                break

        if(not accessPermitted):
            continue

        urls.add(href)
        internal_urls.add(href)

        for condition in config["permitted_urls_rules"]:
            if (len(re.findall(condition, href))>0) and href not in permitted_urls:
                permitted_urls.add(href)
                print(f"{GREEN}[{len(permitted_urls)}] Permitted link: {href}{RESET}")
                indexWebpage(href)
    return urls
#-----------------------------------------------------------------------------------------------------------------------
def extractHTML(url):
    soup=""
    cnt=0
    while soup=='':
        try:
            soup = BeautifulSoup(requests.get(url,verify=True, timeout=5, headers=headers).content, "html.parser",from_encoding="iso-8859-1")
            break
        except:
            print("Connection refused by the server...")
            time.sleep(0.2)
            cnt=cnt+1

            if cnt==20:
                break
            continue
    if len(soup)>0 and len(soup.find_all('body'))>0:
        return soup
    else:
        return ""
#-----------------------------------------------------------------------------------------------------------------------
def extractTitle(html):
    lstTitle=[]
    for title in html.find_all('title'):
        lstTitle.append(title.get_text())
    return lstTitle
#-----------------------------------------------------------------------------------------------------------------------
def indexWebsite(website):
    global max_urls
    global config

    config=openCrawlerConfig(website)
    url=config["seed"]

    permitted_urls.clear()
    internal_urls.clear()
    external_urls.clear()
    total_urls_visited=0

    uniquelinks=set()
    uniquelinks.add(url)

    page_cnt=1
    for page_counter in config["page_counter"]:
        page_cnt=1
        while uniquelinks:
            url = page_counter.replace("{counter}", str(page_cnt))
            uniquelinks = get_all_website_links(url)
            page_cnt=page_cnt+1
            total_urls_visited += 1

    if page_cnt>1:
        printResults()
        return

    while total_urls_visited < max_urls and uniquelinks:
        url=uniquelinks.pop()
        total_urls_visited += 1
        print(f"{YELLOW}[*] Crawling: {url}{RESET}")
        links = get_all_website_links(url)
        for link in links:
            uniquelinks.add(link)

    printResults()
#-----------------------------------------------------------------------------------------------------------------------
def printResults():
    print("[+]  Total Internal links: ", len(internal_urls))
    print("[+]  Total External links: ", len(external_urls))
    print("[+] Total Permitted links: ", len(permitted_urls))
    print("[+]            Total URLs: ", len(external_urls) + len(internal_urls))
    print("[+]  Maximum Crawled URLs: ", max_urls)
#-----------------------------------------------------------------------------------------------------------------------
def strippedText(text):
    if type(text)!=None and type(text)==str:
        text=text.replace('\n',' ')
        text=text.replace('\r','')
        text=text.replace('\t','')
        text=text.replace('  ','')
        text=text.replace('..','.')
    return text
#-----------------------------------------------------------------------------------------------------------------------
def remove_tags(raw_html):
    text=""
    if(type(raw_html)!= type(None)):
        text= BeautifulSoup(raw_html, "lxml").text
        text= "\n".join([s for s in text.split("\n") if s])
    return text
#-----------------------------------------------------------------------------------------------------------------------
def filterByDatatype(value,datatype,expectedValues):
    if datatype=="currency" or datatype=="int" or datatype=="decimal":
        trim = re.compile(r'[^\d.,]+')
        lstvalue=value.split()
        for val in lstvalue:
            value = trim.sub('', val)
            if(value):
                return value
    elif datatype=="char" or datatype=="string":
        return strippedText(value)
    elif datatype=="date":
        return extractDate(value)
    elif datatype=="country":
        return extractCountry(value)
    elif datatype=="multivalue":
        return extarctFromMultivalue(value,expectedValues)
    elif datatype=="zipcode":
        p = re.compile(r'\d{4} [A-Za-z]{2}')
        value=p.findall(value)
        if len(value)>0:
            return value[0]
    return value
#-----------------------------------------------------------------------------------------------------------------------
def extarctFromMultivalue(text,expectedValues):
    for candidateValue in expectedValues:
        if re.search(r'\b' + candidateValue.lower() + r'\b', text.lower()):
            return expectedValues[candidateValue]
    return "Other Category"
#-----------------------------------------------------------------------------------------------------------------------
def extarctFromMultivalueByFrequecny(text,expectedValues):
    lstPotentialValues={}

    for candidateValue in expectedValues:
        if candidateValue.lower() in text.lower():
            potentialValue=expectedValues[candidateValue]
            if potentialValue not in lstPotentialValues:
                lstPotentialValues[potentialValue]=1
            else:
                lstPotentialValues[potentialValue]=lstPotentialValues[potentialValue]+1
    if not lstPotentialValues:
        return "Other Category"

    maxValue=0
    maxCat=""
    for potentialValue in lstPotentialValues:
        if lstPotentialValues[potentialValue]>maxValue:
            maxValue=lstPotentialValues[potentialValue]
            maxCat=potentialValue

    return maxCat
#-----------------------------------------------------------------------------------------------------------------------
def extractCountry(text):
    for country in pycountry.countries:
        if country.name in text:
            return (country.name)

    countryCodes={'Afghanistan': 'AF',
                  'Albania': 'AL',
                  'Algeria': 'DZ',
                  'American Samoa': 'AS',
                  'Andorra': 'AD',
                  'Angola': 'AO',
                  'Anguilla': 'AI',
                  'Antarctica': 'AQ',
                  'Antigua and Barbuda': 'AG',
                  'Argentina': 'AR',
                  'Armenia': 'AM',
                  'Aruba': 'AW',
                  'Australia': 'AU',
                  'Austria': 'AT',
                  'Azerbaijan': 'AZ',
                  'Bahamas': 'BS',
                  'Bahrain': 'BH',
                  'Bangladesh': 'BD',
                  'Barbados': 'BB',
                  'Belarus': 'BY',
                  'Belgium': 'BE',
                  'Belize': 'BZ',
                  'Benin': 'BJ',
                  'Bermuda': 'BM',
                  'Bhutan': 'BT',
                  'Bolivia, Plurinational State of': 'BO',
                  'Bonaire, Sint Eustatius and Saba': 'BQ',
                  'Bosnia and Herzegovina': 'BA',
                  'Botswana': 'BW',
                  'Bouvet Island': 'BV',
                  'Brazil': 'BR',
                  'British Indian Ocean Territory': 'IO',
                  'Brunei Darussalam': 'BN',
                  'Bulgaria': 'BG',
                  'Burkina Faso': 'BF',
                  'Burundi': 'BI',
                  'Cambodia': 'KH',
                  'Cameroon': 'CM',
                  'Canada': 'CA',
                  'Cape Verde': 'CV',
                  'Cayman Islands': 'KY',
                  'Central African Republic': 'CF',
                  'Chad': 'TD',
                  'Chile': 'CL',
                  'China': 'CN',
                  'Christmas Island': 'CX',
                  'Cocos (Keeling) Islands': 'CC',
                  'Colombia': 'CO',
                  'Comoros': 'KM',
                  'Congo': 'CG',
                  'Congo, the Democratic Republic of the': 'CD',
                  'Cook Islands': 'CK',
                  'Costa Rica': 'CR',
                  'Country name': 'Code',
                  'Croatia': 'HR',
                  'Cuba': 'CU',
                  'Curaçao': 'CW',
                  'Cyprus': 'CY',
                  'Czech Republic': 'CZ',
                  "Côte d'Ivoire": 'CI',
                  'Denmark': 'DK',
                  'Djibouti': 'DJ',
                  'Dominica': 'DM',
                  'Dominican Republic': 'DO',
                  'Ecuador': 'EC',
                  'Egypt': 'EG',
                  'El Salvador': 'SV',
                  'Equatorial Guinea': 'GQ',
                  'Eritrea': 'ER',
                  'Estonia': 'EE',
                  'Ethiopia': 'ET',
                  'Falkland Islands (Malvinas)': 'FK',
                  'Faroe Islands': 'FO',
                  'Fiji': 'FJ',
                  'Finland': 'FI',
                  'France': 'FR',
                  'French Guiana': 'GF',
                  'French Polynesia': 'PF',
                  'French Southern Territories': 'TF',
                  'Gabon': 'GA',
                  'Gambia': 'GM',
                  'Georgia': 'GE',
                  'Germany': 'DE',
                  'Ghana': 'GH',
                  'Gibraltar': 'GI',
                  'Greece': 'GR',
                  'Greenland': 'GL',
                  'Grenada': 'GD',
                  'Guadeloupe': 'GP',
                  'Guam': 'GU',
                  'Guatemala': 'GT',
                  'Guernsey': 'GG',
                  'Guinea': 'GN',
                  'Guinea-Bissau': 'GW',
                  'Guyana': 'GY',
                  'Haiti': 'HT',
                  'Heard Island and McDonald Islands': 'HM',
                  'Holy See (Vatican City State)': 'VA',
                  'Honduras': 'HN',
                  'Hong Kong': 'HK',
                  'Hungary': 'HU',
                  'ISO 3166-2:GB': '(.uk)',
                  'Iceland': 'IS',
                  'India': 'IN',
                  'Indonesia': 'ID',
                  'Iran, Islamic Republic of': 'IR',
                  'Iraq': 'IQ',
                  'Ireland': 'IE',
                  'Isle of Man': 'IM',
                  'Israel': 'IL',
                  'Italy': 'IT',
                  'Jamaica': 'JM',
                  'Japan': 'JP',
                  'Jersey': 'JE',
                  'Jordan': 'JO',
                  'Kazakhstan': 'KZ',
                  'Kenya': 'KE',
                  'Kiribati': 'KI',
                  "Korea, Democratic People's Republic of": 'KP',
                  'Korea, Republic of': 'KR',
                  'Kuwait': 'KW',
                  'Kyrgyzstan': 'KG',
                  "Lao People's Democratic Republic": 'LA',
                  'Latvia': 'LV',
                  'Lebanon': 'LB',
                  'Lesotho': 'LS',
                  'Liberia': 'LR',
                  'Libya': 'LY',
                  'Liechtenstein': 'LI',
                  'Lithuania': 'LT',
                  'Luxembourg': 'LU',
                  'Macao': 'MO',
                  'Macedonia, the former Yugoslav Republic of': 'MK',
                  'Madagascar': 'MG',
                  'Malawi': 'MW',
                  'Malaysia': 'MY',
                  'Maldives': 'MV',
                  'Mali': 'ML',
                  'Malta': 'MT',
                  'Marshall Islands': 'MH',
                  'Martinique': 'MQ',
                  'Mauritania': 'MR',
                  'Mauritius': 'MU',
                  'Mayotte': 'YT',
                  'Mexico': 'MX',
                  'Micronesia, Federated States of': 'FM',
                  'Moldova, Republic of': 'MD',
                  'Monaco': 'MC',
                  'Mongolia': 'MN',
                  'Montenegro': 'ME',
                  'Montserrat': 'MS',
                  'Morocco': 'MA',
                  'Mozambique': 'MZ',
                  'Myanmar': 'MM',
                  'Namibia': 'NA',
                  'Nauru': 'NR',
                  'Nepal': 'NP',
                  'Netherlands': 'NL',
                  'New Caledonia': 'NC',
                  'New Zealand': 'NZ',
                  'Nicaragua': 'NI',
                  'Niger': 'NE',
                  'Nigeria': 'NG',
                  'Niue': 'NU',
                  'Norfolk Island': 'NF',
                  'Northern Mariana Islands': 'MP',
                  'Norway': 'NO',
                  'Oman': 'OM',
                  'Pakistan': 'PK',
                  'Palau': 'PW',
                  'Palestine, State of': 'PS',
                  'Panama': 'PA',
                  'Papua New Guinea': 'PG',
                  'Paraguay': 'PY',
                  'Peru': 'PE',
                  'Philippines': 'PH',
                  'Pitcairn': 'PN',
                  'Poland': 'PL',
                  'Portugal': 'PT',
                  'Puerto Rico': 'PR',
                  'Qatar': 'QA',
                  'Romania': 'RO',
                  'Russian Federation': 'RU',
                  'Rwanda': 'RW',
                  'Réunion': 'RE',
                  'Saint Barthélemy': 'BL',
                  'Saint Helena, Ascension and Tristan da Cunha': 'SH',
                  'Saint Kitts and Nevis': 'KN',
                  'Saint Lucia': 'LC',
                  'Saint Martin (French part)': 'MF',
                  'Saint Pierre and Miquelon': 'PM',
                  'Saint Vincent and the Grenadines': 'VC',
                  'Samoa': 'WS',
                  'San Marino': 'SM',
                  'Sao Tome and Principe': 'ST',
                  'Saudi Arabia': 'SA',
                  'Senegal': 'SN',
                  'Serbia': 'RS',
                  'Seychelles': 'SC',
                  'Sierra Leone': 'SL',
                  'Singapore': 'SG',
                  'Sint Maarten (Dutch part)': 'SX',
                  'Slovakia': 'SK',
                  'Slovenia': 'SI',
                  'Solomon Islands': 'SB',
                  'Somalia': 'SO',
                  'South Africa': 'ZA',
                  'South Georgia and the South Sandwich Islands': 'GS',
                  'South Sudan': 'SS',
                  'Spain': 'ES',
                  'Sri Lanka': 'LK',
                  'Sudan': 'SD',
                  'Suriname': 'SR',
                  'Svalbard and Jan Mayen': 'SJ',
                  'Swaziland': 'SZ',
                  'Sweden': 'SE',
                  'Switzerland': 'CH',
                  'Syrian Arab Republic': 'SY',
                  'Taiwan, Province of China': 'TW',
                  'Tajikistan': 'TJ',
                  'Tanzania, United Republic of': 'TZ',
                  'Thailand': 'TH',
                  'Timor-Leste': 'TL',
                  'Togo': 'TG',
                  'Tokelau': 'TK',
                  'Tonga': 'TO',
                  'Trinidad and Tobago': 'TT',
                  'Tunisia': 'TN',
                  'Turkey': 'TR',
                  'Turkmenistan': 'TM',
                  'Turks and Caicos Islands': 'TC',
                  'Tuvalu': 'TV',
                  'Uganda': 'UG',
                  'Ukraine': 'UA',
                  'United Arab Emirates': 'AE',
                  'United Kingdom': 'GB',
                  'United States': 'US',
                  'United States Minor Outlying Islands': 'UM',
                  'Uruguay': 'UY',
                  'Uzbekistan': 'UZ',
                  'Vanuatu': 'VU',
                  'Venezuela, Bolivarian Republic of': 'VE',
                  'Viet Nam': 'VN',
                  'Virgin Islands, British': 'VG',
                  'Virgin Islands, U.S.': 'VI',
                  'Wallis and Futuna': 'WF',
                  'Western Sahara': 'EH',
                  'Yemen': 'YE',
                  'Zambia': 'ZM',
                  'Zimbabwe': 'ZW',
                  'Åland Islands': 'AX'}

    for country in countryCodes:
        if countryCodes[country]==text:
            return country

    return text
#-----------------------------------------------------------------------------------------------------------------------
def extractDate(strDate):

    patterns = [
        # 0) 1-12-1963
        r'(\d{1,2})-(\d{1,2})-(\d{4})',
        # 1) 1/12/1963
        r'(\d{1,2})/(\d{1,2})/(\d{4})',
        # 2) 1789-7-14
        r'(\d{4})-(\d{1,2})-(\d{1,2})',
        # 3) 1789\7\14
        r'(\d{4})\\(\d{1,2})\\(\d{1,2})',
        # 4) '1945-2'
        r'(\d{4})-(\d{1,2})',
        # 5) 2-1883
        r'(\d{1,2})-(\d{4})',
    ]
    selectedPattern=0

    extractedDate=""
    for pattern in patterns:
        p = re.compile(pattern)
        date=p.findall(strDate)
        if date:
            extractedDate=(date[0])
            break
        selectedPattern=selectedPattern+1

    if selectedPattern==0 or selectedPattern==1:
        extractedDate=extractedDate[2]+"-"+extractedDate[1]+"-"+extractedDate[0]
    elif selectedPattern==2 or selectedPattern==3:
        extractedDate=extractedDate[0]+"-"+extractedDate[1]+"-"+extractedDate[2]
    elif selectedPattern==4:
        extractedDate=extractedDate[0]+"-"+extractedDate[1]+"-01"
    elif selectedPattern==5:
        extractedDate=extractedDate[1]+"-"+extractedDate[0]+"-01"

    return extractedDate
#-----------------------------------------------------------------------------------------------------------------------
def saveMetadataInFile(metadata):
    filename= str(uuid.uuid4())
    path="index_files/"+config["decision_model"]+"/"

    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)

    f = open(path+config["decision_model"]+"-"+filename+".json", 'w+')
    f.write(json.dumps(metadata))
    f.close()
#-----------------------------------------------------------------------------------------------------------------------
def ingest_metadataFile(metadataFile):
    global config

    es = Elasticsearch("http://localhost:9200")
    index = Index(config['decision_model'], es)

    if not es.indices.exists(index=config['decision_model']):
        index.settings(
            index={'mapping': {'ignore_malformed': True}}
        )
        index.create()
    else:
        es.indices.close(index=config['decision_model'])
        put = es.indices.put_settings(
            index=config['decision_model'],
            body={
                "index": {
                    "mapping": {
                        "ignore_malformed": True
                    }
                }
            })
        es.indices.open(index=config['decision_model'])


        if config['allArray']=='True':
            id = metadataFile["url"][0]
        else:
            id = metadataFile["url"]

        res = es.index(index=config['decision_model'], id=id, body=metadataFile)
        es.indices.refresh(index=config['decision_model'])
#-----------------------------------------------------------------------------------------------------------------------
def indexWebpage(url):
    global config
    html=extractHTML(url)
    metadata={}
    if html!="":
        if config['allArray']=='True':
            metadata['url']=[removeURLparameters(url)]
        else:
            metadata['url']=removeURLparameters(url)
        for feature in config['features']:
            metadata[feature]=findValue(feature, html)

    if test:
        print(metadata)
    #........................................
    else:
        crawled_features={}
        for crawled_feature in config['equal_crawled_features']:
            if metadata[crawled_feature]!="N/A":
                crawled_features[crawled_feature]=metadata[crawled_feature]
            else:
                return {}

        if metadata and is_not_crawled(crawled_features):
            saveMetadataInFile(metadata)
            ingest_metadataFile(metadata)
        else:
            print("The url has been already crawled!")
    #........................................
    return metadata
#-----------------------------------------------------------------------------------------------------------------------
def extractJSONfromHTML(string):
    clean = re.compile('<.*?>')
    string = re.sub(clean, " ", string)
    jsonFile={}
    try:
        jsonFile=json.loads(string)
    except ValueError as e:
        return {}
    return jsonFile
#-----------------------------------------------------------------------------------------------------------------------
def getPropertyFromJSON(tag, feature):
    jsonFile={}
    property=config['features'][feature]['propertyValue']

    if(config['features'][feature]['metadataFormat']=="json" and property):
        jsonFile=extractJSONfromHTML(str(tag))
        lstproperty=property.split('.')

        hasChanged=False
        for property in lstproperty:
            if(jsonFile and  property in jsonFile):
                jsonFile=jsonFile[property]
                hasChanged=True
        if hasChanged:
            return filterByDatatype(jsonFile,config['features'][feature]['datatype'],config['features'][feature]['expectedValues'])
    return {}
#-----------------------------------------------------------------------------------------------------------------------
def findValue(feature, html):
    global config
    value=getValue(feature, html)
    value=filterValue(value, feature)
    datatype=config['features'][feature]['datatype']

    if (value!="N/A"):
        if datatype=="currency" or datatype=="int":
            value=value.replace(",","").replace(".","").strip()
            if value:
                value= int(value)
        elif datatype=="decimal":
            value= float(value.replace(",",""))
            if value:
                value= int(value)

    if config['allArray']=='True':
        value=[value]
    return value
#-----------------------------------------------------------------------------------------------------------------------
def filterValue(value, feature):
    removeValue=config['features'][feature]['removeValue']
    if removeValue:
        for rmVal in removeValue:
            value=value.replace(rmVal,'')
    return value
#-----------------------------------------------------------------------------------------------------------------------
def getValue(feature, html):
    global config

    tags=html.find_all(config['features'][feature]['tag'], {"class" : config['features'][feature]['cssClass']})

    if len(tags)==1:
        tag=tags[0]
        if not(config['features'][feature]['htmlAllowed']):
            if(config['features'][feature]['propertyValue']):
                tag=tag.attrs.get(config['features'][feature]['propertyValue'])
            return filterByDatatype(remove_tags(str(tag)), config['features'][feature]['datatype'],config['features'][feature]['expectedValues'])
        else:
            return str(tag)

    for tag in tags:

        propertyValue=getPropertyFromJSON(tag, feature)
        if(propertyValue):
            return propertyValue

        infix = getByInfix(feature,tag)
        if(infix):
            return str(infix)

        prefix=getByPrefix(feature,tag,html)
        if(prefix):
            return str(prefix)

        postfix=getByPostfix(feature,tag,html)
        if(postfix):
                return str(postfix)

    return "N/A"
#-----------------------------------------------------------------------------------------------------------------------
def getByPostfix(feature,tag,html):
    global config
    if type(tag)!=type(None):

        index=config['features'][feature]['searchKeywords']['postfix']['index']-1
        for cnt in range(1, index):
            tag=tag.next_element

        preTag=tag.find_next(config['features'][feature]['searchKeywords']['postfix']['tag'],class_=config['features'][feature]['searchKeywords']['postfix']['cssClass'])
        if type(preTag)!=type(None):
            property=config['features'][feature]['searchKeywords']['postfix']['propertyValue']
            tagContents=config['features'][feature]['searchKeywords']['postfix']['content']
            #------ propertyValue
            if(property):
                preTag=preTag.attrs.get(property)
                for tagContent in tagContents:
                    if tagContent == preTag:
                        property=config['features'][feature]['propertyValue']
                        if(property):
                            return filterByDatatype(tag.attrs.get(property), config['features'][feature]['datatype'],config['features'][feature]['expectedValues'])
                        else:
                            return filterByDatatype(str(tag), config['features'][feature]['datatype'],config['features'][feature]['expectedValues'])
            #------ Content
            for tagContent in tagContents:
                if tagContent and tagContent in str(preTag):
                    if not(config['features'][feature]['htmlAllowed']):
                        return filterByDatatype(remove_tags(str(tag)), config['features'][feature]['datatype'],config['features'][feature]['expectedValues'])
                    else:
                        return (str(tag))
    return {}
#-----------------------------------------------------------------------------------------------------------------------
def getByPrefix(feature,tag,html):
    global config
    if type(tag)!=type(None):
        index=config['features'][feature]['searchKeywords']['prefix']['index']-1

        for cnt in range(1, index):
            tag=tag.previous_element

        preTag=tag.find_previous(config['features'][feature]['searchKeywords']['prefix']['tag'],class_=config['features'][feature]['searchKeywords']['prefix']['cssClass'])
        if type(preTag)!=type(None):
            property=config['features'][feature]['searchKeywords']['prefix']['propertyValue']
            tagContents=config['features'][feature]['searchKeywords']['prefix']['content']
            #------ propertyValue
            if(property):
                preTag=preTag.attrs.get(property)
                for tagContent in tagContents:
                    if tagContent == preTag:
                        property=config['features'][feature]['propertyValue']
                        if(property):
                            return filterByDatatype(tag.attrs.get(property), config['features'][feature]['datatype'],config['features'][feature]['expectedValues'])
                        else:
                            return filterByDatatype(str(tag), config['features'][feature]['datatype'],config['features'][feature]['expectedValues'])
            #------ Content
            for tagContent in tagContents:
                if tagContent and tagContent in str(preTag):
                    if not(config['features'][feature]['htmlAllowed']):
                        return filterByDatatype(remove_tags(str(tag)), config['features'][feature]['datatype'],config['features'][feature]['expectedValues'])
                    else:
                        return (str(tag))
    return {}
#-----------------------------------------------------------------------------------------------------------------------
def getByInfix(feature,tag):
    global config
    if type(tag)!=type(None):
        infix=tag.find(config['features'][feature]['searchKeywords']['infix']['tag'], {"class" : config['features'][feature]['searchKeywords']['infix']['cssClass']})
    if type(infix)!=type(None):
        property=config['features'][feature]['searchKeywords']['infix']['propertyValue']
        tagContents=config['features'][feature]['searchKeywords']['infix']['content']
        #------ propertyValue
        if(property):
            preTag=preTag.attrs.get(property)
            for tagContent in tagContents:
                if tagContent == preTag:
                    property=config['features'][feature]['propertyValue']
                    if(property):
                        return filterByDatatype(tag.attrs.get(property), config['features'][feature]['datatype'],config['features'][feature]['expectedValues'])
                    else:
                        return filterByDatatype(str(tag), config['features'][feature]['datatype'],config['features'][feature]['expectedValues'])
        #------ Content
        for tagContent in tagContents:
            if tagContent and tagContent in str(infix):
                if not(config['features'][feature]['htmlAllowed']):
                    return filterByDatatype(remove_tags(str(tag)), config['features'][feature]['datatype'],config['features'][feature]['expectedValues'])
                else:
                    return (str(tag))
    return {}
#-----------------------------------------------------------------------------------------------------------------------
def is_not_crawled(features):

    global config

    es = Elasticsearch("http://localhost:9200")
    index = Index(config['decision_model'], es)

    if not es.indices.exists(index=config['decision_model']):
        index.settings(
            index={'mapping': {'ignore_malformed': True}}
        )
        index.create()
    else:
        es.indices.close(index=config['decision_model'])
        put = es.indices.put_settings(
            index=config['decision_model'],
            body={
                "index": {
                    "mapping": {
                        "ignore_malformed": True
                    }
                }
            })
        es.indices.open(index=config['decision_model'])

    query_conditions=[]
    for feature in features:
        if (config['allArray']=='True' and features[feature] == ["N/A"]) or (config['allArray']=='False' and features[feature] == "N/A"):
            return False
        if feature=="url":
            query={"term": {'_id': features['url'][0]}}
        else:
            query={"term": {feature: features[feature]}}
        query_conditions.append(query)

    user_request = "some_param"
    query_body = {
        "query": {
            "bool": {
                "must": query_conditions
            },
        },
        "from": 0,
        "size": 1,
    }
    try:
        result = es.search(index=config['decision_model'], body=query_body)
    except:
        return False

    numHits=result['hits']['total']['value']

    return False if numHits>0 else True
#-----------------------------------------------------------------------------------------------------------------------
def enableTestModel(website, url):
    global test
    global config
    test=True
    config=openCrawlerConfig(website)
    indexWebpage(url)
#-----------------------------------------------------------------------------------------------------------------------
def open_file(file):
    read_path = file
    with open(read_path, "r", errors='ignore') as read_file:
        data = json.load(read_file)
    return data
#-----------------------------------------------------------------------------------------------------------------------
def ingestIndexes(decisionModel, sourceDirectory, equalityCheckFeature,isArray):
    es = Elasticsearch("http://localhost:9200")
    index = Index(decisionModel, es)

    if not es.indices.exists(index=decisionModel):
        index.settings(
            index={'mapping': {'ignore_malformed': True}}
        )
        index.create()
    else:
        es.indices.close(index=decisionModel)
        put = es.indices.put_settings(
            index=decisionModel,
            body={
                "index": {
                    "mapping": {
                        "ignore_malformed": True
                    }
                }
            })
        es.indices.open(index=decisionModel)
    cnt=0
    root=(os. getcwd()+sourceDirectory)
    for path, subdirs, files in os.walk(root):
        for name in files:
            cnt=cnt+1
            indexfile= os.path.join(path, name)
            indexfile = open_file(indexfile)

            id=""
            if isArray:
                id=indexfile[equalityCheckFeature][0]
            else:
                id=indexfile[equalityCheckFeature]

            res = es.index(index=decisionModel, id= id, body=indexfile)
            es.indices.refresh(index=decisionModel)
            print(str(cnt)+" recode added!")
#-----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    indexWebsite("lifewatch")
    #enableTestModel("lifewatch", "https://metadatacatalogue.lifewatch.eu/srv/api/records/oai:marineinfo.org:id:dataset:610")
    #ingestIndexes("envri","/index_files/envri/","url", True)
#-----------------------------------------------------------------------------------------------------------------------
