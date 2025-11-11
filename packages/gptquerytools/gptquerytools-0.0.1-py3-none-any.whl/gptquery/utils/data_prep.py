
import ast
import pandas as pd

#######################
# <GEN> Function explodes df where literal str store in col row value
# >>> pd.DataFrame
#######################
def eval_and_explode(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Safely evaluates stringified lists in a DataFrame column, explodes them into separate rows,
    and replaces any resulting NaN with an empty string.

    Parameters:
    - df: pandas DataFrame containing the column to process.
    - col: Name of the column with string representations of lists.

    Returns:
    - A new DataFrame where the specified column is exploded into separate rows,
      with empty lists or invalid entries resulting in empty strings.

    Example:
    >>> df = pd.DataFrame({'id': [1, 2, 3], 'list_col': ['[1,2]', '', '[3,4]']})
    >>> eval_and_explode(df, 'list_col')
       id list_col
    0   1        1
    1   1        2
    2   2         
    3   3        3
    4   3        4
    """
    def safe_eval(val):
        # If val is already a list or tuple, return as is
        if isinstance(val, (list, tuple)):
            return val

        # If val is None, NaN, or empty string, return empty list
        if val is None:
            return []
        if isinstance(val, float) and pd.isna(val):
            return []
        if isinstance(val, str) and val.strip() == '':
            return []
        
        # MAIN Evaluating function
        try:
            return ast.literal_eval(val) # type: ignore
        except (ValueError, SyntaxError):
            return []

    df = df.copy()
    df[col] = df[col].apply(safe_eval)
    df = df.explode(col, ignore_index=True)
    df[col] = df[col].fillna('')
    return df


############################################################################################
# # <GEN> Splits a string column by separator into specified named columns, padding empty values with empty strings.
# >>> pd.DataFrame
############################################################################################
def split_column_with_names(
    df: pd.DataFrame,
    source_col: str,
    target_cols: list=['cited_celex', 'doc_col', 'struct_col'],
    sep: str = ','
) -> pd.DataFrame:
    """
    Splits a string column into multiple columns based on an existing separator.

    Pads missing parts with empty strings to match the number of target columns.
    If there are more parts than target columns, the excess is discarded.
    Whitespace is stripped from each part after splitting.
    NaN or empty strings are treated as empty during splitting.

    Parameters:
    - df: Input DataFrame.
    - source_col: Name of the column with separator-separated strings.
    - target_cols: List of column names for the split parts.
    - sep: Separator character (default ',').

    Returns:
    - DataFrame with new columns appended for each split part.

    Examples:
    ---------
    Given a DataFrame where a column contains:
        "31987R2658,annex I,note 5 point (a)"
    Calling:
        >>> split_column_with_names(df, 'ref_string', ['cited_celex', 'doc_col', 'struct_col'])
    
    Will produce:
        cited_celex   | doc_id  | struct_col
        -------------|----------|----------------------
        31987R2658   | annex I  | note 5 point (a)

    If a string is missing components, the missing columns will be empty:
        "31987R2658,annex I"
    Will produce:
        cited_celex  | doc_id    | struct_col
        -------------|----------|-----
        31987R2658   | annex I  | (empty string)
    """
    def safe_split(s):
        if pd.isna(s) or s == '':
            parts = []
        else:
            parts = s.split(sep)
        parts = [p.strip() for p in parts]
        if len(parts) < len(target_cols):
            parts += [''] * (len(target_cols) - len(parts))
        else:
            parts = parts[:len(target_cols)]
        return parts

    split_lists = df[source_col].apply(safe_split)
    split_df = pd.DataFrame(split_lists.tolist(), columns=target_cols, index=df.index)
    return df.join(split_df)


############################################################################################
# <GPTQUERY> Function collapses creates variables of record format data for better parsing.
# >> pd.DataFrame >> pd.DataFrame
############################################################################################
def collapse_fields_per_unit(
    df: pd.DataFrame, 
    group_var: str, 
    columns: list, 
    unit_of_analysis: str = None, # type: ignore
    separator: str = '\n'
) -> pd.DataFrame:
    """
    Collapses specified text fields by a grouping variable, producing 'all_' prefixed columns
    containing newline-separated values per group. Optionally reshapes the DataFrame to the 
    unit of analysis level.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame.
    group_var : str
        The variable to group by (e.g., document ID, paragraph ID).
    columns : list
        The columns to collapse within each group.
    unit_of_analysis : str, optional
        The desired unit of analysis. If provided and different from `group_var`, the output
        will have one row per `group_var`.
        If None or same as `group_var`, the full DataFrame shape is preserved.
    separator : str, optional
        Separator used to join grouped values (default is newline '\\n').

    Returns
    -------
    pd.DataFrame
        A DataFrame with new 'all_' prefixed columns containing collapsed field values.

    Example
    -------
    >>> df = pd.DataFrame({
    ...     'doc_id': [1, 1, 2, 2, 3],
    ...     'citation': ['A', 'B', 'C', None, 'E'],
    ...     'comment': ['x', None, 'y', 'z', 'w']
    ... })
    >>> collapse_fields_per_unit(df, group_var='doc_id', columns=['citation', 'comment'], unit_of_analysis='doc_id')
       doc_id all_citation all_comment
    0       1        A\nB            x
    1       2           C         y\nz
    2       3           E            w
    """
    df = df.copy()
    
    for col in columns:
        df[f'all_{col}'] = (
            df.groupby(group_var)[col]
            .transform(lambda x: separator.join(x.dropna().astype(str)))
        )

    if unit_of_analysis:
        new_cols = [group_var] + [f'all_{col}' for col in columns]
        df = df[new_cols].drop_duplicates(subset=group_var).reset_index(drop=True) # type: ignore
    
    return df
