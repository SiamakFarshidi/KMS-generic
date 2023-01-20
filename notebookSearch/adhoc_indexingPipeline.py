from django.forms.widgets import NullBooleanSelect, Widget
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
import simplejson
from urllib.request import urlopen
import urllib
from datetime import datetime
from elasticsearch import Elasticsearch
from glob import glob
from elasticsearch_dsl import Search, Q, Index
from elasticsearch_dsl.query import MatchAll
from django.core import serializers
import numpy as np
import json
import uuid
import os
from github import BadCredentialsException
from github import Github
import time
import re
ACCESS_TOKEN_Github = os.environ['ACCESS_TOKEN_Github']
ACCESS_TOKEN_Gitlab = os.environ['ACCESS_TOKEN_Gitlab']

elasticsearch_url = os.environ['ELASTICSEARCH_URL']
elasticsearch_username = os.environ.get('ELASTICSEARCH_USERNAME')
elasticsearch_password = os.environ.get('ELASTICSEARCH_PASSWORD')

# ----------------------------------------------------------------
def open_file(file):
    read_path = file
    with open(read_path, "r", errors='ignore') as read_file:
        data = json.load(read_file)
    return data
# ----------------------------------------------------------------
def indexingpipeline():
    es = Elasticsearch(elasticsearch_url,http_auth=[elasticsearch_username, elasticsearch_password])
    index = Index('notebooks', es)

    if not es.indices.exists(index='notebooks'):
        index.settings(
            index={'mapping': {'ignore_malformed': True}}
        )
        index.create()
    else:
        es.indices.close(index='notebooks')
        put = es.indices.put_settings(
            index='notebooks',
            body={
                "index": {
                    "mapping": {
                        "ignore_malformed": True
                    }
                }
            })
        es.indices.open(index='notebooks')
    cnt=0
    root=(os. getcwd()+"/Jupyter Notebook/")
    for path, subdirs, files in os.walk(root):
        for name in files:
            cnt=cnt+1
            indexfile= os.path.join(path, name)
            indexfile = open_file(indexfile)
            newRecord={
                "name":indexfile["name"],
                "full_name":indexfile["full_name"],
                "stargazers_count":indexfile["stargazers_count"],
                "forks_count":indexfile["forks_count"],
                "description":indexfile["description"],
                "size":indexfile["size"],
                "language": indexfile["language"],
                "html_url":indexfile["html_url"],
                "git_url":indexfile["git_url"]
            }
            res = es.index(index="notebooks", id= indexfile["git_url"], body=newRecord)
            es.indices.refresh(index="notebooks")
            print(str(cnt)+" recode added! \n")
# ----------------------------------------------------------------
def search_repository_github(keywords):
    g = Github(ACCESS_TOKEN_Github)
    keywords = [keyword.strip() for keyword in keywords.split(',')]
    keywords.append("notebook")
    query = '+'.join(keywords)+ '+in:readme+in:description'
    result = g.search_repositories(query, 'stars', 'desc')
    cnt=0
    data=[]
    iter_obj = iter(result)
    while True:
        try:
            cnt=cnt+1
            repo = next(iter_obj)
            new_record= {
                "id":cnt,
                "name": repo.full_name,
                "description": re.sub(r'[^A-Za-z0-9 ]+', '',repo.description),
                "html_url":repo.html_url,
                "git_url": repo.clone_url,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "size": repo.size,
            }


            if new_record["language"]=="Jupyter Notebook" and new_record not in data:
                data.append(new_record)
        except StopIteration:
            break
        except RateLimitExceededException:
            continue
    data=(json.dumps({"results_count": result.totalCount,"hits":data}).replace("'",'"'))
    return  json.loads(data)
# ----------------------------------------------------------------
def test():
    response_data=search_repository_github('')
    print(response_data)
    indexFile= open("notebooks.json","w+")
    indexFile.write(json.dumps(response_data))
    indexFile.close()
    indexingpipeline()
# ----------------------------------------------------------------

