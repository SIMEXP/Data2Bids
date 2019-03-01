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
import subprocess
import gzip
import numpy as np
import nibabel as nib
import data2bids.utils as utils

class Data2Bids():

    def __init__(self, input_dir=None, config=None, output_dir=None):
        self._input_dir = None
        self._config_path = None
        self._config = None
        self._bids_dir = None
        self._bids_version = "1.1.1"
        self._dataset_name = None

        self.set_data_dir(input_dir)
        self.set_config_path(config)
        self.set_bids_dir(output_dir)

    def get_data_dir(self):
        return self._data_dir

    def set_data_dir(self, data_dir):
        if data_dir is None:
            self._data_dir = os.getcwd()
        else:
            self._data_dir = data_dir

        self._dataset_name = os.path.basename(self._data_dir)

    def get_config(self):
        return self._config

    def get_config_path(self):
        return self._config_path

    def _set_config(self):
        with open(self._config_path, 'r') as fst:
            self._config = json.load(fst)

    def set_config(self, config):
        self._config = config

    def set_config_path(self, config_path):
        if config_path is None:
            # Checking if a config.json is present
            if os.path.isfile(os.path.join(os.getcwd(), "config.json")):
                self._config_path = os.path.join(os.getcwd(), "config.json")
        else:
            self._config_path = config_path
        
        assert config_path is not None, "Please provide config file"
        self._set_config()

    def get_bids_dir(self):
        return self._bids_dir

    def set_bids_dir(self, bids_dir):
        if bids_dir is None:
            # Creating a new directory for BIDS
            try:
                self._bids_dir = os.path.join(self._data_dir, self._dataset_name + "_BIDS")
            except TypeError:
                print("Error: Please provice input data directory if no BIDS directory...")
        else:
            self._bids_dir = bids_dir

    def get_bids_version(self):
        return self._bids_version

    def match_regexp(self, config_regexp, filename, subtype=False):
        delimiter_left = config_regexp["left"]
        delimiter_right = config_regexp["right"]
        match_found = False

        if subtype:
            for to_match in config_regexp["content"]:
                if re.match(".*?"
                            + delimiter_left
                            + '(' + to_match[1] + ')'
                            + delimiter_right
                            + ".*?", filename):
                    match = to_match[0]
                    match_found = True
        else:
            for to_match in config_regexp["content"]:
                if re.match(".*?"
                            + delimiter_left
                            + '(' + to_match + ')'
                            + delimiter_right
                            + ".*?", filename):
                    match = re.match(".*?"
                                     + delimiter_left
                                     + '(' + to_match + ')'
                                     + delimiter_right
                                     + ".*?", filename).group(1)
                    match_found = True

        assert match_found
        return match

    def bids_validator(self):
        assert self._bids_dir is not None, "Cannot launch bids-validator without specifying bids directory !"
        try:
            subprocess.check_call(['bids-validator', self._bids_dir])
        except FileNotFoundError:
            print("bids-validator does not appear to be installed")
            
    def description_dump(self):
        with open(self._bids_dir + "/dataset_description.json", 'w') as fst:
            data = {'Name': self._dataset_name,
                    'BIDSVersion': self._bids_version}
            json.dump(data, fst, ensure_ascii=False)
    
    def bold_dump(self, dst_file_path, new_name, task_label_match):
        with open(dst_file_path + new_name + ".json", 'w') as fst:
            data = {'RepetitionTime': float(self._config["repetitionTimeInSec"]),
                    'TaskName': task_label_match,
                    'DelayTime' : float(self._config["delayTimeInSec"])}
            json.dump(data, fst, ensure_ascii=False)
    
    def to_NIfTI(self, src_file_path, dst_file_path, new_name):
        # loading the original image
        nib_img = nib.load(src_file_path)
        nib_affine = np.array(nib_img.affine)
        nib_data = np.array(nib_img.dataobj)

        # create the nifti1 image
        # if minc format, invert the data and change the affine transformation
        # there is also an issue on minc headers, TO CHECK...
        if self._config["dataFormat"] == ".mnc":
            if len(nib_img.shape) > 3:
                nib_affine[0:3, 0:3] = nib_affine[0:3, 0:3] \
                    @ utils.rot_z(np.pi/2) \
                    @ utils.rot_y(np.pi) \
                    @ utils.rot_x(np.pi/2)
                nib_data = nib_data.T
                nib_data = np.swapaxes(nib_data, 0, 1)

                nifti_img = nib.Nifti1Image(nib_data, nib_affine, nib_img.header)
                nifti_img.header.set_xyzt_units(xyz="mm", t="sec")
                zooms = np.array(nifti_img.header.get_zooms())
                zooms[3] = self._config["repetitionTimeInSec"]
                nifti_img.header.set_zooms(zooms)
            elif len(nib_img.shape) == 3:
                nifti_img = nib.Nifti1Image(nib_data, nib_affine, nib_img.header)
                nifti_img.header.set_xyzt_units(xyz="mm")
        else:
            nifti_img = nib.Nifti1Image(nib_data, nib_affine, nib_img.header)

        #saving the image
        nib.save(nifti_img, dst_file_path + new_name + ".nii.gz")
    
    def copy_NIfTI(self, src_file_path, dst_file_path, new_name):
        shutil.copy(src_file_path, dst_file_path + new_name + ".nii")
        #compression just if .nii files
        if self._config["compress"] is True:
            with open(dst_file_path + new_name + ".nii", 'rb') as f_in:
                with gzip.open(dst_file_path + new_name + ".nii.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(dst_file_path + new_name + ".nii")
    
    def maybe_create_BIDS_dir(self):
        if os.path.exists(self._bids_dir):
            shutil.rmtree(self._bids_dir)
        os.makedirs(self._bids_dir)
    
    def run(self):
        # First we check that every parameters are configured
        if (self._data_dir is not None
                and self._config_path is not None
                and self._config is not None
                and self._bids_dir is not None):

            print("---- data2bids starting ----")
            print(self._data_dir)
            print("\n BIDS version:")
            print(self._bids_version)
            print("\n Config from file :")
            print(self._config_path)
            print("\n Ouptut BIDS directory:")
            print(self._bids_dir)
            print("\n")

            # Maybe create the output BIDS directory
            self.maybe_create_BIDS_dir()

            #dataset_description.json must be included in the folder root foolowing BIDS specs
            self.description_dump()

            # now we can scan all files and rearrange them
            for root, _, files in os.walk(self._data_dir):
                for file in files:
                    src_file_path = os.path.join(root, file)
                    dst_file_path = self._bids_dir

                    part_match = None
                    sess_match = None
                    data_type_match = None
                    run_match = None
                    new_name = None

                    # if the file doesn't match the extension, we skip it
                    if not re.match(".*?" + self._config["dataFormat"], file):
                        print("Warning : Skipping %s" %src_file_path)
                        continue

                    # Matching the participant label
                    try:
                        part_match = self.match_regexp(self._config["partLabel"], file)
                        dst_file_path = dst_file_path + "/sub-" + part_match
                        new_name = "/sub-" + part_match
                    except AssertionError:
                        print("No participant found for %s" %src_file_path)
                        continue

                    # Matching the session
                    try:
                        sess_match = self.match_regexp(self._config["sessLabel"], file)
                        dst_file_path = dst_file_path + "/ses-" + sess_match
                        new_name = new_name + "_ses-" + sess_match
                    except AssertionError:
                        print("No session found for %s" %src_file_path)
                        continue

                    # Matching the anat/fmri data type and task
                    try:
                        data_type_match = self.match_regexp(self._config["anat"]
                                                            , file
                                                            , subtype=True)
                        dst_file_path = dst_file_path + "/anat"
                    except AssertionError:
                        # If no anatomical, trying functionnal
                        try:
                            data_type_match = self.match_regexp(self._config["func"]
                                                                , file
                                                                , subtype=True)
                            dst_file_path = dst_file_path + "/func"
                            # Now trying to match the task
                            try:
                                task_label_match = self.match_regexp(self._config["func.task"]
                                                                     , file
                                                                     , subtype=True)
                                new_name = new_name + "_task-" + task_label_match
                            except AssertionError:
                                print("No task found for %s" %src_file_path)
                                continue
                        except AssertionError:
                            print("No anat nor func data type found for %s" %src_file_path)
                            continue

                    # Matching the run number
                    try:
                        run_match = self.match_regexp(self._config["runIndex"], file)
                        new_name = new_name + "_run-" + run_match
                    except AssertionError:
                        print("No run found for %s" %src_file_path)

                    # Adding the modality to the new filename
                    new_name = new_name + "_" + data_type_match

                    # Creating the directory where to store the new file
                    if not os.path.exists(dst_file_path):
                        os.makedirs(dst_file_path)

                    # finally, if the file is not nifti, we convert it using nibabel
                    if self._config["dataFormat"] != ".nii" or self._config["dataFormat"] != ".nii.gz":
                        self.to_NIfTI(src_file_path, dst_file_path, new_name)

                    # if it is already a nifti file, no need to convert it so we just copy rename
                    else:
                        self.copy_NIfTI(src_file_path, dst_file_path, new_name)

                    # finally, if it is a bold experiment, we need to add the JSON file
                    if data_type_match == "bold":
                        ### https://github.com/nipy/nibabel/issues/712, that is why we take the
                        ### scanner parameters from the config.json
                        #nib_img = nib.load(src_file_path)
                        #TR = nib_img.header.get_zooms()[3]
                        try:
                            self.bold_dump(dst_file_path, new_name, task_label_match)
                        except FileNotFoundError:
                            print("Cannot write %s" %(dst_file_path + new_name + ".nii.gz"))
                            continue

            # Output
            utils.tree(self._bids_dir)

            # Finally, we check with bids_validator if everything went alright
            self.bids_validator()

        else:
            print("Warning: No parameters are defined !")
            
#def main():
#    data2bids = Data2Bids(input_dir="/home/ltetrel/Documents/data/preventadRaw"
#                          , config="/home/ltetrel/Documents/work/Data2Bids/example/config.json")
#    data2bids.run()
#    
#if __name__ == '__main__':
#    main()
