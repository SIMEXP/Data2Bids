# Data2Bids

Data2Bids is a **python3** package that converts fmri files from extension supported by [nibabel](http://nipy.org/nibabel/api.html) into [NIfTI](https://nifti.nimh.nih.gov/nifti-1/) and then make them [Brain Imaging Data Structure](http://bids.neuroimaging.io/) compliant.
The user specify how the files should be read into a directory. Then the tool scan all the files and move them into the right directories.

*Disclaimer*: This tool is intended to convert data **other than** [DICOM](https://www.dicomstandard.org/about/). If you have DICOM data, please use more recognized tools as [heudiconv](https://github.com/nipy/heudiconv) or [Dcm2Bids](https://github.com/cbedetti/Dcm2Bids).
It also does not handle properly the headers of the images (we rely entirely on nibabel).
Finally, it is not handle well too complicated raw data structures, for this case you should use a GUI converter like [bidscoin](https://github.com/Donders-Institute/bidscoin).

###### Input

A directory containing some files in any extension, with names containing at minimum the information of modality and patient number.
A `.JSON` configuration file explaining how the filenames should be read.

###### Output

A directory as specified by the BIDS standard.
[BIDS validator](https://github.com/bids-standard/bids-validator) is used to check the conformity of the output.

###### Example

A directory `MyDataset` with the following files :
```
MyDataset/
|
└── adhd_41278_FU12_T1_001.nii
|
└── adhd_41278_FU24_T1_001.nii
|
└── adhd_41578_BL00_RSFMRI_001.nii
|
└── adhd_41578_BL00_RSFMRI_002.nii
```

Will be transformed as :

```
MyDataset/
|
└── sub-41278/
|   |
|   └── anat/
|       |
|       └── adhd_41278_FU12_T1_001.nii.gz
|       |
|       └── adhd_41278_FU24_T1_001.nii.gz
└── sub-41578/
    |
    └── func/
        |
        └── adhd_41578_BL00_RSFMRI_001.nii.gz
        |
        └── adhd_41578_BL00_RSFMRI_002.nii.gz
```
## Heuristic

The package is using heuristics on the filenames to see how files should be reorganized.
You will first probably need to write your own configuration file.
Please take example from this file : https://github.com/SIMEXP/Data2Bids/blob/master/example/config.json

The first mandatory field is `dataFormat` which specify what is the extension of the images in your input folder. `Data2Bids` accept all file formats available in [nibabel](http://nipy.org/nibabel/api.html).

If you have `NIfTI` files, you can choose to whether compress the data or not. 
If the files are not `NIfTI`, then the compression in `.nii.gz` is done automatically.

`repetitionTimeInSec` and `delayTimeInSec` are two mandatory fields needed by bids, because of some [issues with nibabel](https://github.com/nipy/nibabel/issues/712), this field is asked to the user.

The remainind fields correspond to bids structure. For each of them you need to specify what content match for what type, with the left and right delimiter with perl regexp format.

For example with `adhd_41578_NAPBL00_RSFMRI_001.mnc` if you want to match:
* the fmri field, you need to specify the left and right delimiter `_` and the content `RSFMRI`.
* the run number, the left delimiter is `_` but the right is `\\.` with content `[0-9]{3}` which means match exactly 3 integers. (\*)
* the session `BL00`, you can use left delimiter `_.*?` (match a `_` and everything after), right delimiter `_` with content `BL00`.

Everything shoud be in a list. For structural mri `anat`, functionnal mri `func` and tasks `func.task`, we use a sub-list to indentify the image sub-type (to differentiate `T1w` and `T2w` for example).

(\*) Do not forget to use an escape character to match for example a "."
## Dependencies

* [BIDS validator](https://github.com/bids-standard/bids-validator)
* nibabel
* numpy

## Install

###### with pip

`pip3 install data2bids`

###### with container

*Docker and singularity comming soon*

## Usage

If you have your configuration file `config.json` in the directory `myFmriData` where your data is just do:

```
cd myFmriData
data2bids
```

The resulting bids directory will be `myFmriData/myFmriData_BIDS`.

You can also use `-c` to provide a path to the configuration.

To change the input directory use `-d`, you can also change the output bids directory with `-o`.
