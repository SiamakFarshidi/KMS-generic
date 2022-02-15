from os import walk
from bs4 import BeautifulSoup
import requests
import os
import json
import sys
import re
import spacy
import nltk
import numpy as np
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
import gensim
from gensim import corpora
import enchant
from fuzzywuzzy import fuzz

#nltk.download('wordnet')
#nltk.download('stopwords')

EnglishTerm = enchant.Dict("en_US")
stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()
Lda = gensim.models.ldamodel.LdaModel

spacy_nlp  = spacy.load('en_core_web_md')

datasets_root="./dataset source files/";
indexFiles_root="./index files/";
metadataStar_root="./Metadata*/metadata*.json";
essentialVariabels_root="./Metadata*/essential_variables.json";
domain_root="./Metadata*/domain.json";
RI_root="./Metadata*/RIs.json";
processedFiles="./processed datasets/"
domainVocbularies_root="./Metadata*/Vocabularies.json"

acceptedSimilarityThreshold=0.8

#----------------------------------------------------------------------------------------
def listToString(s):
    str1 = ""
    for ele in s:
        str1 += ele
    return str1
#----------------------------------------------------------------------------------------
def extractTextualContent(y):
    out = {}
    lstvalues=[]
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x
            text=x
            if type(text)==list or type(text)==dict:
                text=" ".join(str(x) for x in text)
            if type(text)==str and len(text)>1:
                text=re.sub(r'http\S+', '', text)
                if type(text)==str and len(text)>1:
                    lstvalues.append(text)
    flatten(y)
    return lstvalues
#----------------------------------------------------------------------------------------
def clean(doc):
    integer_free = ''.join([i for i in doc if not i.isdigit()])
    stop_free = " ".join([i for i in integer_free.lower().split() if i not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split() if len(word)>2 and EnglishTerm.check(word))
    return normalized
#----------------------------------------------------------------------------------------
def topicMining(dataset_content):
    Jsontext=extractTextualContent(dataset_content)
    doc_clean = [clean(doc).split() for doc in Jsontext]
    dictionary = corpora.Dictionary(doc_clean)
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]
    ldamodel = gensim.models.LdaMulticore(corpus=doc_term_matrix,id2word=dictionary,num_topics=5,passes=20)
    topics=ldamodel.show_topics(log=True, formatted=True)
    topTopics= sum([re.findall('"([^"]*)"',listToString(t[1])) for t in topics],[])
    lsttopic=[]
    for topic in topTopics:
        lsttopic.append(topic) if topic not in lsttopic else lsttopic
    return lsttopic
#----------------------------------------------------------------------------------------
def getTopicsByDomainVocabulareis(topics,domain):
    Vocabs=[]
    domainVocbularies_content = open(domainVocbularies_root,"r")
    domainVocbularies_object = json.loads(domainVocbularies_content.read())
    for vocab in domainVocbularies_object[domain]:
        for topic in topics:
            w1=spacy_nlp(topic.lower())
            w2=spacy_nlp(vocab.lower())
            similarity=w1.similarity(w2)
            if similarity > acceptedSimilarityThreshold:
                Vocabs.append(vocab) if vocab not in Vocabs else Vocabs
    return Vocabs
#----------------------------------------------------------------------------------------
def similatiyBagsOfWords(bagOfWords1,bagOfWords2):
    w2=spacy_nlp(listToString(bagOfWords2).lower())
    w1=spacy_nlp(listToString(bagOfWords1).lower())
    return  w1.similarity(w2)
#----------------------------------------------------------------------------------------
def getRI(dataset_content):
    RI_content = open(RI_root,"r")
    RI_json = json.loads(RI_content.read())
    dataset_content=extractTextualContent(dataset_content)
    for RI in RI_json:
        for RI_keys in RI_json[RI]:
            for ds in dataset_content:
                if RI_keys in ds:
                    return  RI
#----------------------------------------------------------------------------------------
def getDomain(RI_seed):
    domain_content = open(domain_root,"r")
    domain_json = json.loads(domain_content.read())
    for RI in domain_json:
        if RI == RI_seed:
            return domain_json[RI]
#----------------------------------------------------------------------------------------
def getDomainEssentialVariables(domain):
    essentialVariabels_content = open(essentialVariabels_root,"r")
    essentialVariabels_json = json.loads(essentialVariabels_content.read())
    for domainVar in essentialVariabels_json:
        if domain==domainVar:
            return essentialVariabels_json[domain]
#----------------------------------------------------------------------------------------
def getSimilarEssentialVariables(essentialVariables, topics):
    lstEssentialVariables=[]
    for variable in essentialVariables:
        for topic in topics:
            w1=spacy_nlp(topic.lower())
            w2=spacy_nlp(variable.lower())
            similarity=w1.similarity(w2)
            if similarity > acceptedSimilarityThreshold:
                lstEssentialVariables.append(variable) if variable not in lstEssentialVariables else lstEssentialVariables
    return lstEssentialVariables
