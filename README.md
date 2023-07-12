# interface-generator

A Python script suite that can transform data from various sources into desired format basis configuration defined in a yaml file. The process can be divided into five stages:

1. Read: Responsible for reading data from different sources like database or files or APIs. 
2. Pre-Process: Data from different sources can be merged or pre-processed into a single format (table-like structure). 
3. Format: Responsible for structurally modifying columns by applying the formatting options as specified in the metadata file.
4. Validate: Responsible for verifying the file produced has required data in columns. InGen leverages the power of [great_expectations](https://greatexpectations.io/) to validate the data. It supports validation on input data as well as validating data just before writing.
5. Write: Write is supported to files or APIs.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Yaml](#yaml)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)
- [Contact](#contact)

## Installation


## Usage

python interfacegenerator main /u1/username/metadata/config.yml

## Yaml


## Contributing

Guidelines for contributing to the project. link to CONTRIBUTING.md and CODE_OF_CONDUCT.md

## License

The license for the project. Lint to the LICENSE file in the root

## Credits

Acknowledgements for any contributors, libraries, or resources.

## Contact

Contact information for questions or feedback.
