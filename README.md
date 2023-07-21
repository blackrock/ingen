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

The input to Interface Generator is a YAML file called metadata file which contains information regarding the source and the destination of the data and any transformation applied to it.
**Defining Data Sources**
A Data Source is the location from where the data originates. It can be a database, file or an api. The following code snippet shows an example of a 'sources' array containing a data source - an excel file. 
sources:
	- id: restrictions_file
	  type: file
	  file_type: excel
	  file_path: 'path/to/file.xls'

**DB Source**
A DB source is identified by setting type of the data source to db. Connection to a particular database can be made by setting the value of db_token.
The following table shows all the fields available to describe a DB source.
  Field Name	Type	Description
  id	string	REQUIRED. Data Source identifier
  type	string	REQUIRED. [db] type of data source
  db_token	string	REQUIRED. Sybase DB token
  query	string	REQUIRED. SQL query to fetch data from db
  temp_table_params 	array<string>	Optional: params to create temp table from file source

The following table shows all the fields available to describe a temp_table parameters  from file source
  Field Name	Type	Description
  id	string	REQUIRED. Data Source identifier. Used to refer to a source while defining interfaces.
  type	string	REQUIRED. [db] type of data source
  file_type	string	REQUIRED. [delimited_file, excel] type of file
  delimiter	string	Type of delimiter. Default: ','
  file_path	string	REQUIRED. Path of file
  temp_table_name	string	REQUIRED. Name of temp table
  temp_table_cols	array<string>	Return the array of temp table column name, type, size and file column to be used from the source file 
  Eg: 
  temp_table_cols: [
        { "name": "client_id","type": "varchar", "size": 50,"file_col": "no_hold",default:"temP-string"},
        { "name": "ticker", "type": "int", "file_col": "Ticker", default: 0},
        { "name": "cusip", "type": "varchar", "size": 50, "file_col": "cusip"},
      ]
**Passing run-time parameters to SQL queries**
SQL Queries defined in the data source can contain dynamic replaceable elements. These replaceable elements are written within curly braces and the actual values with which it will be replaced can be set via command-line arguments.
In the following example, {date} will be replaced by the value of "date" passed via the command line.
sources:
    - ...
    - query: "SELECT TOP 10 field1, field2
              FROM <table>
              WHERE date > {date}"

**File Source**
A file source is identified by setting type of the data source to file. Interface Generator supports reading excel,fixed width and delimited files (like CSV, PSV, etc). The type of file is identified by setting the file_type field.
The following table describes all the available fields to describe a file source.
  Field Name	Type	Description
  id	string	REQUIRED. Data Source identifier. Used to refer to a source while defining interfaces.
  type	string	REQUIRED. [db] type of data source
  file_type	string	REQUIRED. [delimited_file, excel] type of file
  delimiter	string	Type of delimiter. Default: ','
  file_path	string	REQUIRED. Path of file
  columns	array<string>	REQUIRED. column names in the source file
  sheet_name(only for excel files)	string	Sheet name you want to read (Default: First sheet of the excel)/Can provide sheet index as well
  skip_header_size	integer	Number of lines to be skipped from the top of the file
  skip_trailer_size	integer	Number of lines to be skipped at the bottom of the file
  return_empty_if_not_exist	boolean	Return empty dataframe if the file is not present instead of throwing FileNotFoundError exception
  col_specification	list of tuple (int, int) or string	Tuple defining the fixed width indices of columns. 
String value 'infer' can be used to instruct the parser to try detecting the column specifications from the first 100 rows of
the data which are not being skipped via skiprows (default='infer')

