//  Output `props` descriptors for all writer types supported by the InGen backend.
//  Derived from ingen/writer/ — InterfaceWriter (delimited_file, excel),
//  JsonWriter (json_writer), and SplitFileWriter (splitted_file).
//  output.type is the discriminator; these schemas cover the output.props body.

const HEADER_FIELD = {
  key: 'header', label: 'Header', kind: 'group', fields: [
    { key: 'type', label: 'Type', kind: 'select', options: ['delimited_result_header', 'custom'] },
  ],
};

export const OUTPUT_SCHEMAS = {
  delimited_file: {
    label: 'Delimited file',
    schema: [
      { key: 'path', label: 'Path', kind: 'text', placeholder: 'out/file_$date(%Y%m%d).csv' },
      { key: 'delimiter', label: 'Delimiter', kind: 'text', placeholder: ',' },
      { key: 'encoding', label: 'Encoding', kind: 'text', placeholder: 'utf-8' },
      HEADER_FIELD,
      { key: 'footer', label: 'Footer', kind: 'group', fields: [
        { key: 'type', label: 'Type', kind: 'text', placeholder: 'custom' },
      ] },
    ],
  },

  excel: {
    label: 'Excel',
    schema: [
      { key: 'path', label: 'Path', kind: 'text', placeholder: 'out/report_$date(%Y%m%d).xlsx' },
      { key: 'sheet_name', label: 'Sheet name', kind: 'text', placeholder: 'Sheet1' },
      HEADER_FIELD,
    ],
  },

  json_writer: {
    label: 'JSON writer',
    schema: [
      { key: 'convertor', label: 'Convertor', kind: 'select', options: ['json', 'custom'], help: 'How to convert the DataFrame to JSON' },
      { key: 'convertor_props', label: 'Convertor props', kind: 'json', rows: 3, help: 'Convertor-specific configuration (e.g. orient, columns)' },
      { key: 'destination', label: 'Destination', kind: 'select', options: ['file', 'api'], help: 'Where to write the JSON output' },
      { key: 'destination_props', label: 'Destination props', kind: 'group', fields: [
        { key: 'path', label: 'File path', kind: 'text', placeholder: 'out/file.json', help: 'Required when destination = file' },
        { key: 'url', label: 'API URL', kind: 'text', help: 'Required when destination = api' },
        { key: 'method', label: 'HTTP method', kind: 'select', options: ['POST', 'PUT', 'PATCH'] },
        { key: 'headers', label: 'Headers', kind: 'json', rows: 2 },
        { key: 'api_request_props', label: 'API request props', kind: 'json', rows: 2, help: 'Request configuration for API destinations' },
        { key: 'api_response_props', label: 'API response props', kind: 'json', rows: 2, help: 'Response handling for API destinations' },
      ] },
    ],
  },

  // NOTE: splitted_file is intentionally omitted. The backend SplitFileWriter expects output.props
  // to be an *array* of { col, value, type, props } entries — a shape the current SchemaForm
  // cannot represent. splitted_file configs remain fully settable via raw YAML.
};

export const OUTPUT_TYPE_OPTIONS = Object.keys(OUTPUT_SCHEMAS);

export function outputSchema(type) {
  return OUTPUT_SCHEMAS[type]?.schema ?? [];
}