#----------------------------------------------------------------------------------------
def refineResults(TextArray,datatype,proprtyName):
    datatype=datatype.lower()
    refinedResults=[]
    if len(TextArray):
        if type(TextArray)==str:
            TextArray=[TextArray]
        if type(TextArray)==dict:
            TextArray=list(NestedDictValues(TextArray))

        if type(TextArray)==list:
            TextArray=flatten_list(TextArray)
            values=[]
            for text in TextArray:
                if type(text)==dict:
                    text= list(NestedDictValues(text))
                    values.append(text)
                elif type(text)==list:
                    values=values+text
                else:
                    values.append(text)
            if type (values) == list and len(values):
                TextArray=flatten_list(values)

        for text in TextArray:
            doc = spacy_nlp(str(text).strip())
            #..................................................................................
            if (type(text)==str and  "url" in datatype):
                urls = re.findall("(?P<url>https?://[^\s]+)", text)
                if len(urls):
                    refinedResults.append(urls) if urls not in refinedResults else refinedResults
            #..................................................................................
            if ("person" in datatype):
                if doc.ents:
                    for ent in doc.ents:
                        if (len(ent.text)>0) and ent.label_=="PERSON":
                            refinedResults.append(ent.text) if ent.text not in refinedResults else refinedResults
            #..................................................................................
            if ("organization" in datatype):
                if doc.ents:
                    for ent in doc.ents:
                        if(len(ent.text)>0) and ent.label_=="ORG":
                            refinedResults.append(ent.text) if ent.text not in refinedResults else refinedResults
            #..................................................................................
            if ("place" in datatype):
                if doc.ents:
                    for ent in doc.ents:
                        if(len(ent.text)>0) and ent.label_=="GPE" or ent.label_=="LOC":
                            refinedResults.append(ent.text) if ent.text not in refinedResults else refinedResults
            #..................................................................................
            if ("date" in datatype):
                if doc.ents:
                    for ent in doc.ents:
                        if(len(ent.text)>0) and ent.label_=="DATE":
                            refinedResults.append(ent.text) if ent.text not in refinedResults else refinedResults
            #..................................................................................
            if ("product" in datatype):
                if doc.ents:
                    for ent in doc.ents:
                        if(len(ent.text)>0) and ent.label_=="PRODUCT":
                            refinedResults.append(ent.text) if ent.text not in refinedResults else refinedResults
            #..................................................................................
            if ("integer" in datatype) or ("number" in datatype ):
                if doc.ents:
                    for ent in doc.ents:
                        if(len(ent.text)>0) and ent.label_=="CARDINAL":
                            refinedResults.append(ent.text) if ent.text not in refinedResults else refinedResults
            #..................................................................................
            if ("money" in datatype):
                if doc.ents:
                    for ent in doc.ents:
                        if(len(ent.text)>0) and ent.label_=="MONEY":
                            refinedResults.append(ent.text) if ent.text not in refinedResults else refinedResults
            #..................................................................................
            if ("workofart" in datatype):
                if doc.ents:
                    for ent in doc.ents:
                        if(len(ent.text)>0) and ent.label_=="WORK_OF_ART":
                            refinedResults.append(ent.text) if ent.text not in refinedResults else refinedResults
            #..................................................................................
            if ("language" in datatype):
                if doc.ents:
                    for ent in doc.ents:
                        print(ent.label_)
                        if(len(ent.text)>0) and ent.label_=="LANGUAGE" or ent.label_=="GPE":
                            refinedResults.append(ent.text) if ent.text not in refinedResults else refinedResults
            #..................................................................................
            if proprtyName.lower() not in str(text).lower() and ("text" in datatype or "definedterm" in datatype):
                refinedResults.append(text) if text not in refinedResults else refinedResults
            #..................................................................................
    return refinedResults
#----------------------------------------------------------------------------------------
def flatten_dict(dd, separator='_', prefix=''):
    return { prefix + separator + k if prefix else k : v
             for kk, vv in dd.items()
             for k, v in flatten_dict(vv, separator, kk).items()
             } if isinstance(dd, dict) else { prefix : dd }
#----------------------------------------------------------------------------------------
def NestedDictValues(d):
    for v in d.values():
        if isinstance(v, dict):
            yield from NestedDictValues(v)
        else:
            yield v
#----------------------------------------------------------------------------------------
def remove_none(obj):
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(remove_none(x) for x in obj if x is not None)
    elif isinstance(obj, dict):
        return type(obj)((remove_none(k), remove_none(v))
                         for k, v in obj.items() if k is not None and v is not None)
    else:
        return obj
