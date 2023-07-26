def addition(dataframe, col_name, columns):
    if columns is None or len(columns) < 2:
        return dataframe
    dataframe[col_name] = dataframe[columns].sum(axis=1)
    return dataframe


def multiply(dataframe, col_name, columns):
    if columns is None or len(columns) < 2:
        return dataframe
    dataframe[col_name] = dataframe[columns].prod(axis=1)
    return dataframe


def divide(dataframe, col_name, columns):
    if columns is None or len(columns) < 2:
        return dataframe
    dataframe[col_name] = dataframe[columns[0]].div(dataframe[columns[1]])
    for i in range(2, len(columns)):
        dataframe[col_name] = dataframe[col_name].div(dataframe[columns[i]])
    return dataframe


def subtract(dataframe, col_name, columns):
    if columns is None or len(columns) < 2:
        return dataframe
    dataframe[col_name] = dataframe[columns[0]].sub(dataframe[columns[1]])
    for i in range(2, len(columns)):
        dataframe[col_name] = dataframe[col_name].sub(dataframe[columns[i]])
    return dataframe
