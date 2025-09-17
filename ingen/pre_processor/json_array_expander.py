import pandas as pd
import json
import logging

from ingen.pre_processor.process import Process

log = logging.getLogger()


class JsonArrayExpander(Process):

    def execute(self, config, sources_data, data):
        """
        Expands JSON arrays in a specified column into multiple rows (cartesian product).
        For each JSON array, creates separate rows for each object while preserving existing columns.
        The JSON column is replaced with new columns from the parsed JSON objects.
        
        :param config: Configuration dictionary containing:
                      - 'column': column name with JSON strings (required)
                      - 'include_columns': dict mapping JSON keys to output column names, or list of keys (optional)
                      - 'exclude_columns': list of JSON keys to exclude (optional)
        :param sources_data: Source data dictionary (not used)
        :param data: The input DataFrame containing JSON strings
        :return: A DataFrame with expanded rows and new columns from JSON data
        """
        if config is None:
            raise ValueError("Configuration is required for JsonArrayExpander")
        
        # Handle nested configuration structure - check both 'config' and 'format' keys
        if 'config' in config and isinstance(config['config'], dict):
            format_config = config['config']
        else:
            format_config = config.get('format', config)
        
        column = format_config.get('column')
        if not column:
            raise ValueError(f"Column configuration not found. Config: {config}")
        
        if column not in data.columns:
            raise ValueError(f"Column '{column}' not found. Available columns: {list(data.columns)}")
        
        # Get column filtering options
        include_columns = format_config.get('include_columns', [])
        exclude_columns = format_config.get('exclude_columns', [])
        
        return self.expand_json_array(data, column, include_columns, exclude_columns)

    def expand_json_array(self, dataframe, column, include_columns, exclude_columns):
        """
        Expands JSON arrays in the specified column into multiple rows.
        """
        # Performance: Early return for empty dataframe
        if dataframe.empty:
            return dataframe.copy()
            
        all_keys = self._collect_all_json_keys(dataframe, column)
        filtered_keys = self._apply_column_filters(all_keys, include_columns, exclude_columns)
        
        # Performance: Use list comprehension with generator for memory efficiency
        expanded_rows = list(self._create_expanded_rows_generator(dataframe, column, filtered_keys, include_columns))
        
        # Edge case: Return original dataframe if no expansion occurred
        if not expanded_rows:
            return dataframe.copy()
            
        return pd.DataFrame(expanded_rows)
    
    def _collect_all_json_keys(self, dataframe, column):
        """
        Collects all unique keys from JSON objects across all rows.
        Performance optimized with vectorized operations where possible.
        """
        all_keys = set()
        
        # Performance: Filter non-null values first to avoid unnecessary iterations
        valid_json_series = dataframe[column].dropna()
        valid_json_series = valid_json_series[valid_json_series.astype(str).str.strip() != '']
        
        for json_str in valid_json_series:
            try:
                json_array = json.loads(str(json_str))
                # Edge case: Handle non-list JSON values
                if not isinstance(json_array, list):
                    log.warning(f"Expected JSON array, got {type(json_array).__name__}. Skipping.")
                    continue
                    
                for json_object in json_array:
                    # Edge case: Handle non-dict objects in array
                    if isinstance(json_object, dict):
                        all_keys.update(json_object.keys())
                    else:
                        log.warning(f"Expected dict object in JSON array, got {type(json_object).__name__}. Skipping object.")
                        
            except (json.JSONDecodeError, TypeError) as e:
                log.warning(f"Failed to parse JSON '{json_str}': {e}")
                
        return all_keys
    
    
    def _apply_column_filters(self, all_keys, include_columns, exclude_columns):
        """
        Applies include/exclude filters to the collected keys.
        Edge case: Validates filter conflicts and empty results.
        """
        # Edge case: Validate conflicting filters
        if include_columns and exclude_columns:
            log.warning("Both include_columns and exclude_columns specified. Using include_columns only.")
            
        if include_columns:
            # Handle include_columns as either dict (mapping) or list
            if isinstance(include_columns, dict):
                # Use the keys from the mapping
                include_keys = set(include_columns.keys())
            else:
                # Treat as list of keys
                include_keys = set(include_columns)
                
            filtered_keys = include_keys & all_keys
            # Edge case: Warn if no keys match include filter
            if not filtered_keys:
                log.warning(f"No keys found matching include_columns: {include_columns}")
            return filtered_keys
        elif exclude_columns:
            filtered_keys = all_keys - set(exclude_columns)
            # Edge case: Warn if all keys excluded
            if not filtered_keys:
                log.warning(f"All keys excluded by exclude_columns: {exclude_columns}")
            return filtered_keys
            
        return all_keys
    
    def _create_expanded_rows_generator(self, dataframe, column, filtered_keys, include_columns):
        """
        Generator that yields expanded rows for memory efficiency.
        Handles edge cases for malformed data and empty arrays.
        """
        # Performance: Pre-compute column list to avoid repeated operations
        # Use all columns except the JSON column
        other_columns = [col for col in dataframe.columns if col != column]
        
        for _, row in dataframe.iterrows():
            json_str = row[column]
            base_row = {col: row[col] for col in other_columns}
            
            # Delegate row processing to reduce complexity
            yield from self._process_single_row(json_str, base_row, filtered_keys, include_columns)
    
    def _process_single_row(self, json_str, base_row, filtered_keys, include_columns):
        """
        Processes a single row's JSON string and yields expanded rows.
        Separated to reduce cognitive complexity.
        """
        # Edge case: Handle null, empty, or whitespace-only strings
        if self._is_invalid_json_string(json_str):
            yield self._create_empty_row(base_row, filtered_keys, include_columns)
            return
            
        try:
            json_array = json.loads(str(json_str))
            yield from self._process_json_array(json_array, base_row, filtered_keys, include_columns)
        except (json.JSONDecodeError, TypeError) as e:
            log.warning(f"Failed to parse JSON '{json_str}': {e}. Creating empty row.")
            yield self._create_empty_row(base_row, filtered_keys, include_columns)
    
    def _is_invalid_json_string(self, json_str):
        """Check if JSON string is invalid (null, empty, or whitespace-only)."""
        return pd.isna(json_str) or not str(json_str).strip()
    
    def _process_json_array(self, json_array, base_row, filtered_keys, include_columns):
        """
        Processes a parsed JSON array and yields expanded rows.
        """
        # Edge case: Handle non-list JSON values
        if not isinstance(json_array, list):
            log.warning(f"Expected JSON array, got {type(json_array).__name__}. Creating empty row.")
            yield self._create_empty_row(base_row, filtered_keys, include_columns)
            return
            
        # Edge case: Handle empty arrays
        if not json_array:
            log.debug("Empty JSON array found. Creating empty row.")
            yield self._create_empty_row(base_row, filtered_keys, include_columns)
            return
            
        # Process each object in the array
        for json_object in json_array:
            yield self._create_row_from_json_object(json_object, base_row, filtered_keys, include_columns)
    
    def _create_empty_row(self, base_row, filtered_keys, include_columns):
        """
        Creates an empty row with None values for filtered keys.
        Performance optimized with dict operations.
        """
        # Performance: Use dict constructor and update for efficiency
        new_row = dict(base_row)
        
        # Handle column mapping if include_columns is a dict
        if isinstance(include_columns, dict):
            # Use mapped column names
            for json_key in filtered_keys:
                output_col = include_columns.get(json_key, json_key)
                new_row[output_col] = None
        else:
            # Use original key names
            new_row.update({key: None for key in filtered_keys})
        return new_row
    
    def _create_row_from_json_object(self, json_object, base_row, filtered_keys, include_columns):
        """
        Creates a single expanded row from a JSON object.
        Handles edge cases for non-dict objects and nested data.
        """
        # Performance: Use dict constructor for faster copying
        new_row = dict(base_row)
        
        # Initialize columns with None values
        self._initialize_row_columns(new_row, filtered_keys, include_columns)
        
        # Edge case: Handle non-dict objects in JSON array
        if not isinstance(json_object, dict):
            log.warning(f"Expected dict object, got {type(json_object).__name__}. Using empty values.")
            return new_row
            
        # Populate with actual values from JSON object
        self._populate_row_values(new_row, json_object, filtered_keys, include_columns)
        return new_row
    
    def _initialize_row_columns(self, new_row, filtered_keys, include_columns):
        """
        Initialize row columns with None values based on column mapping configuration.
        """
        if isinstance(include_columns, dict):
            # Initialize all mapped column names with None
            for json_key in filtered_keys:
                output_col = include_columns.get(json_key, json_key)
                new_row[output_col] = None
        else:
            # Initialize all filtered keys with None
            new_row.update({key: None for key in filtered_keys})
    
    def _populate_row_values(self, new_row, json_object, filtered_keys, include_columns):
        """
        Populate row with actual values from JSON object.
        """
        for key, value in json_object.items():
            if key in filtered_keys:
                output_col = self._get_output_column_name(key, include_columns)
                new_row[output_col] = self._process_json_value(value)
    
    def _get_output_column_name(self, key, include_columns):
        """
        Determine the output column name based on include_columns configuration.
        """
        if isinstance(include_columns, dict):
            return include_columns.get(key, key)
        return key
    
    def _process_json_value(self, value):
        """
        Process JSON value, converting nested objects/arrays to strings if needed.
        """
        if isinstance(value, (dict, list)):
            return json.dumps(value) if value else None
        return value