The following code snippet shows an example of a 'source' array containing a file source which points to an excel file stored at this hypothetical location 
  sources:
      - id: file_excel
        type: file
        file_type: excel
        file_path: '..\sample-excel.xlsx'
  	  sheet_name: "sample sheet"
        columns: ['column1',column2']

**Passing run-time parameters to file_path**

Source file_path can be set via command-line argument --infile
Also add new field in Source object in config yml
use_infile : true
So only the specific source will utilize the command line file_path 
i.e. --infile filelLoc/sample.xlsx will overwrite the file_path value in source during runtime.

**API Source**
An API source is identified by setting type of the data source to api. Interface Generator supports reading data from more than one URLs at a time.
The following table describes all the available fields to describe an API source.
  Field Name	Type	Description
  id	string	REQUIRED. Data Source identifier. Used to refer to a source while defining interfaces.
  type	string	REQUIRED. [api] type of data source
  url	string	REQUIRED. base url to access data from.
  method	string	HTTP method. Default GET.
  request_body	string	JSON String for HTTP request body. 
  headers	json object	HTTP headers as key values. 
  batch		REQUIRED. More than one URL can be constructed from the base url depending on batch size and the parameter that needs batching.
  url_params		REQUIRED. query parameters that can be fetched from different sources(DB, File or can be constant)
  data_node	list	REQUIRED. end point of a list in api
  data_key	list	REQUIRED. specific columns in api.
  meta	list	Used in DF to JSON conversion. See examples here
  auth		REQUIRED. Tokens needed to authenticate the urls.
  retries	int	Number of retries to make if the request fails
  interval	int	Number of seconds to wait before making a retry
  interval_increment	int	Number of seconds added to the interval when retrying.

So if a request fails with the following params:
retires = 4, interval = 2, interval_increment = 2
4 retries will be made after 2, 4, 6, and 8 seconds.
success_criteria	string	Name of the success_criteria function. See 'success criteria' below for more info
criteria_option	json_object	Params of success_criteria function. See 'success criteria' below for more info
queue_size	int	When a queue size is given, a queue is created with maxsize = 'queue_size'. See 'throttling' below for more.
tasks_len	int	Number of concurrent requests to fetch. 
(Note: The colored fields are explained below in detail.)
Success Criteria

The following functions can be used to define the success criteria of the http request

  Function Name	Parameters	Description
  status_criteria	{'status': 200}	Checks if the response status code is equal to the expected code passed in options
  payload_criteria	{'key': 'done', 'value': 'True'}	Checks if a given field is present in the response and is equal to the provided value. 

If payload contains a key called 'done' and its values is 'True', then this function returns true
batch: The "batch" field consists of 2 fields:
  1.	size: The size of batching
  2.	id: The id based on which batching can be done.
  ...
  batch:
      size: 2
      id: tickerIds
 **Throttling**
When multiple requests are created using 'batch'-ing. Users have an option to run these requests concurrently. InGen stores all the HTTP Request objects in a list and creates a queue. A producer task picks one request from the list and adds it to the queue if the queue is not full. Multiple consumer tasks concurrently read from the queue and fetch data from API by executing the HTTP request. To control the number of concurrent requests, users can set the max size of the queue (queue_size) and max number of consumer tasks to be created (tasks_len). 
Example:
If an API has a rate limit of 1000 requests per minute and each request takes on average 1 second to complete. 
So we can run ~16 requests parallelly. Hence `tasks_len` = 16  and `queue_size` can be more than 16.
By default, both these parameters will be set to 1,  which basically means all requests will run synchronously. 
url_params: URL params can be fetched from a file, a database, or can be declared as a constant in the configuration file. It consists of fields depending on the type from which the params are fetched.

  ...
  url_params:
      - id: tickerIDs
        type: file
        file_path: '...'
        delimiter: ','
  	  columns: [ column1, column2, column3 ]
        dest_column: 'column1'
      - id: secondId
        type: db
        db_token: databasename
        query: 'select * from ...'
      - id: constExample
        type: const
        value: 'const-string'
for type = file, following table describes the field values
        Field Name	Type	Description
        id	string	REQUIRED. Data Source identifier.
        type	string	REQUIRED. Data Source type.
        file_path	string	REQUIRED. path of file..
        delimiter	string	Type of delimiter. Default: ','
        columns	list	REQUIRED list of all columns in the file.
        dest_column	string	name of the column to be fetched and mapped in the url param.( can skip this filed if file has only one column)
    auth: The "auth" field consists of tokens needed to authenticate the urls. There are 3 fields:
        1.	type: "BasicAuth" (by default as of now).
        2.	username: Service-account/API Token for username 
        3.	pwd: Service-account/API Token for password.
    ...
    auth:
        type: 'BasicAuth'
        username: 'TOKEN'
        pwd: 'TOKEN'
        
    headers: HTTP Headers
    Header values can also contain dynamic fields, similar to file paths. Dynamic values are written in this format - $function(args) - where `function` is the name of interpolator function and `args` is argument to the function.
        headers:
          Content-Type: "application/json"
          Token-Value: $token(TEST_TOKEN_NAME)

**RawDataStore Source**
  A RawDataStore source represents a data that comes in the form of a data frame. It is defined by the following parameters:
  Field Name	Type	Description
  id	string	REQUIRED. ID of the dataframe
  Type	string	REQUIRED.  Type of data, in this case, RawDataStore source
  		
  So here, A dictionary named Store contains IDs and Data Frames as key-value pairs, Which can be read from and written into the dictionary using the ID.
  sources:
  	- id: DF2
        type: rawdatastore

**Json Source**
  A Json source represents a JSON string payload. The payload itself is given alongside the metadata file.
  Field Name	Type	
  id	string	REQUIRED. Data source identifier
  type	string	REQUIRED. Data source type
  sources:
    - id: json_payload
      type: json


**Defining Interfaces**

  A single metadata file can define multiple interfaces. All interfaces and their properties are defined under the root "interfaces" object. For each interface, a separate interface file will be generated. In the following example, three interfaces - positions, tax-lots, accounts - are declared.
  interfaces:
      positions:
          ...
      tax-lots:
          ...
      accounts:
          ...
  
  Each interface object is defined using four properties:
  •	Sources 
  •	Preprocessing
  •	Output
  •	Columns
**Sources**
  The "sources" field is an array of source IDs. Each source ID points to the data source defined in the metadata file. In the following example, the metadata file contains two sources - file_source and db_source. To declare that the "positions" interface will fetch data from both these sources, a sources array is declared containing IDs of the data sources.
  interfaces:
  	positions:
      	sources: [source1, source2]
  		...
  		...
  
  sources:
      - id: file_source
        ...
      - id: db_source
        ... 

**Preprocessing**
  Pre-processing steps are supposed to work like a pipeline. The output of one pre-processor would be the input to the next pre-processor. The input of the first pre-processor in the pipeline would be the first source from the sources array. Pre-processing steps are for row-wise operations on the dataframe.
  Merge
  Merge is used to merge data from multiple sources. In the following example, source1 (first element in the sources array, also called as left source) will be merged with the given source, source2 (also called as right source).  If the merge pre-process step appears after another pre-process step, then the output of the previous step is considered as the left source. The name of the column to use while merging, is given by - left_key and right_key. merge_type indicates the type of merge - left, right, inner (default). These types work like SQL left outer join, right outer join, and inner join.  
  interfaces:
    interface_name:
      sources: [ source1,source2 ]
      pre_processing:
        - type: merge
          source: source2
          left_key: cusip
          right_key: bfm_cusip
          merge_type: left
  		...
  
  sources:
      - id: source1
        ...
      - id: source2
        ... 
      Field Name	Type	Description
      type	string	REQUIRED. merge
      source	string	REQUIRED. identifier of the right data source. This identifier must be present
      in the sources array.
      left_key	string	column name to join on in left data source
      right_key	string	column name to join on in right data source
      merge_type	string	[left, right, inner] default: inner
      Examples:
      Source 1 (left source) - marks1
      name	english	maths
      Ankur	45	49
      Sakshi	37	40
      Peter	44	48
      
      Source 2 (right source) - marks2
      name	science	french
      Ankur	48	39
      James	44	45
      Arthur	39	47
      
      
      Left Merge
      sources: [ marks1,marks2 ]
          pre_processing:
            - type: merge
              source: marks2
              left_key: name
              right_key: name
              merge_type: left
      		...
      Output
      name	english	maths	science	french
      Ankur	45	49	48	39
      Sakshi	37	40		
      Peter	44	48		
      
      Inner Merge
      sources: [ marks1,marks2 ]
          pre_processing:
            - type: merge
              source: marks2
              left_key: name
              right_key: name
              merge_type: inner
      		...
      Output
      name	english	maths	science	french
      Ankur	45	49	48	39
      
      Right Merge
      sources: [ marks1,marks2 ]
          pre_processing:
            - type: merge
              source: marks2
              left_key: name
              right_key: name
              merge_type: right
      		...
      Output
      name	english	maths	science	french
      Ankur	45	49	48	39
      James			44	45
      Arthur			39	47




**Union**
    Union concatenates (appends) the data from multiple data source into a single unit. This should ideally be used when a data in divided in to multiple sources and we want to assemble it into a single unit
    interfaces:
    	positions:
        	sources: [source1, source2]
    		pre_processing:
          		- type: union
            	  source:
              	    - source1
              		- source2
    		...
    
    sources:
        - id: source1
          ...
        - id: source2
          ... 
    
    Aggregation
    Aggregation can be used to perform operations like grouping and performing aggregation operations like sum, count, min, max and mean. This does not work on multiple sources, it would only work on one single unit of data
    interfaces:
    	positions:
        	sources: [source1, source2]
    		pre_processing:
          		- type: aggregate
            	  groupby:
              	    cols: ['fund', 'cusip']
    			  agg:
    				operation: 'sum'
              		col: 'face'
    		...
    
    sources:
        - id: source1
          ...
        - id: source2
          ... 

**Mask**

  Mask allows filtering a data source wrt to another data source. 
  sources: [ 'taxlot', 'accounts' ]
  pre_processing:
  	- type: mask
          on_col: 'Account Number'
          masking_source: account_info
          masking_col: ACCOUNT_ID
  In this example, we are applying mask on column 'Account Number' of 'taxlot' source, using column 'ACCOUNT_ID' of 'accounts' as the masking source. So if taxlot contains data of 10 different account numbers, out of which only 4 are present in accounts file, then after applying the mask operation, only 4 accounts data will be present in tax_lot. 

**Melt**
  Melt is used to convert rows into columns. If the dataframe contains one header row and one data row. It'll be converted into a dataframe containing two columns.
      pre_processing:
        - type: melt
          key_column: TICKER
          value_column: PORTFOLIO_ID
          include_keys: []
          source:
               - portfolio_id
  In the above example, let's say your data frame looks like this:
  A	B	C	D
  1	2	3	4
  Then after applying the above melt pre-processing it'll be converted into the following form:
  TICKER	PORTFOLIO_ID
  A	1
  B	2
  C	3
  D	4

**Filter**
    Filter is used to filter rows by column values, supported column-wise operation are 'and' and 'or'
        pre_processing:
          - type: filter
            operator: and
            cols:
              - col: 'name'
                val: [ 'Ashish' ]
              - col: 'score'
                val: [ 82 ]
    In the above example, let's say your data frame looks like this:
    name	score	subject
    Ashish	50	Science
    Aman	75	Hindi
    Ashish	82	Hindi
    Aditya	93	English
    Aditya	77	Match
    Then after applying the above filter pre-processing it'll be converted into the following form:
    name	score	subject
    Ashish	82	Hindi
    If operator 'or' is configured instead of 'and', then after applying the above filter pre-processing it'll be converted into the following form:
    name	score	subject
    Ashish	50	Science
    Ashish	82	Hindi
    Multiple filters can be configured, it works like a pipleline first filter output will be the input of the next filter
    Columns
    Columns field represents the columns of the final data that will be persisted. It is a mapping of source column name and destination column name. It also includes details of any formatter that is to be applied on a column.
    interfaces:
        positions:
            ...
            columns:
              - src_col_name: "start_date"
                dest_col_name: "START DATE"
                formatters:
                  - type: date
                    format: "%m/%d/%y"
              - src_col_name: "stop_date"
                dest_col_name: "STOP DATE"
              - src_col_name: "fund"
                dest_col_name: "PORTFOLIO"
              - src_col_name: "status"
                dest_col_name: "STATUS"
              - src_col_name: "face"
                dest_col_name: "FACE VALUE"


    Field Name	Type	Description
    src_column_name	string	REQUIRED. Column name in data source
    dest_col_name	string	Column name to be used in the output. Defaults to src_column_name
    formatters	array<object>	formatters to be applied on the column
    Formatting
    Field Name	Type	Description
    type	string	REQUIRED. Type of formatter
    format	string	REQUIRED. Parameter for the formatting function
    The `format` parameter can accept a string, a list, or a dictionary. Refer below for the exact syntax.

**Available formatters:**
**Date** 
Change format of date strings. 
formatters:
	- type: date
	  format:
      	src: "%m%d%Y"
        des: "%Y-%m-%d"
`src` is the format of the existing column.`des` is the format you want to apply. 
Check out the table at the end of this page for accepted values: https://www.w3schools.com/python/python_datetime.asp 
Float
Change format of decimal numbers. InGen uses python's string format function to apply the format, therefore any valid python format string can be passed. Refer this page to know more about python's format function https://docs.python.org/2/library/string.html#format-specification-mini-language
formatters:
	- type: float
      format: '${:,.2f}'

**Concatenate**
Concatenate multiple columns into a new column and separate it via separator:
      - src_col_name: final_column
        formatters:
          - type: concat
            format: 
			  columns: ['column1','column2','column3']
              separator: '_'
In the above example, a new column ‘final_column' will be created by concatenating values of ‘column1’ , ‘column2’ , ‘column3’ and the would be separated with '_'
Note: if the separator is not provided the columns would be concatenated without it.
Constant
Add a new column with a constant value 
      - src_col_name: "country"
        formatters:
          - type: constant
            format: "India"
In the above example a new column 'country' will be created with the value 'India' for all rows.
**Date Constant**
Add a new column with a date
      - src_col_name: "POS_DATE"
        formatters:
          - type: constant-date
            format: [ 0,  "%Y-%m-%d", "EMPTY" ]
`format` accepts a list with 3 items:
1.	offest - 0 indicates today's date, a positive value will add that number of days to today's date, similarly a negative value. will decrease the date. So use -1 to get yesterday's date
2.	date format 
3.	BLK calendar - <todo: add link to BLK calendar wiki>
**Duplicate Column**
Add a new column. by coying an existing one. 
      - src_col_name: newcolumn
        formatters:
          - type: duplicate
            format: existingcolumn
In the above example, a new column `newcolumn` will be created by copying the values from an existing `existingcolumn` column
**Group Percentage**
      - src_col_name: 'WEIGHT'
        formatters:
          - type: group-percentage
            format:
              of: 'Market Value'
              in: 'Account Number'
In the above example, a new column `WEIGHT` will be created by calculating the percentage of 'Market Value' in 'Account Number'. 
**Sum** 
Adds a new column by adding values of two columns
      - src_col_name: marks
        formatters:
         - type: sum
           format: ['mark1','mark2','mark3']

**Date Diff**
Add a new column by calculating the difference between dates in two columns
      - src_col_name: duration
        formatters:
          - type: date-diff
            format: [ 'sell_date','purchase_date','%Y-%m-%d' ]
The above example adds a new column called 'duration' by calculating the difference between values of 'sell_date' and 'purchase_date'.
**Bucket**
Bucket formatter is used to group numerical values into ranges by creating range intervals called buckets and labelling them. In the below example 'GAIN_LOSS_TYPE' column originally contains non-negative numerical values. We need to group these values into two labels :
1.	short_term: 0 to 365
2.	long_term: >=366 


      - src_col_name: GAIN_LOSS_TYPE
        formatters:
          - type: bucket
            format:
              buckets: [0, 365, inf]
              labels: ['short_term', 'long_term']

**Format options:**
format	description
buckets	REQUIRED. A list representing increasing ranges.  
labels	List of labels to be applied on each bucket range
include_right	'true' or 'false'.  Indicates whether bucketsincludes the rightmost edge or not. If include_right=='true' (the default), then the buckets [1, 2, 3, 4] indicate (1,2], (2,3], (3,4].
Business Day Formatter
Business day formatter is used to add another column named billing date to the input data frame. The input data frame contains 'date' column consisting of some dates. After applying this formatter, a new billing date column will be created, which will contain previous business day for the corresponding date, That is, if the date is a business day, it will give the same date, but if it is a holiday, it will give previous business day. The user can choose the calendar from HolidayCalendar. 

  - src_col_name: date
  - src_col_name: business_date
    formatters:
      - type: bus_day
        format:
            col: 'date'
            format: '%m/%d/%Y'
            cal: 'US'
**Split Formatter**
Takes a column having array values and splits it into multiple columns equal to the number of elements in the array. The user can give the names of new columns and choose which column to display finally. This works on both the list and string type values in the column.
For example, we have a 'Subjects' column in a dataframe containing a list of subjects. This formatter will create a separate column for each subject in that list as follows:
Input Dataframe- 
 
Output Dataframe-
 
-src_col_name: name
-src_col_name: subject
 formatters:
      -type: split_col
       format:
           new_col_names: ['sub1','sub2']
-src_col_name: sub1
-src_col_name: sub2
**Fill Empty value with Custom value**
Replaces the NaN values in a column by a value specified in the config

- src_col_name: grade         
  formatters: 
	- type: fill_empty_values_with_custom_value
      format:
         value: 0
         condition:
           match_col: 'sec_desc'
           pattern: 'CASH'


In the above example, any NaN values in column 'grade' would be replaced by 0 but only for rows where sec_desc value is 'CASH'

**Spacing Formatter**
Adds specific number of spaces within the two columns of a data frame. It takes the number of spaces from the user and adds those on the left side of the column.

- src_col_name: value3
  formatters:
    - type: add_space
      format:
        spacing: 30


**Add Trailing Zeros Formatter**
Adds specific number of leading zeros before all values of a specific data frame column . It takes the number of zeros from the user as a format option.

- src_col_name: value3
   formatters:
     - type: add_trailing_zeros
       format:
         num_of_chars: 13

**Last date of Previous month Formatter**
It creates a new column containing value which is the last date of previous month based on the runtime date given in the cli. The output date is returned in the user desired format. The name of the column is taken as an argument from the user.
- src_col_name: Date1
  formatters:
    - type: last_date_of_prev_month
      format:
        outdate_format: '%Y%m%d'

**replace_value**
Replace value formatter replaces multiple values to another, from_value and to_value are provided along with the column to perform the operation on
in below example, in TRADE_TYPE column, every row with 'BUY' and 'SELL' is replaced by 'O', 'C' respectively.
- src_col_name: 'TRAN_TYPE'
  dest_col_name: 'TRADE TYPE'
  formatters:
    - type: replace_value
       format:
         from_value: ['BUY', 'SELL']
         to_value: ['B', 'S']
**sub_string**
Sub String formatter which gets the sub string from the string type column. In the format option you have to provide start and end index of the string.
In below example, The STRING_COL first character is dropped and the sub string is returned.

      - src_col_name: 'STRING_COL'
        formatters:
          - type: sub_string
            format:
              start: 1


**Arithmetic Operations ( Math Formatter)**
Permitted operations: div, mul, sub, add, abs
The value and cols property are optional and only one of them can exist at a given time
sec_col_name:  is the column on which the results should be saved, if this is a new column, a new column in created in a dataframe, if this is an existing column, it is updated
formatters
   cols: these are the columns on which the operation has to be performed, this has to be an array of more than one column
  value: if specified, this is the constant value which is used in operation, in below case, quantity and sell price are multiplied and then the row is multiplied with 4
you can avoid value field altogether and it would do quantity * sell_price and store it in SALE_VALUE column
similarly, if cols are avoided, it would multiply 4 into SALE_VALUE column
- src_col_name: SALE_VALUE
  formatters:
    - type: arithmetic_calc
      format:
        cols: [ 'quantity','sell_price' ]
        value: 4
        operation: 'mul'

Example of abs:
formatters:
  - type: arithmetic_calc
    format:
      operation: 'abs'
**Encryption**
The Purpose of this formatter is to encrypt PII data using the AES/CTR/NoPadding approach and return a output of a json with Keys : [cipher, nonce, mac]
columns:
      - src_col_name: ACCOUNT_NUMBER
        dest_col_name: ACCOUNT_NUMBER_ENCRYPTED
        formatters:
            - type: encryption
              format: ""

**Decryption**
The Purpose of this formatter is to decrypt PII data using the AES/CTR/NoPadding approach and return a plaintext.
columns:
      - src_col_name: ACCOUNT_NUMBER_ENCRYPTED
        dest_col_name: ACCOUNT_NUMBER
        formatters:
            - type: decryption
              format: ""

**Uuid**
UUID formatter adds a new column in the dataframe with UUID in each row
columns:
  - src_col_name: random_id
    formatters:
      - type: uuid
**Conditional Formatter:**
The purpose of this formatter is  based on a condition replaces the row value with another column value.
The formatter takes following options:
i) column: It's the value of from_column whose value would picked up when the condition provided in the format options is set to true.
ii) condition: It's a dict which takes in match_col which is the column whose value is to be checked and pattern is the value of that matching column.
- src_col_name: 'SHARES'
  formatters:
	- type: conditional_replace_formatter
      format:
      	from_column: 'ORD_DETAIL_FACE'
        condition:
        	match_col: 'TRAN_TYPE'
            pattern: 'C'
