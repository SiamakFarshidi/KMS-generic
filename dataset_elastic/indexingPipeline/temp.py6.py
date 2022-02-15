def metadataRecord_similarity_evaluation(filename, drivedFields, originalFields, SetOfValues):
    similarityDic={}
    ScoreSim={}
    lstOriginalValues=[]
    lstdrivedValues=[]
    dataset_content = open(filename,"r")
    dataset_object = json.loads(dataset_content.read())
    TP=[]
    FP=[]
    FN=[]
    TN=[]
    for drivedfield in drivedFields:
        for originalField in originalFields:
            for subDrivedField in dataset_object[drivedfield]:
                for subOriginalField in dataset_object[originalField]:
                    simScore=get_jaccard_sim(subDrivedField,subOriginalField)

                    if subOriginalField not in lstOriginalValues:
                        lstOriginalValues.append(subOriginalField)
                    if subDrivedField not in lstdrivedValues:
                        lstdrivedValues.append(subDrivedField)

                    if subDrivedField not in similarityDic.keys():
                        similarityDic[subDrivedField]=[]

                    similarityDic[subDrivedField].append(simScore)
    cntTruePositive=0
    for key in similarityDic:
        sum=0
        for val in similarityDic[key]:
            sum=sum + val
        avg=sum/len(similarityDic[key])
        similarityDic[key].clear()

        inContext=False
        if avg>0:
            cntTruePositive=cntTruePositive+1
            inContext=True
        similarityDic[key].append(inContext)
    Precision=0
    if len(similarityDic)>0:
        Precision= (cntTruePositive)/len(similarityDic) *100

    FN=getFalseNegative(lstdrivedValues, lstOriginalValues, SetOfValues)

    return similarityDic, Precision