#----------------------------------------------------------------------------------------
def is_nested_list(l):
    try:
        next(x for x in l if isinstance(x,list))
    except StopIteration:
        return False
    return True
#----------------------------------------------------------------------------------------
def flatten_list(t):
    if(is_nested_list(t)):
        return [item for sublist in t for item in sublist if type(sublist)==list and type(sublist)!= type(None)]
    return t
#----------------------------------------------------------------------------------------
foundResults=[]
def deep_search(needles, haystack):
    found = {}
    if type(needles) != type([]):
        needles = [needles]

    if type(haystack) == type(dict()):
        for needle in needles:
            if needle in haystack.keys():
                found[needle] = haystack[needle]
            elif len(haystack.keys()) > 0:
                #--------------------- Fuzzy calculation
                for key in haystack.keys():
                    if fuzz.ratio(needle.lower(),key.lower()) > 75:
                        found[needle] = haystack[key]
                        break
                #--------------------- ^
                for key in haystack.keys():
                    result = deep_search(needle, haystack[key])
                    if result:
                        for k, v in result.items():
                            found[k] = v
                            foundResults.append(v) if v not in foundResults else foundResults
    elif type(haystack) == type([]):
        for node in haystack:
            result = deep_search(needles, node)
            if result:
                for k, v in result.items():
                    found[k] = v
                    foundResults.append(v) if v not in foundResults else foundResults
    return found

def searchField(field,datatype,json):
    foundResults.clear()
    deep_search(field,json)
    refinedResults=refineResults(foundResults,datatype,field)
    return refinedResults
#----------------------------------------------------------------------------------------
def url_to_string(url):
    res = requests.get(url)
    html = res.text
    soup = BeautifulSoup(html, 'html5lib')
    for script in soup(["script", "style", 'aside']):
        script.extract()
    return " ".join(re.split(r'[\n\t]+', soup.get_text()))
#----------------------------------------------------------------------------------------
def ProcessDataset(dataset_path):
    print (dataset_path)

    indexfname = os.path.join(indexFiles_root,os.path.basename(dataset_path))
    indexFile= open(indexfname,"w+")
    indexFile.write("{\n")

    dataset_content = open(dataset_path,"r")
    JSON = json.loads(dataset_content.read())

    metadataStar_content = open(metadataStar_root,"r")
    metadataStar_object = json.loads(metadataStar_content.read())

    searchFields=[]
    RI=""
    domains=""
    topics=[]
    cnt=0
    for metadata_property in metadataStar_object:
        cnt=cnt+1
        if metadata_property=="ResearchInfrastructure":
            result= getRI(JSON)
        elif metadata_property=="theme":
            if not len(RI):
                RI= getRI(JSON)
            if not len(domains):
                domains = getDomain(RI)
            if not len(topics):
                topics=topicMining(JSON)
            result=getTopicsByDomainVocabulareis(topics,domains[0])
        elif metadata_property=="EssentialVariables":
            if not len(RI):
                RI= getRI(JSON)
            if not len(domains):
                domains = getDomain(RI)
            if not len(topics):
                topics=topicMining(JSON)
            essentialVariables=getDomainEssentialVariables(domains[0])
            result=getSimilarEssentialVariables(essentialVariables,topics)
        else:
            result=deep_search([metadata_property],JSON)
            if not len(result):
                searchFields=[]
                for i in range (3, len(metadataStar_object[metadata_property])):
                    result=deep_search([metadataStar_object[metadata_property][i]],JSON)
                    if len(result): searchFields.append(result)
                result=searchFields
        propertyDatatype=metadataStar_object[metadata_property][0]
        result=refineResults(result,propertyDatatype,metadata_property)
        if(cnt==len(metadataStar_object)):
            extrachar="\n"
        else:
            extrachar=",\n"
        indexFile.write("\""+str(metadata_property)+"\" :"+str(result).replace("'","\"")+extrachar)
    indexFile.write("}")
    indexFile.close()

    #indexFile.write(metadata_property)
    #indexFile.close()
    #
    #RI= getRI(datasets_root+"SeaDataNet.json")
    #domains = getDomain(RI)
    #for domain in domains:
    #    essentialVariables=getDomainEssentialVariables(domain)
    #    essentialVariables=getSimilarEssentialVariables(essentialVariables,topics)
    #for r in foundResults:
    #    print(r)
#----------------------------------------------------------------------------------------
def TraverseFiles(root): #implement moving files
    for dirpath, dirs, files in walk(root):
        for filename in files:
            fname = os.path.join(dirpath,filename)
            ProcessDataset(fname)
#----------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------
# Main
#TraverseFiles(datasets_root)
#ProcessDataset(datasets_root+"SeaDataNet.json")
ProcessDataset(datasets_root+"DiSSCo.json")