1.2.3.1.21. float_precision
used to specify decimal precision on numerical columns. The format used is common python format
- src_col_name: 'price'
  formatters:
	- type: float_precision
      format:
      	precision: 2
Drop duplicate rows
The purpose of this formatter is to drop rows with duplicate ID values from a dataframe. In the format option, there are three possible values to keep certain duplicates:
•	'first': keeps the first duplicate row
•	'last'; keeps the last duplicate row
•	False: drops all of the duplicate rows
'first' is the default option.
- src_col_name: unique_id
  formatters:
    - type: drop_duplicates
      format:
        keep: 'last'

**Prefix_string**
The purpose of this formatter is to append string and multiple column data into a single column
The following example concatenates "161"+fc_ofc_no + fc_no 

 - src_col_name: 'Unique_ID__c'
   formatters:
     - type: prefix_string
       format:
         columns: [ 'fc_ofc_no', 'fc_no' ]
         prefix: '161'

**Validations**
Field Name	Type	Description
type	string	REQUIRED. Type of validation.
severity	string	OPTIONAL. Severity of the validation result.
args	list	OPTIONAL. List of arguments for expectations.
The 'severity' parameter accepts one of 'blocker', 'critical' and 'warning' value. These values defines what actions needs to be taken after receiving validation result.
'blocker' defines we exit out of the application after getting column value that fails validation.
'critical' removes the rows of the data corresponding to column values that fails validation.
'warning' just displays column values that fails validation.

