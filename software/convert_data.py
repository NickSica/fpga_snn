#!/usr/bin/python3

import os

import pandas as pd
import wfdb

baseDir = os.getcwd()
outputDir = os.path.join(baseDir, "data")
rawDir = os.path.join(outputDir, "raw")
headDir = os.path.join(outputDir, "head")
testFile = os.path.join(headDir,"test.csv")
trainFile = os.path.join(headDir,"train.csv")

def convert_data(csv_file, output_name):
    trainData = pd.read_csv(csv_file)
    patients = pd.DataFrame(columns=trainData.columns)
    for i,row in trainData.iterrows():
        try:
            recordname = os.path.join(rawDir, row['Record'])
            train0Head = wfdb.rdrecord(recordname)
            annotation0 = wfdb.rdann(recordname, extension="apn")
            wfdb.mit2edf(recordname,output_filename=os.path.join(outputDir, row['Record']+".edf"))
            annodf = pd.DataFrame()


            annodf['onset'] = annotation0.sample/100.00
            annodf['duration'] = 60
            annodf['description'] = annotation0.symbol
            annodf.to_csv(os.path.join(outputDir, row['Record']+".txt"),index=False, header=False)
            patients.loc[i] = row.tolist()
        except:
            continue

    patients.to_csv(os.path.join(outputDir, output_name+".csv"),index=False)

if __name__ == "__main__":
    convert_data(trainFile, "TrainRecords")
    convert_data(testFile, "TestRecords")
