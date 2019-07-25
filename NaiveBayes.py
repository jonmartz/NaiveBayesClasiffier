import numpy as np
import pandas as pd


def stringToListOfValues(stringToParse):
    """
    gets the values string and return in list format
    :param stringToParse: string of values
    :return: list of values
    """
    listofValues = stringToParse.split(',')
    return listofValues


def readStructure(pathToStructureFile):
    """
    read the structure file and proccess it into a dictionary
    :param pathToStructureFile: path to the structure file
    :return: dictionary of the feature name and their optional values
    """
    fields = {}
    structureFile = open(pathToStructureFile, "r")
    dataStructure = structureFile.read().split('\n')
    for att in dataStructure:
        splited = att.split(" ")
        attName = splited[1]
        attValues = splited[2]
        if attValues == 'NUMERIC':
            fields[attName] = attValues
        else:
            if attValues[0] == '{' and attValues[len(attValues) - 1] == '}':
                fields[attName] = stringToListOfValues(attValues[1:len(attValues) - 1])
    return fields


def readDataSet(pathToDataSet):
    """
    reading the csv dataset and return it
    :param pathToDataSet: path to the dataset
    :return: the dataset in pandas dataframe
    """
    return pd.read_csv(pathToDataSet)


def discretization(datasetDF, fieldsStructure, numOfBins):
    labelsForDiscrite = []
    for i in range(1, numOfBins + 1):
        labelsForDiscrite.append(str(i))

    for field in fieldsStructure:
        if fieldsStructure[field] == 'NUMERIC':
            datasetDF[field] = pd.cut(datasetDF[field], numOfBins, labels=labelsForDiscrite)
            fieldsStructure[field] = labelsForDiscrite


def fillMissingValues(datasetDF, fieldsStructure):
    for field in fieldsStructure:
        if fieldsStructure[field] == 'NUMERIC':
            datasetDF[field] = datasetDF.groupby("class")[field].transform(lambda x: x.fillna(x.mean()))
        else:
            mostCommon = datasetDF[field].mode(dropna=True)[0]
            datasetDF[field].fillna(mostCommon, inplace=True)


def buildModel(trainCleanDF, fieldsStructure):
    mfeatures = {}
    for feature in fieldsStructure:
        if feature != 'class':
            fieldDict = {}
            for pVal in fieldsStructure[feature]:
                pvalDict = {}
                for c in fieldsStructure['class']:
                    tempFilter = trainCleanDF.loc[trainCleanDF['class'] == c]
                    pvalDict[c] = len(tempFilter.loc[tempFilter[feature] == pVal])
                fieldDict[pVal] = pvalDict
            mfeatures[feature] = fieldDict

    mclasses = {}
    totalRecords = len(trainCleanDF)
    for c in fieldsStructure['class']:
        countClass = len(trainCleanDF.loc[trainCleanDF['class'] == c])
        prob = float(countClass) / float(totalRecords)
        mclasses[c] = [prob, countClass]
    return [mfeatures, mclasses]


def predictTestFile(NaiveBayesModel, testDataFrame, fieldsStructure):
    predictionsDict = {}
    for i,row in enumerate(testDataFrame.iterrows()):
        maxClass = ''
        maxClassVal = 0
        for c in fieldsStructure['class']:
            classVal = 1.0
            for f in fieldsStructure.keys():
                if f != 'class':
                    classVal = classVal * (float(NaiveBayesModel[0][f][row[1][f]][c] + (2/ len(fieldsStructure[f])))/float((NaiveBayesModel[1][c][1] + 2)))
            classVal = classVal * NaiveBayesModel[1][c][0]
            if classVal > maxClassVal:
                maxClass = c
                maxClassVal = classVal
        predictionsDict[i] = maxClass
    return predictionsDict





dfStructure = readStructure("C:\\Users\\odedblu\\Desktop\\Structure.txt")
df = readDataSet("C:\\Users\\odedblu\\Desktop\\train.csv")
fillMissingValues(df, dfStructure)
discretization(df, dfStructure, 6)
model = buildModel(df, dfStructure)
dfStructure = readStructure("C:\\Users\\odedblu\\Desktop\\Structure.txt")
testdf = readDataSet("C:\\Users\\odedblu\\Desktop\\test.csv")
fillMissingValues(testdf, dfStructure)
discretization(testdf, dfStructure, 6)
predictions = predictTestFile(model, testdf, dfStructure)
for i in predictions:
    print(predictions[i])