**Available validations:**
**Inbuilt Validations**
These are the validations that are part of great_expectations library.
expect_column_values_to_not_be_null
Validate whether all column values are not null.
validations:
  - type: expect_column_values_to_not_be_null
    severity: "warning"

expect_column_values_to_match_regex_list
Expect the column entries to be strings that can be matched to either any of or all of a list of regular expressions.
validations:
  - type: expect_column_values_to_match_regex_list
    severity: "warning"
    args: [["^[0-9]*[.][0-9]+$"],any]
'args' takes the list of all regular expressions that is needed to check against column values, there is also optional parameter (any, all) that decides whether to match all the regex or just any one of them.

expect_column_values_to_match_strftime_format
Expect column entries to be strings representing a date or time with a given format.
validations:
  - type: expect_column_values_to_match_strftime_format
    severity: "warning"
    args: ["%Y-%m-%d"]
'args' takes a strftime format string to use for matching column values.

expect_column_values_to_be_between
Expect column entries to be between a minimum value and a maximum value.
validations:
  - type: expect_column_values_to_be_between
    severity: "warning"
    args: [10,20]
'args' takes two values -
'min_value' takes minimum value for a column entry.
'max_value' takes maximum value for a column entry.

expect_column_values_to_be_unique
Expect each column value to be unique. This expectation detects duplicates. All duplicated values are counted as exceptions.
validations:
  - type: expect_column_values_to_be_unique
    severity: "warning"

