from django.shortcuts import render
from elasticsearch import Elasticsearch
import json
import numpy as np

# Create your views here.
es = Elasticsearch("http://localhost:9200")
#---------------------------------------------------------------------------------------------------------------------
def landingpage(request):
    return render(request,'landingpage.html',{})
#---------------------------------------------------------------------------------------------------------------------

def mergeList(first_list, second_list):
    resulting_list = list(first_list)
    resulting_list.extend(x for x in second_list if x not in resulting_list)
    return resulting_list
#---------------------------------------------------------------------------------------------------------------------

def genericpages(request):

    try:
        page = request.GET['page']
    except:
        page = ''

    try:
        term = request.GET['term']
    except:
        term = ''
    #----------------------------------------------
    if page=="publications":
        return render(request,'publications.html',{"searchTerm":term,  "functionList": getAllfunctionList(request)})
    #----------------------------------------------
    elif page=="recommendation":
        return render(request,'recommendation.html',returnResult)
    #----------------------------------------------
    elif page=="RnD":
        return render(request,'RnDTeam.html',{"searchTerm":term,  "functionList": getAllfunctionList(request)})
    #----------------------------------------------
    elif page=="pieChart":
        id,dataset_nodes1, dataset_edges1, numHits1 = graphV_dataset(100,term)
        id,dataset_nodes2, dataset_edges2, numHits2 = graphV_webSearch(id,term)
        id,dataset_nodes3, dataset_edges3, numHits3 = graphV_webAPI(id,term)

        sum= (numHits1+numHits2+numHits3)+1

        dataPoints=[
            {'y': numHits2/sum*100 , 'label': 'Webpages'},
            {'y': numHits1/sum*100 , 'label': 'Dataset'},
            {'y': numHits3/sum*100 , 'label': 'Web APIs'}
        ]

        return render(request,'pieChart.html',{
                                               "searchTerm":term,
                                               "dataPoints":json.dumps(dataPoints),
                                                "functionList": getAllfunctionList(request)
                                               })
    #----------------------------------------------
    elif page=="graphV":
        try:
            Query["label"]="Query: " + term
            id,dataset_nodes1, dataset_edges1, numHits1 = graphV_dataset(100,term)
            id,dataset_nodes2, dataset_edges2, numHits2 = graphV_webSearch(id,term)
            id,dataset_nodes3, dataset_edges3, numHits3 = graphV_webAPI(id,term)

            dataset_nodes4=mergeList(dataset_nodes1,dataset_nodes2)
            dataset_edges4=mergeList(dataset_edges1,dataset_edges2)

            dataset_nodes=mergeList(dataset_nodes3,dataset_nodes4)
            dataset_edges=mergeList(dataset_edges3,dataset_edges4)

            return render(request,'graphV.html',{
                "dataset_nodes":json.dumps(dataset_nodes),
                "dataset_edges":json.dumps(dataset_edges),
                "searchTerm":term,
                "functionList": getAllfunctionList(request)
            })

        except:
            searchValue = ''
    #----------------------------------------------
    elif page=="home":
        request.session['filters']=[]
        return render(request,'landingpage.html',{"searchTerm":term,  "functionList": getAllfunctionList(request)})

#---------------------------------------------------------------------------------------------------------------------
def getResearchInfrastructure(url):
    lstRI=[]
    for RI in ResearchInfrastructures:
        if RI in url:
            if(ResearchInfrastructures2[RI]['acronym'] not in lstRI):
                lstRI.append(ResearchInfrastructures2[RI]['acronym'])
    return lstRI
#---------------------------------------------------------------------------------------------------------------------
Query={
    'id': 0,
    'url':'N/A',
    'widthConstraint': { 'maximum': 150,'minimum': 100  },
    'heightConstraint': { 'minimum': 70, 'maximum': 100 },
    'label': '',
    'x': -150,
    'y': -150,
    'shape': "box",
}

