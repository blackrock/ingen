# Example: Convert XML into CSV (or excel)

XML files are commonly used for data extraction because they are readable by both humans and machines. However, their verbosity can make large XML files challenging to comprehend. Additionally, you might not need all the information in the XML file and only want to focus on specific points. InterfaceGenerator (InGen) can help with this by enabling you to convert an XML file into a more manageable CSV format.

Let's imagine a scenario where we have an XML file filled with customer data. Each customer's data is represented as an XML node, which includes their customer ID, name, and email. Additionally, there's a nested node within each customer's node that contains their address details, such as street, city, state, and country.

```
<?xml version="1.0" encoding="UTF-8"?>
<customers>
  <customer>
    <id>1</id>
    <name>John Doe</name>
    <email>johndoe@example.com</email>
    <address>
      <street>123 Main St</street>
      <city>Anytown</city>
      <state>AnyState</state>
      <country>USA</country>
    </address>
  </customer>
  <customer>
    <id>2</id>
    <name>Jane Doe</name>
    <email>janedoe@example.com</email>
    <address>
      <street>456 Main St</street>
      <city>Anytown</city>
      <state>AnyState</state>
      <country>China</country>
    </address>
  </customer>
  <customer>
    <id>3</id>
    <name>Bob Smith</name>
    <email>bobsmith@example.com</email>
    <address>
      <street>789 Main St</street>
      <city>Anytown</city>
      <state>AnyState</state>
      <country>India</country>
    </address>
  </customer>
</customers>
```

In this XML file there are details of three customers, let us say we want to convert this into a CSV file and only need their `id`, `name` and the `country`. Notice that `country` is field inside the `address` node.

Create an InGen config file and open it in your favourite text editor

```
touch customers_xml_to_csv.yaml
```

Let's start by defining our data source - the customers XML file

```
sources:
    - id: customer_data
      type: file
      file_type: xml
      file_path: /Users/piyushranjan/customers.xml
      root_tag: 'customer'
      columns: ['id', 'name', 'address.country']
```
The above snippet declares a XML File source stored at `/Users/piyushranjan/customers.xml` location. The `root_tag` is the name of the elements node within the XML document. `columns` are the field names that we want to read from the XML file. Here we extracting `id` and `name` fields directly, and the `country` field from within the `address` tag.

Now let's define the interface (the CSV file that we want as an output)

```
interfaces:
    customers:
        sources: [customer_data]
        output:
            type: delimited_file
            props:
                header:
                    type: delimited_result_header
                path: /Users/piyushranjan/customers.csv
        columns:
            - src_col_name: id
            - src_col_name: name
            - src_col_name: address.country
```

In this section, we're setting up an interface named `customers`. This interface is based on a single data source, `customer_data`, which we've previously defined. The output is set to be a delimited file, which is a CSV file by default.

The `delimited_result_header` option will add a header row to the CSV file. This header row will contain the names of the columns.

The `path` option specifies the location where the CSV file will be saved.

The `columns` option is a list of the columns that we want to include in the CSV file. Each `src_col_name` should match one of the column names in the data source.

Here's the full configuration file:

```
interfaces:
    customers:
        sources: [customer_data]
        output:
            type: delimited_file
            props:
                header:
                    type: delimited_result_header
                path: /Users/piyushranjan/customers.csv
        columns:
            - src_col_name: id
            - src_col_name: name
            - src_col_name: address.country

sources:
    - id: customer_data
      type: file
      file_type: xml
      file_path: /Users/piyushranjan/customers.xml
      columns: ['id', 'name', 'address.country']
      root_tag: 'customer'
```

Now let us run ingen and provide this config as input:

```
python -m ingen customers_xml_to_csv.yaml
```

If everything works fine, a new CSV file will be created with following content

```
id,name,address.country
1,John Doe,USA
2,Jane Doe,China
3,Bob Smith,India
```