expect_column_value_lengths_to_equal
Expect column entries to be strings with length equal to the provided value. This expectation only works for string-type values. Invoking it on ints or floats will raise a TypeError.
validations:
  - type: expect_column_value_lengths_to_equal
    severity: "warning"
    args: [8]
'args' takes the expected value for a column entry length.

Custom Validations
These are the expectations that are not present in great_expectations library.
expect_column_to_contain_values
Expect column entries to contain the provided value.
validations:
  - type: expect_column_to_contain_values
    severity: "warning"
    args: [["XUSD0000", "ABC1234F"]]
'args' takes the list of expected values to check its presence in the column.

expect_column_values_to_be_of_type
Expect column entries to be parseable (type casted) to provided type.
validations:
  - type: expect_column_values_to_be_of_type
    severity: "warning"
    args: ["float"]
'args' takes a string representing the data type that each column should have as entries. Valid data types include 'str', 'int', 'float'.

expect_column_to_be_present_in
Expects all column values to be present in all columns of sources provided.
validations:
  - type: expect_column_to_be_present_in
    severity: "warning"
    args: [[COL_2, cusip], [COL_3,cusip]]
'args' takes list of all sources along with the column name, in which we need to check whether all values of current column are present.

Output
The output object is used to declare how the output data should be persisted. The following code snippet shows an example of storing data into an excel file:
output:
	type: excel
	props:
		path: 'path/to/write/file.xls'
