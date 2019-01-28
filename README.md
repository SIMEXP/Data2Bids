# Data2Bids

Data2Bids convert fmri files from any extension into [NIfTI](https://nifti.nimh.nih.gov/nifti-1/) and then make them [Brain Imaging Data Structure](http://bids.neuroimaging.io/) compliant.
The user specify how the files should be read into a directory. Then the tool scan all the files and move them into the right directories.

*Disclaimer*: This tool is intended to convert data **other than** [DICOM](https://www.dicomstandard.org/about/). If you have DICOM data, please use more recognized tools as [heudiconv](https://github.com/nipy/heudiconv) or [Dcm2Bids](https://github.com/cbedetti/Dcm2Bids)

###### Input

A directory containing some files in any extension, with names containing at minimum the information of modality and patient number.
A `.JSON` configuration file explaining how the filenames should be read.

###### Output

A directory as specified by the BIDS standard.
[BIDS validator](https://github.com/bids-standard/bids-validator) is used to check the BIDS conformity of the output.

###### Example

A directory `MyDataset` with the following files :
```
MyDataset/
|
└── adhd_41278_FU12_T1_001.mnc
|
└── adhd_41278_FU24_T1_001.mnc
|
└── adhd_41578_BL00_RSFMRI_001.mnc
|
└── adhd_41578_BL00_RSFMRI_002.mnc
```

Will be transformed as :

```
MyDataset/
|
└── sub-41278/
|   |
|   └── anat/
|       |
|       └── adhd_41278_FU12_T1_001.nii
|       |
|       └── adhd_41278_FU24_T1_001.nii
└── sub-41578/
    |
    └── func/
        |
        └── adhd_41578_BL00_RSFMRI_001.nii
        |
        └── adhd_41578_BL00_RSFMRI_002.nii
```

## Usage

## Install

###### with pip

###### with singularity
