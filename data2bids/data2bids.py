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
import nibabel as nib
import numpy as np
import subprocess
import data2bids.utils as utils

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

class Data2bids:
    
    def __init__(self, pDataDir=None, pConfigPath=None, pBidsDir=None):
        self._data_dir = None
        self._config_path = None
        self._config = None
        self._bids_dir = None
        self._bids_version = "1.1.1"
        
        self.set_data_dir(pDataDir)
        self.set_config_path(pConfigPath)
        self.set_bids_dir(pBidsDir)
        
    def get_data_dir(self):
        return self._aDataDir
    
    def set_data_dir(self, pDataDir):
        if pDataDir == None:
            self._aDataDir = os.getcwd()
        else:
            self._aDataDir = pDataDir
                
    def get_config(self):
        return self._aConfig
            
    def get_config_path(self):
        return self._aConfigPath
    
    def _set_config(self):
        with open(self._aConfigPath, 'r') as fst:
            self._aConfig = json.load(fst)
    
    def set_config(self, pConfig):
        self._aConfig = pConfig
    
    def set_config_path(self, pConfigPath):
        if pConfigPath == None:
            # Checking if a config.json is present
            if os.path.isfile(os.path.join(os.getcwd(), "config.json")) :
                self._aConfigPath = os.path.join(os.getcwd(), "config.json")
            # Otherwise taking the default config
            else:
                self._aConfigPath = os.path.join(
                        os.path.dirname(__file__), "config.json")
        else:
            self._aConfigPath = pConfigPath
        
        self._mSetConfig()
    
    def get_bids_dir(self):
        return self._aBidsDir
    
    def set_bids_dir(self, pBidsDir):
        if pBidsDir == None:
            # Creating a new directory for BIDS
            try:
                self._aBidsDir = os.path.join(self._aDataDir + "_BIDS")
            except TypeError:
                print("Error: Please provice input data directory if no BIDS directory...")
        else:
            self._aBidsDir = pBidsDir
        
    def run(self):
        
        # First we check that every parameters are configured
        if ((self._aDataDir != None)
            & (self._aConfigPath != None)
            & (self._aConfig != None)
            & (self._aBidsDir!= None)):
            
            # Create the output BIDS directory
            if os.path.exists(self._aBidsDir):
                shutil.rmtree(self._aBidsDir)
            os.makedirs(self._aBidsDir)
            
            print("---- data2bids starting ----")
            print(self._aDataDir)
            print("\n Config from file :")
            print(self._aConfigPath)
            print("\n Ouptut BIDS directory:")
            print(self._aBidsDir)
            
            datasetName = os.path.basename(self._aDataDir)
            
            # What is the base format to convert to
            currExt = ".mnc"
            
            dataType = cDataType()
        #   According to  https://bids.neuroimaging.io/bids_spec.pdf
            
            # option delimiter, before and after every groups
            delimiter = '_'
            
            dataType.anat = list(["adniT1"])
            dataType.func = list(["Resting"])
            
            # session label : how much visits the patient attended
            sessLabel = list(["WA00", "BL00", "EN00", "FU03", "FU12", "FU24", "FU36", "FU48"])
            
            # task label for fmri, including resting state, TO ADD
            taskLabel = None
            
            # run number
            runIndex = "[0-9]{3}"
            
            #patient-id, with regexp 4 times
            partLabel = "[0-9]{6}"
            
            # optionnal scanner parameters
            
            # delay time in TR unit (if delayTime = 1, delayTime = repetitionTime)
            repetitionTime = 2
            delayTime = 0.03
            delayTime = delayTime*repetitionTime
            
            # creating the output dir
            outDir = os.path.dirname(pathDir) + '/' + datasetName + "_BIDS"
            if os.path.exists(outDir):
                shutil.rmtree(outDir)
            os.makedirs(outDir)
            
            #dataset_description.json must be included in the folder root foolowing BIDS specs
            
            with open(outDir + "/dataset_description.json", 'w') as fst:
                data = {'Name': datasetName,
                        'BIDSVersion': bidsVersion}
                json.dump(data, fst, ensure_ascii=False)
            
            # now we can scan all files and rearrange them
            for root,_,files in os.walk(pathDir): 
                for file in files: 
                    srcFilePath = os.path.join(root, file)
                    dstFilePath = outDir
                    
                    partMatch = None
                    sessMatch = None
                    dataTypeMatch = None
                    runMatch = None
                    newName = None
                    
                    # we first start by matching the extension
                    if not re.match(".*?" + currExt, file):
                        continue
                    
                    # Matching the participant number
                    if re.match(".*?" + delimiter + '(' + partLabel + ')' + delimiter + ".*?" + currExt, file):
                        partMatch = re.match(".*?" + delimiter + '(' + partLabel + ')' + delimiter + ".*?" + currExt, file).group(1)
                        dstFilePath = dstFilePath + "/sub-" + partMatch
                    
                    # Matching the session label
                    for toMatch in sessLabel:
                        if re.match(".*?" + delimiter + ".*?" + '(' + toMatch + ')' + delimiter + ".*?" + currExt, file):
                            sessMatch = re.match(".*?" + delimiter + ".*?" + '(' + toMatch + ')' + delimiter + ".*?" + currExt, file).group(1)
                            dstFilePath = dstFilePath + "/ses-" + sessMatch
                        else:
                            continue
                    
                    # Matching the data type
                    for toMatch in dataType.anat:
                        if re.match(".*?" + delimiter + '(' + toMatch + ')' + delimiter + ".*?" + currExt, file):
                            dataTypeMatch = "T1w"
                            dstFilePath = dstFilePath + "/anat"
                        else:
                            continue
                    
                    for toMatch in dataType.func:
                        if re.match(".*?" + delimiter + '(' + toMatch + ')' + delimiter + ".*?" + currExt, file):
                            dataTypeMatch = "bold"
                            dstFilePath = dstFilePath + "/func"
                        #### Here the part for resting task
                            taskLabelMatch = "rest"
                        else:
                            continue
                    
                    # Matching the run number
                    if re.match(".*?" + delimiter + '(' + runIndex + ')' + currExt, file):
                        runMatch = re.match(".*?" + delimiter + '(' + runIndex + ')' + currExt, file).group(1)
                        
                    # if one match is missing, there is something wrong
                    if ((partMatch == None)
                        | (sessMatch == None) 
                        | (dataTypeMatch == None) 
                        | (runMatch == None)):
                        
                        print("WARNING : Missmatch for %str" %srcFilePath)
                        continue
                    
                    # Creating the directory
                    if not os.path.exists(dstFilePath):
                        os.makedirs(dstFilePath)
                    
                    # copying and renaming the file
                    if dataTypeMatch == "T1w":
                        newName = "/sub-" + partMatch + "_ses-" + sessMatch + "_T1w.nii"
                    elif dataTypeMatch == "bold":
                        newName = "/sub-" + partMatch + "_ses-" + sessMatch + "_task-" + taskLabelMatch + "_bold.nii"
                    # if the file is not recognized, we simply continue the process
                    else:
                        continue
                        
                    # finally, if the file is not nifti, we convert it using nibabel
                    if file[-4::] != ".nii":
                        
                        # loading the original image
                        nibImg = nib.load(srcFilePath)
                        nibAffine = np.array(nibImg.affine)
                        nibData = np.array(nibImg.dataobj)
                        
                        # create the nifti1 image
                        # if minc format, invert the data and change the affine transformation (TO CHECK !)
                        # there is also an issue on minc headers...
                        if( file[-4::] == ".mnc" ):
                            if( len(nibImg.shape) > 3):
                                nibAffine[0:3, 0:3] = nibAffine[0:3, 0:3] @ utils.rotZ(np.pi/2) @ utils.rotY(np.pi) @ utils.rotX(np.pi/2)
                                nibData = nibData.T
                                nibData = np.swapaxes(nibData, 0, 1)
                            
                                niftiImg = nib.Nifti1Image(nibData, nibAffine, nibImg.header)
                                niftiImg.header.set_xyzt_units(xyz="mm", t="sec")
                                zooms = np.array(niftiImg.header.get_zooms())
                                zooms[3] = repetitionTime
                                niftiImg.header.set_zooms(zooms)
                            elif( len(nibImg.shape) == 3):
                                niftiImg = nib.Nifti1Image(nibData, nibAffine, nibImg.header)
                                niftiImg.header.set_xyzt_units(xyz="mm")
                        else:
                            niftiImg = nib.Nifti1Image(nibData, nibAffine, nibImg.header)
                        
                        #saving the image
                        nib.save(niftiImg, dstFilePath + newName)
                    
                    # if it is already a nifti file, no need to convert it so we just copy and rename
                    else:
                        shutil.copy(srcFilePath, dstFilePath + newName)
                        
                    # finally, if it is a bold experiment, we need to add the JSON file
                    if dataTypeMatch == "bold":
                        nibImg = nib.load(srcFilePath)
                        TR = nibImg.header.get_zooms()[3]
                        with open(dstFilePath + newName[:-4] + ".json", 'w') as fst:
                            data = {'RepetitionTime': float(repetitionTime),
                                    'TaskName': taskLabelMatch,
                                    'DelayTime' : float(delayTime)}
                            json.dump(data, fst, ensure_ascii=False)
                    
            # Output
            utils.tree(outDir)
            
            # Finally, we check with bids_validator if everything went alright
            self.bidsValidator()
            
        else:
            print("Warning: No parameters are defined !")
            
    def bidsValidator(self):
        if self._aDataDir != None:
            try:
                subprocess.check_call(['bids-validator', self._aDataDir])
            except FileNotFoundError:
                print("bids-validator does not appear to be installed")
        else:
            print("Warning: No input data dir !")