The 'type' field can take two values:
•	excel - for Excel sheets
•	file - for any delimited files like csv, psv, etc
The following example declares a CSV output
output:
	type: file
	props:
		delimiter: ','
		path: 'path/to/write/file.xls'

**Header & Footer**
CSV files by default do not write the column names in the file. To add the column names in the output file an extra property called 'header'/'footer' should be provided in the output. 
output:
	type: file
	props:
		delimiter: ','
		path: 'path/to/write/file.xls'
		header:
			type: delimited_result_header


**Custom Header/Footer**
To have custom footer/headers in the output csv files, header/footer are initialised with type = 'custom' . Different custom values can be achieved using this. There are 5 custom functions which can be used to get the header/footer of the output file.
constant 
Takes a string as input and adds the constant string as a header/footer.
filler
Takes integer as input and adds the string containing equivalent number of empty spaces to header/footer.
get_new_line
Takes boolean input from the user and if true, adds a new line after any value.
col_sum
Takes column name as input and returns the sum of values of that column.
sum_of_substr
Takes column name, starting index, ending index for the substring, and the number of characters from the user, and returns the sum of all substring values of that column. The number of characters is the total characters user wants in the final output. The extra characters apart from sum value are fulfilled by leading zeros. 
Field Name	Type	Description
col_name	string	column on which user wants to apply this function
start	int	Starting index to get substring
end	int	Ending index to get substring
char_count	int	Total characters in the final result
last_date_of_prev_month
Takes date format as input and returns the last date of previous month based on the runtime date given in the cli.
first_date_of_current_month
Takes date format as input and returns the first date of current month based on the runtime date given in the cli.
row_count
Takes dictionary as input which refers to left padding needed(for eg if padding is 4, 10 is displayed as 0010.) and adds the number of records in the output file +  header count+ footer count to header/footer of output file.
Field Name	Type	Description
left_padding	integer	left padding needed(for eg if padding is 4, 10 is displayed as 0010.)
header	bool
Int	true indicates to include header count in the total count and add 1.
Add the int value to the total row count.
footer	bool
int	true indicates  to include footer count in the total count and add 1.
Add the int value to the total row count.
date
Takes the date format as input and adds today's date to header/footer.
run_date
Takes the date format as input and adds the run_date(date used in cli) to header/footer.
These custom functions can be used together to generate the header/footer as required. In the functions tag  we need to mention the custom functions in the order you need them in the header/footer. Therefore in below case the 
resultant header = constant + filler + constant + run_date =  H          MRC20211203
resultant footer = constant + row_count(with left padding as 7 and include header + include footer) = TRECORD COUNT0000010

output:
      type: delimited_file
      props:
        delimiter: ','
        path: 'C:\interfacegenerator\output\test_file.csv'
        header:
          type: custom
          function:
            - constant: UHDR
            - last_date_of_prev_month:
                dt_format: '%Y%j'
            - add_new_line: true
            - constant: FileTitle=TransactionsVER44
            - filler: 10
            - first_date_of_current_month:
                dt_format: '%m/%d/%Y'
            - constant: GAMUT
            - add_new_line: true
            - filler: 231
            - constant: X

        footer:
          type: custom
          function:
            - constant: 'NumberOfRecords='
            - row_count:
                left_padding: 7
                header: false
                footer: false
            - constant: 'TotalAmount='
            - sum_of_substr:
                start: 26
                end: 39
                col_name: concatenated_col
                char_count: 18
            - add_new_line: true
            - filler: 231
            - constant: X
            - add_new_line: true
            - constant: UTRL
            - filler: 1
            - row_count:
                left_padding: 7
                header: false
                footer: false

**Split File Writer**
Split File allows the final data to be written in chunks to multiple file(s) based on a column, the type should be 'splitted_file' and the props should contain configuration for each file with 2 additional columns, viz. `col` and `value`. Apart from this the run_config at the end of the file should have `writer: SplitFileWriter`
output:
  type: 'splitted_file'
  props:
    - col: 'TYPE'
      value: 'BLK'
      type: delimited_file
      props:
        header:
          type: delimited_result_header #/custom
        delimiter: ','
        path: '/PATH/output/FILE.csv'

...
...

run_config:
  generator: InterfaceGenerator
  writer: SplitFileWrite



**Dataframe Writer**
The data frame writer allows us to write data in the form of dataframes directly into the memory without creating multiple interface files. The dataframe can come from any source such as a file, database, etc. It takes an Id that user wants to give to the data frame and writes both of them into the Store dictionary in the form of key-value pairs. The data frame reader can then read the desired dataframe based on the given ID. We also have to give the column names of the dataframe.
In the below sample YAML, the column names are- Name and Gender and the dataframe is being read from a .csv file - sampledf.csv. Here, we are checking if the writer writes the actual key-value pair properly using reader. first we will write, and then read that dataframe using the ID- DF2.
interfaces:
  Dataframewriter:
    sources: [DF1]
    output:
      type: rawdatastore
      props:
        id: DF2
    columns:
      - src_col_name: Name
      - src_col_name: gender

  Dataframefinal:
    sources: [DF2]
    output:
        type: delimited_file
        props:
            delimiter: ','
            path: PATH\sampledf2.csv
            header:
              type: delimited_result_header
    columns:
      - src_col_name: Name
      - src_col_name: gender

