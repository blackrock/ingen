# InterfaceGenerator

A Python script suite that generates interface files based on the given interface metadata/config file.
The input to Interface Generator is a YAML file called metadata file which contains information regarding the source and the destination of the data and any transformation applied to it.

#### Operations and transformations supported by InterfaceGenerator on the Data:

1. Read: Responsible for reading data from different sources like databases or files. 
2. Pre-Process: Data from different sources can be merged into a single format (table-like structure). 
3. Format: Responsible for structurally modifying columns by applying the formatting options as specified in the metadata file.
4. Validate: Responsible for verifying the file produced has required data in columns. InGen leverages the power of [great_expectations](https://greatexpectations.io/) to validate the data.

To get more information on the InterfaceGenerator and how to write its metadata file we can refer below wikis -

* [How to write metadata file?](https://webster.bfm.com/Wiki/pages/viewpage.action?pageId=578637877#Howtowritemetadatafile?-DefiningDataSources)
* [SMA Interface Generator](https://webster.bfm.com/Wiki/display/BDW/SMA+Interface+Generator)


# Usage

InterfaceGenerator can be launched using pylauncher and providing the path of your metadata file. For example, if your metadata file is stored in `/u1/username/metadata/config.yml` then you can run Interface Generator by running the following command:

`pylauncher.py interfacegenerator main /u1/username/metadata/config.yml
`
#### Steps to run it locally:

1. Follow this [wiki](https://webster.bfm.com/Wiki/display/APGNEWHIRE/Python+Developer+Environment+Setup) to install PyCharm and setup `pydl`.
2. Go to Tools > External Tools > pydl. Open `pydl`, under `Select pydl command` window choose `setup` and click `Next`.
3. Click on `Add new configuration`, add path to **_main.py_** in `Script Path` and path to metadata file in `Parameters`, save it.
4. Click on `Run` to execute InterfaceGenerator.