#def main():
#    pathDir = "/home/ltetrel/Documents/data/preventadRaw"
#    datasetName = os.path.basename(pathDir)
#    bidsVersion = "1.1.1"
#    
#    # What is the base format to convert to
#    currExt = ".mnc"
#    
#    dataType = cDataType()
##   According to  https://bids.neuroimaging.io/bids_spec.pdf
#    
#    # option delimiter, before and after every groups
#    delimiter = '_'
#    
#    dataType.anat = list(["adniT1"])
#    dataType.func = list(["Resting"])
#    
#    # session label : how much visits the patient attended
#    sessLabel = list(["WA00", "BL00", "EN00", "FU03", "FU12", "FU24", "FU36", "FU48"])
#    
#    # task label for fmri, including resting state, TO ADD
#    taskLabel = None
#    
#    # run number
#    runIndex = "[0-9]{3}"
#    
#    #patient-id, with regexp 4 times
#    partLabel = "[0-9]{6}"
#    
#    # optionnal scanner parameters
#    
#    # delay time in TR unit (if delayTime = 1, delayTime = repetitionTime)
#    repetitionTime = 2
#    delayTime = 0.03
#    delayTime = delayTime*repetitionTime
#    
#    # creating the output dir
#    outDir = os.path.dirname(pathDir) + '/' + datasetName + "_BIDS"
#    if os.path.exists(outDir):
#        shutil.rmtree(outDir)
#    os.makedirs(outDir)
#    
#    #dataset_description.json must be included in the folder root foolowing BIDS specs
#    
#    with open(outDir + "/dataset_description.json", 'w') as fst:
#        data = {'Name': datasetName,
#                'BIDSVersion': bidsVersion}
#        json.dump(data, fst, ensure_ascii=False)
#    
#    # now we can scan all files and rearrange them
#    for root,_,files in os.walk(pathDir): 
#        for file in files: 
#            srcFilePath = os.path.join(root, file)
#            dstFilePath = outDir
#            
#            partMatch = None
#            sessMatch = None
#            dataTypeMatch = None
#            runMatch = None
#            newName = None
#            
#            # we first start by matching the extension
#            if not re.match(".*?" + currExt, file):
#                continue
#            
#            # Matching the participant number
#            if re.match(".*?" + delimiter + '(' + partLabel + ')' + delimiter + ".*?" + currExt, file):
#                partMatch = re.match(".*?" + delimiter + '(' + partLabel + ')' + delimiter + ".*?" + currExt, file).group(1)
#                dstFilePath = dstFilePath + "/sub-" + partMatch
#            
#            # Matching the session label
#            for toMatch in sessLabel:
#                if re.match(".*?" + delimiter + ".*?" + '(' + toMatch + ')' + delimiter + ".*?" + currExt, file):
#                    sessMatch = re.match(".*?" + delimiter + ".*?" + '(' + toMatch + ')' + delimiter + ".*?" + currExt, file).group(1)
#                    dstFilePath = dstFilePath + "/ses-" + sessMatch
#                else:
#                    continue
#            
#            # Matching the data type
#            for toMatch in dataType.anat:
#                if re.match(".*?" + delimiter + '(' + toMatch + ')' + delimiter + ".*?" + currExt, file):
#                    dataTypeMatch = "T1w"
#                    dstFilePath = dstFilePath + "/anat"
#                else:
#                    continue
#            
#            for toMatch in dataType.func:
#                if re.match(".*?" + delimiter + '(' + toMatch + ')' + delimiter + ".*?" + currExt, file):
#                    dataTypeMatch = "bold"
#                    dstFilePath = dstFilePath + "/func"
#                #### Here the part for resting task
#                    taskLabelMatch = "rest"
#                else:
#                    continue
#            
#            # Matching the run number
#            if re.match(".*?" + delimiter + '(' + runIndex + ')' + currExt, file):
#                runMatch = re.match(".*?" + delimiter + '(' + runIndex + ')' + currExt, file).group(1)
#                
#            # if one match is missing, there is something wrong
#            if ((partMatch == None)
#                | (sessMatch == None) 
#                | (dataTypeMatch == None) 
#                | (runMatch == None)):
#                
#                print("WARNING : Missmatch for %str" %srcFilePath)
#                continue
#            
#            # Creating the directory
#            if not os.path.exists(dstFilePath):
#                os.makedirs(dstFilePath)
#            
#            # copying and renaming the file
#            if dataTypeMatch == "T1w":
#                newName = "/sub-" + partMatch + "_ses-" + sessMatch + "_T1w.nii"
#            elif dataTypeMatch == "bold":
#                newName = "/sub-" + partMatch + "_ses-" + sessMatch + "_task-" + taskLabelMatch + "_bold.nii"
#            # if the file is not recognized, we simply continue the process
#            else:
#                continue
#                
#            # finally, if the file is not nifti, we convert it using nibabel
#            if file[-4::] != ".nii":
#                
#                # loading the original image
#                nibImg = nib.load(srcFilePath)
#                nibAffine = np.array(nibImg.affine)
#                nibData = np.array(nibImg.dataobj)
#                
#                # create the nifti1 image
#                # if minc format, invert the data and change the affine transformation (TO CHECK !)
#                # there is also an issue on minc headers...
#                if( file[-4::] == ".mnc" ):
#                    if( len(nibImg.shape) > 3):
#                        nibAffine[0:3, 0:3] = nibAffine[0:3, 0:3] @ utils.rotZ(np.pi/2) @ utils.rotY(np.pi) @ utils.rotX(np.pi/2)
#                        nibData = nibData.T
#                        nibData = np.swapaxes(nibData, 0, 1)
#                    
#                        niftiImg = nib.Nifti1Image(nibData, nibAffine, nibImg.header)
#                        niftiImg.header.set_xyzt_units(xyz="mm", t="sec")
#                        zooms = np.array(niftiImg.header.get_zooms())
#                        zooms[3] = repetitionTime
#                        niftiImg.header.set_zooms(zooms)
#                    elif( len(nibImg.shape) == 3):
#                        niftiImg = nib.Nifti1Image(nibData, nibAffine, nibImg.header)
#                        niftiImg.header.set_xyzt_units(xyz="mm")
#                else:
#                    niftiImg = nib.Nifti1Image(nibData, nibAffine, nibImg.header)
#                
#                #saving the image
#                nib.save(niftiImg, dstFilePath + newName)
#            
#            # if it is already a nifti file, no need to convert it so we just copy and rename
#            else:
#                shutil.copy(srcFilePath, dstFilePath + newName)
#                
#            # finally, if it is a bold experiment, we need to add the JSON file
#            if dataTypeMatch == "bold":
#                nibImg = nib.load(srcFilePath)
#                TR = nibImg.header.get_zooms()[3]
#                with open(dstFilePath + newName[:-4] + ".json", 'w') as fst:
#                    data = {'RepetitionTime': float(repetitionTime),
#                            'TaskName': taskLabelMatch,
#                            'DelayTime' : float(delayTime)}
#                    json.dump(data, fst, ensure_ascii=False)
#            
#    # Output
#    utils.tree(outDir)
#
#if __name__ == '__main__':
#    main()
