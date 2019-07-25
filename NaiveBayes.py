import tkinter as tk
from tkinter import Tk, Label, Button, Entry, END, W, E, messagebox, StringVar, Canvas, NW, S, N, Listbox, MULTIPLE, \
    DISABLED
from tkinter.filedialog import askdirectory
import os
import pandas as pd


class GUI:

    def __init__(self, master):
        self.master = master
        master.title("Naive Bayes Classifier")

        # Members
        self.directory_path = ""
        self.discretization_bins = 1
        self.structure_path = ""
        self.train_path = ""
        self.test_path = ""
        # self.model

        # Labels
        self.directory_path_label = Label(master, text="Directory Path:")
        self.discretization_bins_label = Label(master, text="Discretization Bins:")

        # Vars
        self.directory_path_text = StringVar()
        self.directory_path_text.trace("w", lambda name, index, mode, sv=self.directory_path_text: self.check_path(sv))

        # Entries
        self.directory_path_entry = Entry(master, textvariable=self.directory_path_text, width=50)
        self.discretization_bins_entry = IntEntry(master, width=10)
        self.discretization_bins_entry.set('1')

        # Buttons
        self.browse_button = Button(master, text="Browse", command=lambda: self.browse())
        self.build_button = Button(master, text="Build", state=DISABLED, command=lambda: self.build(), width=20)
        self.classify_button = Button(master, text="Classify", state=DISABLED, command=lambda: self.classify(), width=20)

        # LAYOUT
        self.directory_path_label.grid(row=0, column=0, padx=10, pady=10, sticky=E)
        self.directory_path_entry.grid(row=0, column=1, padx=10, pady=10)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)
        self.discretization_bins_label.grid(row=1, column=0, sticky=E, padx=10, pady=10)
        self.discretization_bins_entry.grid(row=1, column=1, sticky=W, padx=10, pady=10)
        self.build_button.grid(row=2, column=0, columnspan=3,  padx=10, pady=10)
        self.classify_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    def browse(self):
        entry = self.directory_path_entry
        path = askdirectory()
        if path != '':
            entry.delete(0, END)
            entry.insert(0, path)

    def check_path(self, sv):
        if sv.get() != '':
            self.build_button['state'] = 'normal'
        else:
            self.build_button['state'] = 'disabled'
        self.classify_button['state'] = 'disabled'

    def build(self):

        # save variables
        self.directory_path = self.directory_path_entry.get()
        if self.discretization_bins_entry.get() == '':
            self.discretization_bins_entry.set('1')
        self.discretization_bins = int(self.discretization_bins_entry.get())

        # reset paths
        self.structure_path = ""
        self.train_path = ""
        self.test_path = ""

        # look for required files
        for root_path, dirnames, filenames in os.walk(self.directory_path):
            for filename in filenames:
                if filename == 'Structure.txt':
                    if self.structure_path != '':
                        messagebox.showerror("Naive Bayes Classifier", "more than one Structure.txt in directory")
                        return
                    else:
                        self.structure_path = root_path+'\\'+filename
                elif filename == 'train.csv':
                    if self.train_path != '':
                        messagebox.showerror("Naive Bayes Classifier", "more than one train.csv in directory")
                        return
                    else:
                        self.train_path = root_path+'\\'+filename
                elif filename == 'test.csv':
                    if self.test_path != '':
                        messagebox.showerror("Naive Bayes Classifier", "more than one test.csv in directory")
                        return
                    else:
                        self.test_path = root_path+'\\'+filename

        # check that all files were found
        if self.structure_path == '':
            messagebox.showerror("Naive Bayes Classifier", "Structure.txt not found")
            return
        if self.train_path == '':
            messagebox.showerror("Naive Bayes Classifier", "train.csv not found")
            return
        if self.test_path == '':
            messagebox.showerror("Naive Bayes Classifier", "test.csv not found")
            return

        self.build_model()

    def build_model(self):
        try:
            dfStructure = readStructure(self.structure_path)
            df = readDataSet(self.train_path)
            fillMissingValues(df, dfStructure)
            discretization(df, dfStructure, int(self.discretization_bins_entry.get()))
            self.model = buildModel(df, dfStructure)
            messagebox.showinfo("Naive Bayes Classifier", "Building classifier using train-set is done!")
            # self.build_button['state'] = 'disabled'
            self.classify_button['state'] = 'normal'
        except:
            messagebox.showerror("Naive Bayes Classifier", "There is an error in the format of one of the files")

    def classify(self):
        try:
            dfStructure = readStructure(self.structure_path)
            testdf = readDataSet(self.test_path)
            fillMissingValues(testdf, dfStructure)
            discretization(testdf, dfStructure, self.discretization_bins)
            predictions = predictTestFile(self.model, testdf, dfStructure)
            with open(self.directory_path+'\\output.txt', 'w') as output_file:
                for i in predictions:
                    line = str(i+1)+' '+predictions[i]
                    print(line)
                    output_file.write(line+'\n')
            messagebox.showinfo("Naive Bayes Classifier", "Classification completed!")
        except:
            messagebox.showerror("Naive Bayes Classifier", "There is an error in the format of test.csv")


class IntEntry(tk.Entry):
    def __init__(self, master=None, **kwargs):
        self.var = tk.StringVar()
        tk.Entry.__init__(self, master, textvariable=self.var, **kwargs)
        self.old_value = ''
        self.var.trace('w', self.validate)
        self.get, self.set = self.var.get, self.var.set

    def validate(self, *args):
        if self.get() == '' or self.get().isdigit():
            if self.get().isdigit() and self.get()[0] == '0':
                self.set(self.old_value)
            else:
                self.old_value = self.get()
        else:
            self.set(self.old_value)

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

root = Tk()
my_gui = GUI(root)
root.mainloop()
