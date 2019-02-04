#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 14:40:18 2019

@author: ltetrel
"""

class DataType:
    
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

class AnatModalityLabel:
    
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