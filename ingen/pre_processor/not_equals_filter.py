import pandas as pd

from ingen.pre_processor.process import Process 

class NotEqualsFilter(Process): 

    """
        Filter pre_processor that excludes roes where column values match specified values. 
        This is the inverse of the standard 'filter' preprocessor.

        Usage in YAML: 
            pre_processing: 
            - type: not_equals_filter
              source: <source>
              cols: 
                - col: <column_name>
                  val: ["value_to_exclude]

        This will keep all rows where <column_name> is NOT in ["value_to_exclude]
    """
    def execute(self, config, sources_data, data):
        source = config.get('source')
        cols = config.get('cols', [])
        
        #Get source data or use current data 
        if source and source in sources_data:
            df = sources_data.get(source)
        else: 
            df = data 
        
        if df is None or df.empty:
            return pd.DataFrame()
        
        return self.not_equals_filter(df, cols)

    def not_equals_filter(self, data, cols):
        """
        Filter out rows where column values match any of the specified values

        Args:
            data: pandas Dataframe
            cols: list of dicts with 'col' (column name) and 'val' (list of values to exclude)

        Returns:
            Dataframe with rows excluded where column matches any specified values
        """
        if not cols:
            return data

        mask = pd.Series([True] * len(data), index=data.index)

        for col_config in cols:
            col_name = col_config.get('col')
            values_to_exclude = col_config.get('val', [])

            if col_name not in data.columns:
                continue
            
            # Exclude rows where column value is in the exclusion list
            # Using ~isin() to get NOT IN behavior 
            mask &= ~data[col_name].isin(values_to_exclude)

        return data[mask].reset_index(drop=True)