sources:
  - id: DF1
    type: file
    file_type: delimited_file
    delimiter: ','
    file_path: PATH\sampledf.csv
    columns: [ Name, gender]
    skip_header_size: 1

  - id: DF2
    type: rawdatastore

 
**JSON Writer**
JSON Writer can be used to transform the data stored in a dataframe into JSON format and then store in a file or can be sent to an API as request body. There can be different ways to transform a dataframe into JSON. Currently, InGen provides two convertors - i) Single and ii) Multiple. The choice of convertor can be declared in the YAML config as shown in the below example. In a similar way, the destination, i.e where to send the JSONs can be declared in the config file. There are two possible destinations - i) File and ii) API. 
JSON Writer accepts four top-level configs:
output:
	type: json_writer
	props:
		convertor: ...
		convertor_props: ...
		destination: ...
		destination_props: ...
 Converter: 
Converters are used to convert the dataframes into JSONs. Users can declare the converter function they want to use and also pass the properties that the function needs. 
Single converter
JSON writer allows the final output dataframe to be written as a JSON file on the configured path. This writer works with two optional arguments.
1.	Indent(int) to define the indentation of the JSON in terms of spaces. 
2.	Orient decides the orientation of the JSON document.
1.	The orient options are : 
	‘split’ : dict like {‘index’ -> [index], ‘columns’ -> [columns], ‘data’ -> [values]}
	‘records’ : list like [{column -> value}, … , {column -> value}]
	‘index’ : dict like {index -> {column -> value}}
	‘columns’ : dict like {column -> {index -> value}}
	‘values’ : just the values array
	‘table’ : dict like {‘schema’: {schema}, ‘data’: {data}}
Describing the data, where data component is like orient='records'.
3.	column_details: We need to provide schema for the writer here under the schema.
a.  The schema order of columns should be sequential such that the column on which the operation is required already exists/built-up in dataframe
      1. field_name: the resultant column to be generated.
      2. field_type: the type of data the field can have
      3. field_attr: The attributes the field is supposed to have.
      4. field_action: the action that needs to be performed in the field, in case we are using group_by or sum we need to provide the field_agg_column
      5. field_agg_column: the column which will contain the aggregated data.
      6. field_total: to be set when using the field action as 'sum'
      7. field_action_column: the column where the actions are to be performed.

interfaces:
  sec_master:
    sources: [ 'encryption_bt' ]
    output:
      type: json_writer
      props:
        convertor: single
		convertor_props:
        	config:
          	orient: 'records'
          	indent: 3
            column_details:
  	          schema: #order of columns should be sequential such that the column on which the operation is required already exists/built-up in dataframe
    	          - field_name: accounts
        	        field_type: dict
            	    field_attr: [ accountName, accountNumber, registrationType, custodian, product, pkg, accountId, accountBaseMarketValue ]
                	field_action: groupby #if groupBy , define aggregation column too
	                field_action_column: advisorId
    	            field_agg_column: accounts
        	      - field_name: asOfDate
            	    field_type: date
                	field_attr: YYYY-MM-DD #not used
	              - field_name: clientsSummary
    	            field_type: dict
        	        field_attr: [ asOfDate, accounts ]
            	    field_action: sum
                	field_action_column: accountBaseMarketValue
                	field_agg_column: accounts
	                field_total: totalAccountBaseMarketValue
    	          - field_name: accountName
        	        field_type: str
            	resultant_columns: [ advisorId, clientsSummary ]
		destination: file
		destination_props:
			path: 'output/positions.json'
    columns:
      - src_col_name: "start_date"
        dest_col_name: "START DATE"
...
...
run_config:
  generator: InterfaceGenerator

The above YAML for json_writer is equivalent to old JSON writer as shown below.
interfaces:
  sec_master:
    sources: [ 'encryption_bt' ]
    output:
      type: json
      props:
        path: 'output/positions.json'
        config:
          orient: 'records'
          indent: 3
          column_details:
            schema: #order of columns should be sequential such that the column on which the operation is required already exists/built-up in dataframe
              - field_name: accounts
                field_type: dict
                field_attr: [ accountName, accountNumber, registrationType, custodian, product, pkg, accountId, accountBaseMarketValue ]
                field_action: groupby #if groupBy , define aggregation column too
                field_action_column: advisorId
                field_agg_column: accounts
              - field_name: asOfDate
                field_type: date
                field_attr: YYYY-MM-DD #not used
              - field_name: clientsSummary
                field_type: dict
                field_attr: [ asOfDate, accounts ]
                field_action: sum
                field_action_column: accountBaseMarketValue
                field_agg_column: accounts
                field_total: totalAccountBaseMarketValue
              - field_name: accountName
                field_type: str
            resultant_columns: [ advisorId, clientsSummary ]

    columns:
      - src_col_name: "start_date"
        dest_col_name: "START DATE"
...
...
run_config:
  generator: InterfaceGenerator

**Multiple converter**
'Multiple' converter is mostly used with API destination. You can pass a JSON template to a 'multiple' converter where some fields are to be set dynamically. The dynamic fields in the template will be replaced by the column values of one row of the dataframe. So, if there are 'n' rows in the dataframe, a list of 'n' json strings will be created. Consider a dataframe like this:
name	marks
Amit	35
Arya	45

and a json template like this:
{"name": "<name>", "subject": "maths", "marks": <marks>}

'multiple' json converter will create two json strings like this
{"name": "Amit", "subject": "maths", "marks": 35}
{"name": "Arya", "subject": "maths", "marks": 45}
Destination
A converter produces a list of JSON strings that are ready to be written to a file or to be sent as request payload to an API. 
File destination
 Writes the JSON string to a file.
 API Destination
