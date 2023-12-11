# interface-generator

A Python script suite that can transform data from various sources into desired format basis configuration defined in a yaml file. The process can be divided into five stages:

1. Read: Responsible for reading data from different sources like database or files or APIs. 
2. Pre-Process: Data from different sources can be merged or pre-processed into a single format (table-like structure). 
3. Format: Responsible for structurally modifying columns by applying the formatting options as specified in the metadata file.
4. Validate: Responsible for verifying the file produced has required data in columns. InGen leverages the power of [great_expectations](https://greatexpectations.io/) to validate the data. It supports validation on input data as well as validating data just before writing.
5. Write: Write is supported to files or APIs.

## Table of Contents

- [Installation](#installation)
- [Examples](#examples)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)
- [Contact](#contact)

## Installation
1. Create a virtual environment
    ```
    python -m venv venv
    ```
2. Activate venv and install dependencies
    ```
    source venv/bin/activate
    pip install -r requirements.txt
    ```

### Examples
Checkout the sample metadata files in the `examples` directory to see how InterfaceGenerator can be used to solve
common data problems.

| Examples                                            |
|-----------------------------------------------------|
| [Merge two CSV files](./examples/merge_two_csvs.md) |


## Usage

`python main.py <metadata file path>`

### Sample YAML
To test your local setup let's write a config file that will read a CSV file 
and write its content into a PSV file without any other modification.

1. Create a file in your home directory called `test-file.yaml`
2. Copy the following code into the file
```
interfaces:
    sample:
        sources: [input_file]
        columns:
            - src_col_name: name
            - src_col_name: city
        output:
            type: delimited_file
            props:
                delimiter: '|'
                path: ~/output.psv
                header:
                    type: delimited_result_header

sources:
    - id: input_file
      type: file
      file_type: delimited_file
      delimiter: ','
      file_path: ~/input.csv
      columns: [name, city]
      skip_header_size: 1
```
3. Create a sample intput file `input.csv` and copy the following contents
```
name,city
piyush,pune
sachin,mumbai
dhoni,ranchi
```
4. Run InterfaceGenerator 
```
python main.py ~/test-file.yaml
```
5. An output file `output.psv` should be created with following contents
```
name|city
piyush|pune
sachin|mumbai
dhoni|ranchi
```


## Contributing

Guidelines for contributing to the project. link to CONTRIBUTING.md and CODE_OF_CONDUCT.md

## License

The license for the project. Lint to the LICENSE file in the root

## Credits

Acknowledgements for any contributors, libraries, or resources.

## Contact

Contact information for questions or feedback.
