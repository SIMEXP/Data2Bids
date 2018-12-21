#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 11:55:12 2018

@author: ltetrel
"""
import os
import re
import shutil
import json

"""
https://github.com/MounaSafiHarab/Loris-MRI/blob/9b7c299006378d54c9b457d8e1c1a3c71eaf4176/tools/MakeNiiFilesBIDSCompliant.pl
"""

class cDataType:
    
    def __init__(self):
        self.anat = str(None)
        self.func = str(None)
        self.dwi = str(None)
        self.map = str(None)
        self.meg = str(None)
        
    def __repr__(self):
        return "anat :\n\t" + self.anat + '\n'\
        + "func :\n\t" + self.func + '\n'\
        + "dwi :\n\t" + self.dwi + '\n'\
        + "map :\n\t" + self.map + '\n'\
        + "meg :\n\t" + self.meg
    
    def __str__(self):
        return "anat :\n\t" + self.anat + '\n'\
        + "func :\n\t" + self.func + '\n'\
        + "dwi :\n\t" + self.dwi + '\n'\
        + "map :\n\t" + self.map + '\n'\
        + "meg :\n\t" + self.meg

class cAnatModalityLabel:
    
    def __init__(self):
        self.T1w = str(None)
        self.T2w = str(None)
        self.T1rho = str(None)
        self.T1map = str(None)
        self.T2map = str(None)
        self.T2star = str(None)
        self.FLAIR = str(None)
        self.FLASH = str(None)
        self.PD = str(None)
        self.PDmap = str(None)
        self.FLASH = str(None)
        self.PDT2 = str(None)
        self.inplaneT1 = str(None)
        self.inplaneT2 = str(None)
        self.angio = str(None)

def main():
    pathDir = "/home/ltetrel/Documents/data/testPreventAD"
    datasetName = os.path.basename(pathDir)
    bidsVersion = "1.1.1"
    
    dataType = cDataType()
#   According to  https://bids.neuroimaging.io/bids_spec.pdf
    
    # option delimiter, before and after every groups
    delimiter = '_'
    
    dataType.anat = list(["adniT1"])
    dataType.func = list(["Resting"])
    
    # session label : how much visits the patient attende
    sessLabel = list(["BL00", "EN00", "FU03", "FU12", "FU24", "FU36", "FU48"])
    
    # task label for fmri, including resting state, TO ADD
    taskLabel = None
    
    # run number
    runIndex = "[0-9]{3}"
    
    #patient-id, with regexp 4 times
    partLabel = "[0-9]{6}"
    
    # creating the output dir
    outDir = os.path.dirname(pathDir) + '/' + datasetName + "_BIDS"
    if os.path.exists(outDir):
        os.system("rm -r " + outDir + "/*")
    else:
        os.makedirs(outDir)
        
    
    #Must be included in the folder root foolowing BIDS specs
    
    with open(outDir + "/dataset_description.json", 'w') as fst:
        data = {'Name': datasetName,
                'BIDSVersion': bidsVersion}
        json.dump(data, fst, ensure_ascii=False)
    
    # now we can scan all files and rearrange them
    for root,_,_ in os.walk(pathDir): 
        for file in os.listdir(root): 
            srcFilePath = os.path.join(root, file)
            dstFilePath = outDir
            
            # Matching the participent number
            if re.match(".*?" + delimiter + '(' + partLabel + ')' + delimiter + ".*?", file):
                partMatch = re.match(".*?" + delimiter + '(' + partLabel + ')' + delimiter + ".*?", file)[1]
                dstFilePath = dstFilePath + "/sub-" + partMatch
            
            # Matching the session label
            for toMatch in sessLabel:
                if re.match(".*?" + delimiter + ".*?" + '(' + toMatch + ')' + delimiter + ".*?", file):
                    sessMatch = re.match(".*?" + delimiter + ".*?" + '(' + toMatch + ')' + delimiter + ".*?", file)[1]
                    dstFilePath = dstFilePath + "/ses-" + sessMatch
                else:
                    continue
            
            # Matching the data type
            for toMatch in dataType.anat:
                if re.match(".*?" + delimiter + '(' + toMatch + ')' + delimiter + ".*?", file):
                    dataTypeMatch = "T1w"
                    dstFilePath = dstFilePath + "/anat"
                else:
                    continue
            
            for toMatch in dataType.func:
                if re.match(".*?" + delimiter + '(' + toMatch + ')' + delimiter + ".*?", file):
                    dataTypeMatch = "bold"
                    dstFilePath = dstFilePath + "/func"
                #### Here the part for resting task
                    TaskLabelMatch = "resting"
                else:
                    continue
            
            # Matching the run number
            if re.match(".*?" + delimiter + '(' + runIndex + ')' + ".*?", file):
                runMatch = re.match(".*?" + delimiter + '(' + runIndex + ')' + ".nii", file)[1]
                
            # Creating the directory
            if not os.path.exists(dstFilePath):
                os.makedirs(dstFilePath)
                
            # copying and renaming the file
            if dataTypeMatch == "T1w":
                newName = "/sub-" + partMatch + "_run-" + runMatch + "_T1w.nii"
            else:
                newName = "/sub-" + partMatch + "_task-" + TaskLabelMatch + "_run-" + runMatch + "_bold.nii"
            shutil.copy(srcFilePath, dstFilePath + newName)
            
    # Output
    os.system("tree " + outDir)

if __name__ == '__main__':
    main()