ResearchInfrastructures2={
    'icos-cp.eu': {
        'id': 1,
        'url':'https://www.icos-cp.eu/',
        'label': 'Multi-domain',
        'title': 'Integrated Carbon Observation System',
        'acronym':'ICOS'
    },
    'seadatanet.org': {
        'id': 2,
        'url':'https://www.seadatanet.org/',
        'label': 'Marine',
        'title': 'Pan-European infrastructure for ocean and marine data management',
        'acronym':'SeaDataNet'
    },
    'lifewatch.eu': {
        'id': 3,
        'url':'https://www.lifewatch.eu/',
        'label': 'Multi-domain',
        'title': 'An e-Infrastructure for basic research on biodiversity and ecosystems',
        'acronym':'LifeWatch'
    },
    'anaee.eu':{
        'id': 4,
        'url':'https://www.anaee.eu/',
        'label': 'Terrestrial ecosystem / Biodiversity',
        'title': 'Analysis and Experimentation on Ecosystems',
        'acronym':'AnaEE'
    },
    'actris.eu':{
        'id': 5,
        'url':'https://www.actris.eu/',
        'label': 'Atmospheric',
        'title': 'The Aerosol, Clouds and Trace Gases Research Infrastructure',
        'acronym':'ACTRIS'
    },
    'aquacosm.eu':{
        'id': 6,
        'url':'https://www.aquacosm.eu/',
        'label': 'Marine / Freshwater',
        'title': 'EU network of mesocosms facilities for research on marine and freshwater',
        'acronym':'AQUACOSM'
    },
    'arise-project.eu':{
        'id': 7,
        'url':'http://arise-project.eu/',
        'label': 'Atmosphere',
        'title': 'Atmospheric dynamics Research InfraStructure in Europe',
        'acronym':'ARISE'
    },
    'danubius-pp.eu':{
        'id': 8,
        'url':'https://danubius-pp.eu/',
        'label': 'River / Marine',
        'title': 'Preparatory Phase For The Paneuropean Research Infrastructure',
        'acronym':'DANUBIUS-RI'
    },
    'dissco.eu':{
        'id': 9,
        'url':'https://www.dissco.eu/',
        'label': 'Terrestrial ecosystem / Biodiversity',
        'title': 'Distributed System of Scientific Collections',
        'acronym':'DiSSCo'
    },
    'eiscat.se':{
        'id': 10,
        'url':'https://eiscat.se/',
        'label': 'Atmospheric',
        'title': 'EISCAT Scientific Association',
        'acronym':'EISCAT 3D'
    },
    'elter-ri.eu':{
        'id': 11,
        'url':'https://www.elter-ri.eu/',
        'label': 'Biodiversity / Ecosystems',
        'title': 'Long-Term Ecosystem Research in Europe',
        'acronym':'eLTER RI'
    },
    'embrc.eu':{
        'id': 12,
        'url':'https://www.embrc.eu/',
        'label': 'Marine / Biodiversity',
        'title': 'Long-Term Ecosystem Research in Europe',
        'acronym':'EMBRC'
    },
    'emso.eu':{
        'id': 13,
        'url':'https://emso.eu/',
        'label': 'Multi-domain',
        'title': 'European Multidisciplinary Seafloor and water column Observatory',
        'acronym':'EMSO'
    },
    'emphasis.plant-phenotyping.eu':{
        'id': 14,
        'url':'https://emphasis.plant-phenotyping.eu/',
        'label': 'Terrestrial Ecosystem',
        'title': 'European Infrastructure for Plant Phenotyping',
        'acronym':'EMPHASIS'
    },
    'epos-eu.org':{
        'id': 15,
        'url':'https://www.epos-eu.org/',
        'label': 'Solid Earth Science',
        'title': 'European Plate Observing System',
        'acronym':'EPOS'
    },
    'eufar.net':{
        'id': 16,
        'url':'https://www.eufar.net/',
        'label': 'Atmospheric',
        'title': 'The EUropean Facility for Airborne Research',
        'acronym':'EUFAR'
    },
    'euro-argo.eu':{
        'id': 17,
        'url':'https://www.euro-argo.eu/',
        'label': 'Marine',
        'title': 'European Research Infrastructure Consortium for observing the Ocean',
        'acronym':'Euro-Argo ERIC'
    },
    'eurofleet.fr':{
        'id': 18,
        'url':'https://www.eurofleet.fr/',
        'label': 'Marine',
        'title': 'An alliance of European marine research infrastructure to meet the evolving needs of the research and industrial communities',
        'acronym':'EUROFLEETS+'
    },
    'eurogoos.eu':{
        'id': 19,
        'url':'https://eurogoos.eu/',
        'label': 'Marine',
        'title': 'European Global Ocean Observing System',
        'acronym':'EuroGOOS'
    },
    'eurochamp.org':{
        'id': 20,
        'url':'https://www.eurochamp.org/',
        'label': 'Atmospheric',
        'title': 'Integration of European Simulation Chambers for Investigating Atmospheric Processes',
        'acronym':'EUROCHAMP'
    },
    'hemera-h2020.eu':{
        'id': 21,
        'url':'https://www.hemera-h2020.eu/',
        'label': 'Atmospheric',
        'title': 'Integrated access to balloon-borne platforms for innovative research and technology',
        'acronym':'HEMERA'
    },
    'iagos.org':{
        'id': 22,
        'url':'https://www.iagos.org/',
        'label': 'Atmospheric',
        'title': 'In Service Aircraft for a Global Observing System',
        'acronym':'IAGOS'
    },
    'eu-interact.org':{
        'id': 23,
        'url':'https://eu-interact.org/',
        'label': 'Terrestrial Ecosystem',
        'title': 'Building Capacity For Environmental Research And Monitoring In Arctic And Neighbouring Alpine And Forest Areas',
        'acronym':'INTERACT'
    },
    'is.enes.org':{
        'id': 24,
        'url':'https://is.enes.org/',
        'label': 'Multi-domain',
        'title': 'Infrastructure For The European Network For Earth System Modelling Enes',
        'acronym':'IS-ENES'
    },
    'jerico-ri.eu':{
        'id': 25,
        'url':'https://www.jerico-ri.eu/',
        'label': 'Marine',
        'title': 'The European Integrated Infrastructure For In Situ Coastal Observation',
        'acronym':'JERICO-RI'
    },
    'sios-svalbard.org':{
        'id': 26,
        'url':'https://www.sios-svalbard.org/',
        'title': 'Multi-domain',
        'title': 'Svalbard integrated Earth observing system',
        'acronym':'SIOS'
    }
}



