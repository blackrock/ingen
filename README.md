# InGen

InGen is a command line tool written on top of [pandas](https://pandas.pydata.org/) and
[great_expectations](https://greatexpectations.io/) to perform small scale data transformations and validations
without writing code. It is designed for developers and analysts to quickly transform data by specifying their
requirements in a simple YAML file.

## Table of Contents

- [InGen](#ingen)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Examples](#examples)
  - [Contributing](#contributing)
  - [License](#license)

## Installation
Note: This project has been tested on python version 3.9.6 on MacOS Ventura with apple chip.

To install the project locally follow the steps:
1. Make sure you have Python 3.9.6 installed on your system.
2. To be able to build the project locally, you will need to install the `build` package
    ```
    pip install build
    ```
3. Clone the repository
    ```
    git clone git@github.com:blackrock/ingen.git
    ```
4. Build the project
    ```
    cd ingen
    python -m build
    ```
5. Install the wheel
    ```
    pip install dist/ingen-*.whl
    ```
6. Run the project
    ```
   python -m ingen <metadata file path>
    ```

## Examples
Checkout the sample metadata files in the `examples` directory to see how InterfaceGenerator can be used to solve
common data problems.

| Examples                                                       |
| -------------------------------------------------------------- |
| [Merge two CSV files](./examples/merge_two_csvs.md)            |
| [Database as source](./examples/extract_data_from_database.md) |
| [Convert XML to CSV/Excel](./examples/xml_to_csv.md)|


For a complete list of configuration options, see the metadata reference documentation [here](./docs/config_reference.md).

## Contributing

All contributions are welcome, please see [open issues](https://github.com/blackrock/interface-generator/issues) or
create a [new issue](https://github.com/blackrock/interface-generator/issues/new/choose) to discuss your ideas. Please see our
[contributing guidelines](https://github.com/blackrock/interface-generator/blob/main/CONTRIBUTING.md) for more information.

## License
[LICENSE](https://github.com/blackrock/interface-generator/blob/main/LICENSE)