def get_most_starred_repos():
    g = Github(ACCESS_TOKEN_Github)
    languages=["Jupyter Notebook"]
    for lang in languages:
        i = 0
        # create folder named after current language
        if not os.path.exists(lang):
            os.makedirs(lang)
        # search top repos of lang by descending stars

        potentialQueries=[
            "Temperature","Vapour","Wind","Speed","Direction","Aerosols","Properties",
            "Aerosols","Carbon","Dioxide","Methane","other","Greenhouse","Gases","Cloud","Properties","Ozone","Precursors","for","aerosols","ozone",
            "Precursors","Clouds","Above-Ground","Biomass","Albedo","Anthropogenic","Greenhouse","Gas","Fluxes","Anthropogenic","Water",
            "Fire","Fraction","Absorbed","Photosynthetically","Active","Radiation","FAPAR","Glaciers","Groundwater","Ice","Sheets","Ice","Shelves",
            "Lakes","Land","Cover","Land","Surface","Temperature","Latent","Sensible","Heat","Fluxes","Leaf","Area","Index","LAI","Permafrost",
            "River","Discharge","Snow","Soil","Carbon","Soil","Moisture","ICOS","SeaDataNet","LifeWatch","AnaEE","ACTRIS","AQUACOSM","ARISE","DANUBIUS-RI","DiSSCo",
            "workflow","marine","weather","geography","environment","CO2","EISCAT","3D","eLTER","RI","EMBRC",
            "EMSO","EMPHASIS","EPOS","EUFAR","Euro-Argo","ERIC","EUROFLEETS","EuroGOOS","EUROCHAMP","HEMERA","IAGOS",
            "INTERACT","IS-ENES","JERICO-RI","SIOS","atmosphere","wave","telecommunication","electronics","plankton","temperature",
            "Nitrous","birds", "Oxide", "Habitat", "Inbreeding", "Morphology", "Physiology", "Phenology", "Taxonomic", "diversity",
            "Ecosystem", "Precipitation", "rain","reinforcement learning", "quantum", "decision tree",
            "decision making", "decision structure", "data mining", "data analysis",
            "software engineering", "fuzzy", "math", "physics", "chemistry", "logic", "recommender", "lab", "biology", "organic", "green gas",
            "substance", "particle", "technology", "psychology", "atom", "periodic table", "astronomy", "Biochemistry", "bio", "cycle", "geometry",
            "Natural", "nature", "volcano", "crust", "lava", "oxygen", "carbon", "density", "gravity", "cell",
            "Pressure","state", "deep learning", "Ocean","stress","stress","ice","level","height","temperature","Subsurface","temperature","currents","currents", "color",
            "Sea","salinity","subsurface","salinity","heat","flux","colour","Sound","Phytoplankton","biomass","diversity",
            "Nutrients","Fish","abundace","Transient","traces","Particulate","matter","Nitrous","oxide","Stable","carbon","isotopes",
            "Dissolved","organic","carbon","Microbe","biomass","diversity","Invertebrate","abundance","distribution",
            "Marine","turtles,","birds,","mammals","abundance","distribution","Hard","coral","cover","composition","Seagrass","cover","composition",
            "Macroalgal","canopy","cover","composition","Mangrove","cover","composition","Inorganic","Carbon","Nitrous","Oxide",
            "Nutrients","Oxygen","Transient","Tracers","Marine","Habitat","Properties","Genetic","diversity","richness","heterozygosity",
            "Genetic","differentiation","number","genetic","units","genetic","distance","Effective","population","size","Inbreeding",
            "Species","distributions","Species","abundances","Morphology","Physiology","Phenology","Movement","Community","abundance",
            "Taxonomic","phylogenetic","diversity","Trait","diversity","Interaction","diversity","Primary","productivity","Ecosystem","phenology",
            "Ecosystem","disturbances","Live","cover","fraction","Ecosystem","distribution","Ecosystem","Vertical","Profile","Precipitation",
            "Pressure","Radiation","budget","Radiation","Budget","Wind","Speed","Direction","Temperature","Vapour",
            "Earth","Radiation","Budget","Lightning"]
        for query in potentialQueries:
            print ("\n\n------------------- Current query:  " + query.lower() +"  ---------------------\n\n")
            for repo in g.search_repositories(query.lower(),sort="stars", order="desc", language=lang):
                try:
                    temp_data = {}
                    temp_data["name"] = repo.name
                    temp_data["full_name"] = repo.full_name
                    temp_data["stargazers_count"] = repo.stargazers_count
                    temp_data["forks_count"] = repo.forks_count
                    temp_data["description"] = re.sub(r'[^A-Za-z0-9 ]+', '',repo.description)
                    temp_data["id"] = repo.id
                    temp_data["size"] = repo.size
                    temp_data["language"] = repo.language
                    temp_data["html_url"] = repo.html_url
                    temp_data["git_url"] = repo.clone_url
                    filename= re.sub(r'[^A-Za-z0-9 ]+', '',repo.name)+"_"+"_"+str(repo.id)+"_"+str(repo.size)
                    f = open(lang+"/"+filename+".json", 'w+')
                    f.write(json.dumps(temp_data))
                    f.close()
                    print(repo.html_url)
                except:
                    print("Pleaes wait for a couple of seconds...")
                    time.sleep(10)
            time.sleep(10)
# ----------------------------------------------------------------
indexingpipeline()