ResearchInfrastructures={
    'icos-cp.eu': {
        'id': 1,
        'url':'https://www.icos-cp.eu/',
        'label': 'Multi-domain',
        'title': 'Integrated Carbon Observation System',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/ICOS.jpg",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':20,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'seadatanet.org': {
        'id': 2,
        'url':'https://www.seadatanet.org/',
        'label': 'Marine',
        'title': 'Pan-European infrastructure for ocean and marine data management',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/SeaDataNet.jpg",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':35,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'lifewatch.eu': {
        'id': 3,
        'url':'https://www.lifewatch.eu/',
        'label': 'Multi-domain',
        'title': 'An e-Infrastructure for basic research on biodiversity and ecosystems',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/LifeWatchERIC.png",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':30,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'anaee.eu':{
        'id': 4,
        'url':'https://www.anaee.eu/',
        'label': 'Terrestrial ecosystem / Biodiversity',
        'title': 'Analysis and Experimentation on Ecosystems',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/anaee.png",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':30,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'actris.eu':{
        'id': 5,
        'url':'https://www.actris.eu/',
        'label': 'Atmospheric',
        'title': 'The Aerosol, Clouds and Trace Gases Research Infrastructure',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/actris.png",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':30,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'aquacosm.eu':{
        'id': 6,
        'url':'https://www.aquacosm.eu/',
        'label': 'Marine / Freshwater',
        'title': 'EU network of mesocosms facilities for research on marine and freshwater',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/AQUACOSM.png",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':40,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'arise-project.eu':{
        'id': 7,
        'url':'http://arise-project.eu/',
        'label': 'Atmosphere',
        'title': 'Atmospheric dynamics Research InfraStructure in Europe',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/arise.jpg",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':30,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'danubius-pp.eu':{
        'id': 8,
        'url':'https://danubius-pp.eu/',
        'label': 'River / Marine',
        'title': 'Preparatory Phase For The Paneuropean Research Infrastructure',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/DANUBIUS-RI.png",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':40,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'dissco.eu':{
        'id': 9,
        'url':'https://www.dissco.eu/',
        'label': 'Terrestrial ecosystem / Biodiversity',
        'title': 'Distributed System of Scientific Collections',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/Dissco.png",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':30,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'eiscat.se':{
        'id': 10,
        'url':'https://eiscat.se/',
        'label': 'Atmospheric',
        'title': 'EISCAT Scientific Association',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/EISCAT3D.png",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':20,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'elter-ri.eu':{
        'id': 11,
        'url':'https://www.elter-ri.eu/',
        'label': 'Biodiversity / Ecosystems',
        'title': 'Long-Term Ecosystem Research in Europe',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/elterRI.png",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':20,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'embrc.eu':{
        'id': 12,
        'url':'https://www.embrc.eu/',
        'label': 'Marine / Biodiversity',
        'title': 'Long-Term Ecosystem Research in Europe',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/EMBRC.png",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':35,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'emso.eu':{
        'id': 13,
        'url':'https://emso.eu/',
        'label': 'Multi-domain',
        'title': 'European Multidisciplinary Seafloor and water column Observatory',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/EMSOERIC.png",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':35,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'emphasis.plant-phenotyping.eu':{
        'id': 14,
        'url':'https://emphasis.plant-phenotyping.eu/',
        'label': 'Terrestrial Ecosystem',
        'title': 'European Infrastructure for Plant Phenotyping',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/EMPHASIS.png",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':12,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'epos-eu.org':{
        'id': 15,
        'url':'https://www.epos-eu.org/',
        'label': 'Solid Earth Science',
        'title': 'European Plate Observing System',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/EPOS.png",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':25,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'eufar.net':{
        'id': 16,
        'url':'https://www.eufar.net/',
        'label': 'Atmospheric',
        'title': 'The EUropean Facility for Airborne Research',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/EUFAR.jpg",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':35,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'euro-argo.eu':{
        'id': 17,
        'url':'https://www.euro-argo.eu/',
        'label': 'Marine',
        'title': 'European Research Infrastructure Consortium for observing the Ocean',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/euroArgo.png",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':40,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'eurofleet.fr':{
        'id': 18,
        'url':'https://www.eurofleet.fr/',
        'label': 'Marine',
        'title': 'An alliance of European marine research infrastructure to meet the evolving needs of the research and industrial communities',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/Eurofleets.jpg",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':20,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'eurogoos.eu':{
        'id': 19,
        'url':'https://eurogoos.eu/',
        'label': 'Marine',
        'title': 'European Global Ocean Observing System',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/EuroGOOS.png",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':30,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'eurochamp.org':{
        'id': 20,
        'url':'https://www.eurochamp.org/',
        'label': 'Atmospheric',
        'title': 'Integration of European Simulation Chambers for Investigating Atmospheric Processes',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/EUROCHAMP.png",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':30,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'hemera-h2020.eu':{
        'id': 21,
        'url':'https://www.hemera-h2020.eu/',
        'label': 'Atmospheric',
        'title': 'Integrated access to balloon-borne platforms for innovative research and technology',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/HEMERA.jpg",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':40,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'iagos.org':{
        'id': 22,
        'url':'https://www.iagos.org/',
        'label': 'Atmospheric',
        'title': 'In Service Aircraft for a Global Observing System',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/IAGOSERI.png",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':20,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'eu-interact.org':{
        'id': 23,
        'url':'https://eu-interact.org/',
        'label': 'Terrestrial Ecosystem',
        'title': 'Building Capacity For Environmental Research And Monitoring In Arctic And Neighbouring Alpine And Forest Areas',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/INTERACT.jpg",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':30,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'is.enes.org':{
        'id': 24,
        'url':'https://is.enes.org/',
        'label': 'Multi-domain',
        'title': 'Infrastructure For The European Network For Earth System Modelling Enes',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/ISENES.png",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':30,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'jerico-ri.eu':{
        'id': 25,
        'url':'https://www.jerico-ri.eu/',
        'label': 'Marine',
        'title': 'The European Integrated Infrastructure For In Situ Coastal Observation',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/JERICO.jpg",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':30,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'sios-svalbard.org':{
        'id': 26,
        'url':'https://www.sios-svalbard.org/',
        'label': 'Multi-domain',
        'title': 'Svalbard integrated Earth observing system',
        'shape': 'image',
        'image': "/static/images/ENVRI-Collection/RIs-graph/sios.png",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':35,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    },
    'KB':{
        'id': 27,
        'url':'',
        'label': 'Knowledge Base',
        'title': 'Multi-domain',
        'shape': 'image',
        'image': "/static/images/knowledge_base_icon.png",
        'imagePadding': { 'left': 2, 'top': 2, 'right': 2, 'bottom': 2 },
        'size':35,
        'color': {
            'border': '#406897',
            'background': 'white',
        },
    }
}
#---------------------------------------------------------------------------------------------------------------------
def detectRI(url):
    for RI in ResearchInfrastructures:
        for r in url:
            if RI in r:
                return RI
    return 'KB'
#---------------------------------------------------------------------------------------------------------------------
def createNode(id, caption, url, tooltip, img, size=12):
    cap=""
    for c in caption:
        if cap!="":
            cap= cap+" . "+c
        else:
            cap=c

    tool=""
    for t in tooltip:
        if tool!="":
            tool= tool+" . "+t
        else:
            tool=t

    newNode={
        'id': id,
        'url': url.replace('json',''),
        'label': cap[:30] + (cap[30:] and '...'),
        'title': tool[:100]  + (tool[100:] and '...'),
        'shape': 'image',
        'image': img,
        'size':size,
    }
    return newNode
#---------------------------------------------------------------------------------------------------------------------
def createEdge(from_node_id, to_node_id):
    Newedge={'from': from_node_id, 'to': to_node_id, 'title': '' }
    return Newedge
#---------------------------------------------------------------------------------------------------------------------
def graphV_dataset(id,searchValue):

    user_request = "some_param"
    query_body = {
        "from" : 0,
        "size" : 100,
        "query": {
            "bool": {
                "must": {
                    "multi_match" : {
                        "query": searchValue,
                        "fields": [ "description", "keywords", "contact", "publisher", "citation",
                                    "genre", "creator", "headline", "abstract", "theme", "producer", "author",
                                    "sponsor", "provider", "name", "measurementTechnique", "maintainer", "editor",
                                    "copyrightHolder", "contributor", "contentLocation", "about", "rights", "useConstraints",
                                    "status", "scope", "metadataProfile", "metadataIdentifier", "distributionInfo", "dataQualityInfo",
                                    "contentInfo", "ResearchInfrastructure", "EssentialVariables", "potentialTopics"],
                        "type": "best_fields",
                        "minimum_should_match": "50%"
                    }
                },
            }
        },
    }

    result = es.search(index="envri", body=query_body)
    numHits=result['hits']['total']['value']

    lstDataset= {}
    lstAddedRIs=[]
    nodes=[]
    edges=[]
    nodes.append(Query)

    for searchResult in result['hits']['hits']:
        result= searchResult['_source']
        RI=detectRI(result['url'])

        url=result['url'][0]
        caption=result['description']
        tooltip=result['name']
        id=id+1
        img="/static/images/dataset.png"

        if RI not in lstAddedRIs:
            lstAddedRIs.append(RI)
            nodes.append(ResearchInfrastructures[RI])
            edges.append(createEdge(Query['id'], ResearchInfrastructures[RI]['id']))
            nodes.append(createNode(id, ['Datasets'], ResearchInfrastructures[RI]['url'], ['Datasets'], "/static/images/datasetCollectionlogo.png",30))
            lstDataset[RI]=id
            edges.append(createEdge(ResearchInfrastructures[RI]['id'], lstDataset[RI]))
            id=id+1

        nodes.append(createNode(id, caption, url, tooltip,img))
        edges.append(createEdge(lstDataset[RI],id))

    return id,nodes,edges,numHits
#---------------------------------------------------------------------------------------------------------------------
def graphV_webSearch(id,searchValue):

    user_request = "some_param"
    query_body = {
        "from" : 0,
        "size" : 100,
        "query": {
            "bool": {
                "must": {
                    "multi_match" : {
                        "query": searchValue,
                        "fields": [ "title", "pageContetnts", "organizations", "topics",
                                    "people", "workOfArt", "files", "locations", "dates",
                                    "researchInfrastructure"],
                        "type": "best_fields",
                        "minimum_should_match": "50%"
                    }
                },
            }
        },
    }

    result = es.search(index="webcontents", body=query_body)
    numHits=result['hits']['total']['value']

    lstWebpages= {}
    lstAddedRIs=[]
    nodes=[]
    edges=[]
    nodes.append(Query)

    for searchResult in result['hits']['hits']:

        result= searchResult['_source']
        RI=detectRI(result['url'])

        url=result['url'][0]
        caption=result['title']
        tooltip=result['pageContetnts']
        id=id+1
        img="/static/images/webpageslogo.png"

        if RI not in lstAddedRIs:
            lstAddedRIs.append(RI)
            nodes.append(ResearchInfrastructures[RI])
            edges.append(createEdge(Query['id'], ResearchInfrastructures[RI]['id']))
            nodes.append(createNode(id, ['Webpages'], ResearchInfrastructures[RI]['url'], ['Webpages'], "/static/images/websitelogo.png",30))
            lstWebpages[RI]=id
            edges.append(createEdge(ResearchInfrastructures[RI]['id'], lstWebpages[RI]))
            id=id+1

        nodes.append(createNode(id, caption, url, tooltip,img))
        edges.append(createEdge(lstWebpages[RI],id))

    return id,nodes,edges,numHits
#---------------------------------------------------------------------------------------------------------------------
def graphV_webAPI(id,searchValue):

    user_request = "some_param"
    query_body = {
        "from" : 0,
        "size" : 100,
        "query": {
            "bool": {
                "must": {
                    "multi_match" : {
                        "query": searchValue,
                        "fields": [ "name", "description", "category", "provider", "serviceType", "architecturalStyle"],
                        "type": "best_fields",
                        "minimum_should_match": "50%"
                    }
                },
            }
        },
    }

    result = es.search(index="webapi", body=query_body)
    numHits=result['hits']['total']['value']

    lstWebAPIs= {}
    lstAddedRIs=[]
    nodes=[]
    edges=[]
    nodes.append(Query)

    for searchResult in result['hits']['hits']:
        result= searchResult['_source']
        RI=detectRI(result['url'])
        url=result['url'][0]
        caption=result['name']
        tooltip=result['description']
        id=id+1
        img="/static/images/webapilogo.jpg"

        if RI not in lstAddedRIs:
            lstAddedRIs.append(RI)
            nodes.append(ResearchInfrastructures[RI])
            edges.append(createEdge(Query['id'], ResearchInfrastructures[RI]['id']))
            nodes.append(createNode(id, ['Web API'], ResearchInfrastructures[RI]['url'], ['Web API'], "/static/images/WebAPIsLogo.png",30))
            lstWebAPIs[RI]=id
            edges.append(createEdge(ResearchInfrastructures[RI]['id'], lstWebAPIs[RI]))
            id=id+1

        nodes.append(createNode(id, caption, url, tooltip,img))
        edges.append(createEdge(lstWebAPIs[RI],id))


    return id,nodes,edges,numHits
#-----------------------------------------------------------------------------------------------------------------------
def getAllfunctionList(request):
    if not 'BasketURLs' in request.session or not request.session['BasketURLs']:
        request.session['BasketURLs'] = []
    if not 'MyBasket' in request.session or not request.session['MyBasket']:
        request.session['MyBasket'] = []

    functionList=""
    saved_list = request.session['MyBasket']
    for item in saved_list:
        functionList= functionList+r"modifyCart({'operation':'add','type':'"+item['type']+"','title':'"+item['title']+"','url':'"+item['url']+"','id':'"+item['id']+"' });"
    return functionList