For each row (or each JSON string in the list created by the converter) a single API call is made as per the given configuration. The result of the API call is written to the dataframe store. (InMemory). 

Sample API destination and its props:
          destination: api
          destination_props:
            api_request_props:
              url: https://tst.blackrock.com/api/...
              method: post
              headers:
                Content-Type: "application/json"
                VND.com.blackrock.API-Key: "..."
              auth:
                type: BasicAuth
                user: ''
                password: ''
              success_criteria: 'status_criteria'
              criteria_options:
                status: 200
              interval: 2
              retries: 3
              tasks_len: 10
              queue_size: 10
            api_response_props:
              type: dataframe
              dataframe_id: long_running_ids
              data_key: [id]
              data_node: ...
              meta: ...
Most of the YAML params are similar to API source params. The only difference here is that they are grouped into 'api_request_props' and 'api_response_props'. See API source for the definition of the parameters.

**JSONReader:**
JSON Reader helps to read a json file and convert it to CSV file. It generates csv on the basis of column names we provide in the yml file.
Yaml code that helps to convert json to csv
interfaces:
  proposal_id:
    sources: [proposals]
    output:
      type: delimited_file
      props:
        header:
          type: delimited_result_header
        delimiter: ','
        path: '/PATH/reader/sample_output.csv'
    columns:
      - src_col_name: id
        dest_col_name: PORTFOLIO_ID
      - src_col_name: cusip
        dest_col_name: CLIENT_ID
      - src_col_name: marketValue
        dest_col_name: MKT_VALUE_BASE
      - src_col_name: posInfo.SLEEVE_ID
        dest_col_name: SLEEVE_ID
      - src_col_name: quantity
        dest_col_name: POS_CUR_PAR


sources:
  - id: proposals
    type: file
    file_type: json
    file_path: '/PATH/InterfaceGenerator/reader/sample.json'
    record_path: positions
    meta: ["id", "cash_allocation"]
    meta_prefix: position

Attaching the input (json) and output (csv) files

          
**XMLReader:**
Xml Reader helps to read an xml file and convert it to CSV file. It generates csv on the basis of column names we provide in the yml file. We also have to provide the root tag in the yml itself which is the main tag which has sub tags and its data.
The xml can either has a text or an attribute.
eg: <CUSIP>123456789</CUSIP>
      <ASSIGNED_TO name="TRADER">TRADER</ASSIGNED_TO>
In this example cusip tag has text with value 123456789 and assigned_to tag has attribute and text both. The attribute name has value "TRADER".
interfaces:
  proposal_batcher_input:
    sources: [input_account]
    output:
      type: delimited_file
      props:
        header:
          type: delimited_result_header
        path:  input/CSVFROMXML.csv
    columns:
      - src_col_name: 'CUSIP'
      - src_col_name: 'PORTFOLIO_NAME'
        dest_col_name: 'PORTFOLIO_NAME'
      - src_col_name: 'ORD_DETAIL_FUND'
        dest_col_name: 'ORD_DETAIL_FUND'
      - src_col_name: 'ASSIGNED_TO@id'
        dest_col_name: 'ASSIGNED_TO'
      - src_col_name: 'MODIFIED_BY.@name'
        dest_col_name: 'MODIFIED_BY'
      - src_col_name: 'TRAN_TYPE'
     

sources:
    - id: input_account
      type: file
      file_type: xml
      delimiter: ','
      file_path: input/MF.20211022.xml
      columns : [
      'CUSIP',
      'PORTFOLIO_NAME',
      'ORD_DETAIL_FUND',
      'ASSIGNED_TO.@id',
      'MODIFIED_BY.@name',
      'TRAN_TYPE'
      ]
      root_tag: 'ORDER'


The important thing to note here is that nested tags can be accessed via '.' operator. The other thing to note is to the attribute tag is accessed via '.@' operator. 
Some tags have multiple nested tags for them 2 rows would be created in CSV with the duplicate data from the parent tag.

drop_null
For JSON input and output, the number of columns in the configuration file may exceed the number of columns in the JSON payload. This means that the extra configuration columns will be populated with null values. To only account for the payload columns, there's a drop_null flag under output's props. Said flag will drop the extra configuration columns from the JSON output.
interfaces:
  json_sample:
    sources: [json_payload]
    columns:
      - src_col_name: 'Account__c'
        dest_col_name: 'Account__target'
      - src_col_name: 'Type__c'
        dest_col_name: 'Type__target'
      - src_col_name: 'Status__c'
        dest_col_name: 'Status__target'
      - src_col_name: 'Platform__c'
        dest_col_name: 'Platform__target'
      - src_col_name: 'Date__c'
        dest_col_name: 'Date_target'
    output:
      props:
        drop_null: true
sources:
  - id: json_payload
    type: json



**Interpolators**
Interpolator functions can be used at various places in the YAML to add dynamic content in a string. Like adding token values or dates in file paths or HTTP headers. An interpolator function is written in following form:
$function_name(args)
`function_name` is the name of the interpolator function
`args` is the argument passed to the interpolator function

Supported interpolators:
Interpolator function	Argument	Detail	Example
date*	format of date	Returns a date string in the given format	$date(%Y%m%d)
token	token name	Returns the token value for the given token	$token(TOKEN_NAME)
token_secret	token name containing the path of the secret file	Reads the token value to get the path of the secret file and decrypts its content using tsgops private keys	$token_secret(TOKEN_NAME)
timestamp	format of date	Takes the date format and returns the current timestamp	$timestamp(FORMAT)
uuid	NA	Generates random UUID using uuid4() inbuilt function	$uuid()
*only available in file path names






## Contributing

Guidelines for contributing to the project. link to CONTRIBUTING.md and CODE_OF_CONDUCT.md

## License

The license for the project. Lint to the LICENSE file in the root

## Credits

Acknowledgements for any contributors, libraries, or resources.

## Contact

Contact information for questions or feedback.
