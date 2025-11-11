# caactus
caactus (**c**ell **a**nalysis **a**nd **c**ounting **t**ool **u**sing ilastik **s**oftware) is a collection of python scripts to provide a streamlined workflow for [ilastik-software](https://www.ilastik.org/), including data preparation, processing and analysis. It aims to provide biologist with an easy-to-use tool for counting and analyzing cells from a large number of microscopy pictures.

 ![workflow](https://github.com/mr2raccoon/caactus/blob/main/images/caactus-workflow(1).png)
 

# Introduction
The goal of this script collection is to provide an easy-to-use completion for the [Boundary-based segmentation with Multicut-workflow](https://www.ilastik.org/documentation/multicut/multicut) in [ilastik](https://www.ilastik.org/).
This workflow allows for the automatization of cell-counting from messy microscopic images with different (touching) cell types for biological research. 
For easy copy & paste, commands are provided in `grey code boxes` with one-click copy & paste.

# Installation
## Install miniconda, create an environment and install Python and vigra
- [Download and install miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install#windows-installation) for your respective operating system according to the instructions.
  - Miniconda provides a lightweight package and environment manager. It allows you to create isolated environments so that Python versions and package dependencies required by caactus do not interfere with your system Python or other projects.
- Once installed, create an environment for using `caactus` with the following command from your cmd-line
  ```bash
  conda create -n caactus-env -c conda-forge "python>=3.10.12" vigra 

## Install caactus
- Activate the `caactus-env` from the cmd-line with
  ```bash
  conda activate caactus-env
- To install `caactus` plus the needed dependencies inside your environment, use
  ```bash
  pip install caactus
- During the below described steps that call the `caactus-scripts`, make sure to have the `caactus-env` activated.


## Install ilastik
- [Download and install ilastik](https://www.ilastik.org/download) for your respective operating system.

## Quick Overview of the workflow
1. **Culture** organism of interest in 96-well plate
2. **Acquire** images of cells via microscopy.
3. **Create** project directory
4. **Rename** Files with the caactus-script ```renaming```
5. **Convert** files to HDF5 Format with the caactus-script  ```tif2h5py```
6. Train a [pixel classification](https://www.ilastik.org/documentation/pixelclassification/pixelclassification) model in ilastik for and later run it batch-mode.
7. Train a [boundary-based segmentation with Multicut](https://www.ilastik.org/documentation/multicut/multicut) model in ilastik for and later run it batch-mode.
8. **Remove** the background from the images using ```background_processing```
9. Train a [object classification](https://www.ilastik.org/documentation/objects/objects) model in ilastik for  and later run it batch-mode.
10. **Pool** all csv-tables  from the individual images into one global table with ```csv_summary```
- output generated: 
    - "df_clean.csv"
11. **Summarize** the data with  ```summary_statistics```
- output generated:
    - a) "df_summary_complete.csv" = .csv-table containing also "not usable" category,
    - b) "df_refined_complete.csv" = .csv-table without "not usable" category", 
    - c) "counts.csv" dataframe used in PlnModelling
    - d) bar graph ("barchart.png")
13. **Model** the count data with ```pln_modelling```




# Detailed Description of the Workflow
## 1. Culturing
- Culture your cells in a flat bottom plate of your choice and according to the needs of the organims being researched.
## 2. Image acquisition
- In your respective microscopy software environment, save the images of interest to `.tif-format`.
- From the image metadata, copy the pixel size and magnification used. 

## 3. Data Preparation
### 3.1 Create Project Directory

- For portability of the ilastik projects create the directory in the following structure:\
(Please note: the below example already includes examples of resulting files in each sub-directory)
- This allows you to copy an already trained workflow and use it multiple times with new datasets

```
project_directory  
├── 1_pixel_classification.ilp  
├── 2_boundary_segmentation.ilp  
├── 3_object_classification.ilp
├── renaming.csv
├── conif.toml
├── 0_1_original_tif_training_images
  ├── training-1.tif
  ├── training-2.tif
  ├── ...
├── 0_2_original_tif_batch_images
  ├── image-1.tif
  ├── image-2.tif
  ├── ..
├── 0_3_batch_tif_renamed
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1.tif
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2.tif
  ├── ..
├── 1_images
  ├── training-1.h5
  ├── training-2.h5
  ├── ...
├── 2_probabilities
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1-data_Probabilities.h5
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2-data_Probabilities.h5
  ├── ...
├── 3_multicut
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1-data_Multicut Segmentation.h5
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2-data_Multicut Segmentation.h5
  ├── ...
├── 4_objectclassification
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1-data_Object Predictions.h5
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1-data_table.csv
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2-data_Object Predictions.h5
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2-data_table.csv
  ├── ...
├── 5_batch_images
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1.h5
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2.h5
  ├── ...
├── 6_batch_probabilities
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1-data_Probabilities.h5
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2-data_Probabilities.h5
  ├── ...
├── 7_batch_multicut
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1-data_Multicut Segmentation.h5
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2-data_Multicut Segmentation.h5
  ├── ...
├── 8_batch_objectclassification
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1-data_Object Predictions.h5
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-1-data_table.csv
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2-data_Object Predictions.h5
  ├── strain-xx_day-yymmdd_condition1-yy_timepoint-zz_parallel-2-data_table.csv
  ├── ...
├── 9_data_analysis

```
### 3.2 Setup config.toml-file
- copy config/config.toml to your working directory and modify it as needed.
- the caactus scripts are setup for pulling the information needed for running from the file
  - CAVE: for Windows users make sure to change the backlash fro `/path/to/config.toml` to `\path\to\config.toml`, when copying the path to your working directory
- open the command line (for Windows: Anaconda Powershell) and save the path to your project file to a variable
  - whole command UNIX:
  ```bash
  p = "\path\to\config.toml" 
- whole command Windows:
  ```bash
  $p = "\path\to\config.toml"

## 4. Training
### 4.1. Selection of Training Images and Conversion
#### 4.1.1 Selection of Training data
- select a set of images that represant the different experimental conditions best
- store them in 0_1_original_tif_training_images

#### 4.1.2 Conversion
- call the `tif2h5py` script from the cmd prompt to transform all `.tif-files` to `.h5-format`. 
 The `.h5-format` allows for better [performance when working with ilastik](https://www.ilastik.org/documentation/basics/performance_tips). 
- select "-c" and enter path to config.toml
- select "-m" and choose "training"
- whole command UNIX:
  ```bash
  tif2h5py -c "$p" -m training
- whole command Windows:
  ```bash
  tif2h5py.exe -c $p -m training

### 4.2. Pixel Classification
#### 4.2.1 Project setup
- Follow the the [documentation for pixel classification with ilastik](https://www.ilastik.org/documentation/pixelclassification/pixelclassification). 
- Create the `1_pixel_classification.ilp`-project file inside the project directory.  
- For working with neighbouring / touching cells, it is suggested to create three classes: 0 = interior, 1 = background, 2 = boundary (This follows python's 0-indexing logic where counting is started at 0).

![pixel_classes](https://github.com/mr2raccoon/caactus/blob/main/images/pixel_classification_classes.JPG)

#### 4.2.2 Export Probabilties
In prediction export change the settings to 
- `Convert to Data Type: integer 8-bit`
- `Renormalize from 0.00 1.00 to 0 255`
- File:
  ```bash
  {dataset_dir}/../2_probabilties/{nickname}_{result_type}.h5

![export_prob](https://github.com/mr2raccoon/caactus/blob/main/images/export_probabilities.JPG)


### 4.3 Boundary-based Segmentation with Multicut
#### 4.3.1 Project setup
- Follow the the [documentation for boundary-based segmentation with Multicut](https://www.ilastik.org/documentation/multicut/multicut).  
- Create the `2_boundary_segmentation.ilp`-project file inside the project directory.
- In `DT Watershed` use the input channel the corresponds to the order you used under project setup (in this case input channel = 2).

![watershed](https://github.com/mr2raccoon/caactus/blob/main/images/watershed.png)


#### 4.3.2 Export Multicut Segmentation
In prediction export change the settings to 
- `Convert to Data Type: integer 8-bit`
- `Renormalize from 0.00 1.00 to 0 255`
- Format: `compressed hdf5`
- File:
  ```bash
  {dataset_dir}/../3_multicut/{nickname}_{result_type}.h5

![export_multicut](https://github.com/mr2raccoon/caactus/blob/main/images/export_multicut.JPG)


### 4.4 Background Processing
For futher processing in the object classification, the background needs to eliminated from the multicut data sets. For this the next script will set the numerical value of the largest region to 0. It will thus be shown as transpartent in the next step of the workflow. This operation will be performed in-situ on all `.*data_Multicut Segmentation.h5`-files in the `project_directory/3_multicut/`.
- call the `background-processing` script from the cmd prompt
- select "-c" and enter path to config.toml
- enter "-m training" for training mode
- whole command UNIX:
  ```bash
  background_processing -c "$p" -m training
- whole command Windows:
  ```bash
  background_processing.exe -c $p -m training

### 4.5. Object Classification
#### 4.5.1 Project setup
- Follow the the [documentation for object classification](https://www.ilastik.org/documentation/objects/objects).
- define your cell types plus an additional category for "not-usuable" objects, e.g. cell debris and cut-off objects on the side of the images
#### 4.5.2 Export Object Information
In `Choose Export Imager Settings` change settings to
- `Convert to Data Type: integer 8-bit`
- `Renormalize from 0.00 1.00 to 0 255`
- Format: `compressed hdf5`
- File:
  ```bash
  {dataset_dir}/../4_objectclassification/{nickname}_{result_type}.h5

![export_multicut](https://github.com/mr2raccoon/caactus/blob/main/images/export_objectclassification.JPG)
  
In `Configure Feature Table Export General` change seetings to
- format `.csv` and output directory File:
  ```bash
  {dataset_dir}/../4_objectclassification/{nickname}.csv`
- select your features of interest for exporting

  
![export_prob](https://github.com/mr2raccoon/caactus/blob/main/images/object_tableexport.JPG)

  
## 5. Batch Processing
- Follow the [documentation for batch processing](https://www.ilastik.org/documentation/basics/batch)
- store the images you want to process in the 0_2_original_tif_batch_images directory
- Perform steps D.2 to D.5 in batch mode, as explained in detail below (E.2 to E.5)
  
### 5.1 Rename Files
- Rename the `.tif-files` so that they contain information about your cells and experimental conditions
- Create a csv-file that contains the information you need in columns. Each row corresponds to one image. Follow the same order as the sequence of image acquisition.
- the only hardcoded columns that have to be added are `biorep` for "biological replicate" and `techrep` for "technical replicate". They are needed for downstream analysis for calculating the averages
- The script will rename your files in the following format ```columnA-value1_columnB-value2_columnC_etc.tif ``` eg. as seen in the example below picture 1 (well A1 from our plate) will be named ```strain-ATCC11559_date-20241707_timepoint-6h_biorep-A_techrep-1.tif ```
- Call the `rename` script from the cmd prompt to rename all your original `.tif-files` to their new name.
- whole command Unix:
  ```bash
  renaming -c "$p"
- whole command Windows:
  ```bash
  renaming.exe -c $p

#### 5.2 Conversion
- call the `tif2h5py` script from the cmd prompt to transform all `.tif-files` to `.h5-format`. 
- select "-m" and choose "batch"
- whole command UNIX:
  ```bash
  tif2h5py -c "$p" -m batch
- whole command Windows:
  ```bash
  tif2h5py.exe -c $p -m batch

 ![96-well-plate](https://github.com/mr2raccoon/caactus/blob/main/images/96_well_setup.png)

### 5.3 Batch Processing Pixel Classification
- open the `1_pixel_classification.ilp` project file
- under `Prediction Export` change the export directory to `File`:
  ```bash
  {dataset_dir}/../6_batch_probabilities/{nickname}_{result_type}.h5
- under `Batch Processing` `Raw Data` select all files from  `5_batch_images`

### 5.4 Batch Processing Multicut Segmentation
- open the `2_boundary_segmentation.ilp` project file
- under `Choose Export Image Settings` change the export directory to `File`:
  ```bash
  {dataset_dir}/../7_batch_multicut/{nickname}_{result_type}.h5
- under `Batch Processing` `Raw Data` select all files from  `5_batch_images`
- under `Batch Processing` `Probabilities` select all files from  `6_batch_probabilities`

### 5.5 Background Processing 
For futher processing in the object classification, the background needs to eliminated from the multicut data sets. For this the next script will set the numerical value of the largest region to 0. It will thus be shown as transpartent in the next step of the workflow. This operation will be performed in-situ on all `.*data_Multicut Segmentation.h5`-files in the `project_directory/3_multicut/`.
- call the `background-processing.py` script from the cmd prompt
- enter "-m batch" for batch mode
- whole command Unix:
  ```bash
  background_processing -c "$p" -m batch
- whole command Windows:
  ```bash
  background_processing.exe -c $p -m batch


### 5.6 Batch processing Object classification 
- under `Choose Export Image Settings` change the export directory to `File`:
  ```bash
  {dataset_dir}/../8_batch_objectclassification/{nickname}_{result_type}.h5
- in `Configure Feature Table Export General` choose format `.csv` and change output directory to:
  ```bash
  {dataset_dir}/../8_batch_objectclassification/{nickname}.csv
- select your features of interest for exporting
- under `Batch Processing` `Raw Data` select all files from  `5_batch_images`
- under `Batch Processing` `Segmentation Image` select all files from  `7_batch_multicut`

## 6. Post-Processing and Data Analysis
- Please be aware, the last two scripts, `summary_statisitcs.py` and `pln_modelling.py` at this stage are written for the analysis and visualization of two independent variables.
### 6.1 Merging Data Tables and Table Export
The next script will combine all tables from all images into one global table for further analysis. Additionally, the information stored in the file name will be added as columns to the dataset. 
- call the `csv_summary.py` script from the cmd prompt
- whole command Unix:
   ```bash
   csv_summary -c "$p"
- whole command Windows
   ```bash
   csv_summary.exe -c $p
- Technically from this point on, you can continue to use whatever software / workflow your that is easiest for use for subsequent data analysis. 

### 6.2 Creating Summary Statistics
- call the `summary_statistics.py` script from the cmd prompt
- whole command Unix:
   ```bash
  summary_statistics -c "$p"
 - whole command Windows:
   ```bash
   summary_statistics.exe -c $p
- if working with EUCAST antifungal susceptibility testing, call `summary_statistics_eucast`


### 6.3 PLN Modelling 
- call the `pln_modelling.py` script from the cmd prompt`
- whole command Unix:
   ```bash
  pln_modelling -c "$p"
 - whole command Windows:
   ```bash
   pln_modelling.exe -c $p
- please note: the limit of categories for display in the PCA-plot is n=15






