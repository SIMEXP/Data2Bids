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

"""
another way to do it:

https://github.com/MounaSafiHarab/Loris-MRI/blob/9b7c299006378d54c9b457d8e1c1a3c71eaf4176/tools/MakeNiiFilesBIDSCompliant.pl
"""

# tree shell-like in python from (https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python)
from pathlib import Path

class DisplayablePath(object):
    display_filename_prefix_middle = '├──'
    display_filename_prefix_last = '└──'
    display_parent_prefix_middle = '    '
    display_parent_prefix_last = '│   '

    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(list(path
                               for path in root.iterdir()
                               if criteria(path)),
                          key=lambda s: str(s).lower())
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(path,
                                         parent=displayable_root,
                                         is_last=is_last,
                                         criteria=criteria)
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    def displayable(self):
        if self.parent is None:
            return self.path

        _filename_prefix = (self.display_filename_prefix_last
                            if self.is_last
                            else self.display_filename_prefix_middle)

        parts = ['{!s} {!s}'.format(_filename_prefix,
                                    self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle
                         if parent.is_last
                         else self.display_parent_prefix_last)
            parent = parent.parent

        return ''.join(reversed(parts))

def tree(path):
    paths = DisplayablePath.make_tree(Path(path))
    for path in paths:
        print(path.displayable())

def rotX(alpha):
    return np.array([[1,0,0],[0, np.cos(alpha), np.sin(alpha)], [0, -np.sin(alpha), np.cos(alpha)]])

def rotY(alpha):
    return np.array([[np.cos(alpha), 0, -np.sin(alpha)],[0, 1, 0], [np.sin(alpha), 0, np.cos(alpha)]])

def rotZ(alpha):
    return np.array([[np.cos(alpha), np.sin(alpha), 0],[-np.sin(alpha), np.cos(alpha), 0], [0, 0, 1]])

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
    pathDir = "/home/ltetrel/Documents/data/preventadRaw"
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
                    taskLabelMatch = "rest"
                else:
                    continue
            
            # Matching the run number
            if re.match(".*?" + delimiter + '(' + runIndex + ')' + '\.' + ".*?", file):
                runMatch = re.match(".*?" + delimiter + '(' + runIndex + ')' + '\.' + ".*?", file)[1]
                
            # Creating the directory
            if not os.path.exists(dstFilePath):
                os.makedirs(dstFilePath)
            
            # copying and renaming the file
            if dataTypeMatch == "T1w":
                newName = "/sub-" + partMatch + "_ses-" + sessMatch + "_T1w.nii"
            else:
                newName = "/sub-" + partMatch + "_ses-" + sessMatch + "_task-" + taskLabelMatch + "_bold.nii"
                
            # finally, if the file is not nifti, we convert it using nibabel
            if file[-4::] != ".nii":
                
                # loading the original image
                nibImg = nib.load(srcFilePath)
                nibAffine = np.array(nibImg.affine)
                nibData = np.array(nibImg.dataobj)
                
                # create the nifti1 image
                # if minc format, invert the data and change the affine transformation (TO CHECK !)
                if( (file[-4::] == ".mnc") & (len(nibImg.shape)>3)):
                    nibAffine[0:3, 0:3] = nibAffine[0:3, 0:3] @ rotZ(np.pi/2) @ rotY(np.pi) @ rotX(np.pi/2)
                    nibData = nibData.T
                    nibData = np.swapaxes(nibData, 0, 1)
                    
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
                    data = {'RepetitionTime': TR,
                            'TaskName': taskLabelMatch}
                    json.dump(data, fst, ensure_ascii=False)
            
    # Output
    tree(outDir)

if __name__ == '__main__':
    main()
