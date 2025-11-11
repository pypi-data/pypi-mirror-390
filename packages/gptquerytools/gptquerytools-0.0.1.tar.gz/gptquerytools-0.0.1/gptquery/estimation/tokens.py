# gptquery/gptquery/estimation/tokens.py
""" 


"""
import tiktoken 
##############################################
# FUNCTION Lenght of strings
##############################################
def token_str_estimate(text):
    import re
    # SPLIT the text on whitespace and punctuation
    tokens = re.findall(r'\S+', text)
    return len(tokens)

##############################################
# FUNCTION Compare encoding OpenAI
# GEN >> TEXT STRING << lambda
##############################################
def compare_token_encodings(text_string: str, models: list = None, show_details: bool = False) -> None: # type: ignore
    """
    Prints a comparison of token encodings for multiple models.

    Args:
        text_string (str): The input text to be encoded.
        models (list, optional): A list of model names to compare. 
                                 Defaults to common GPT models.
        show_details (bool, optional): If True, also print token IDs and decoded bytes.
    """

    # Default model list
    if models is None:
        models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]

    for model in models:
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print(f"{model:<20} : [ERROR] Unknown model name.")
            continue

        token_ids = encoding.encode(text_string)
        num_tokens = len(token_ids)

        print(f"{model:<20} : {num_tokens:>5} tokens")
        
        if show_details:
            decoded_bytes = [encoding.decode([tok]).encode('utf-8') for tok in token_ids]
            print(f"  Token IDs     : {token_ids}")
            print(f"  Token bytes   : {decoded_bytes}")
            print()

def token_text_estimate(text_string: str, model="gpt-4o-mini"):
    """
    Estimate the number of tokens in the given text using the specified model's encoding.

    Args:
        text (str): The text to estimate the token count for.
        model (str): The name of the model to use for encoding 
                     (default is "gpt-4o-mini").

    Supported models:
        - gpt-4o, gpt-4, gpt-4o-mini, gpt-4-turbo
        - gpt-3.5-turbo
        - text-embedding-ada-002, text-embedding-3-small, text-embedding-3-large
        - davinci, text-davinci-002, text-davinci-003

    Returns:
        int: The number of tokens in the given text.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback to default encoding if the model is not recognized
        encoding = tiktoken.get_encoding("cl100k_base")

    token_ids = encoding.encode(text_string)
    return len(token_ids)


################################################
# FUCNTION estimate max tokens in col-row value
# >> pd.Series <<
################################################
def max_tokens_in_column(df, column_name, model="gpt-4o-mini"):

    """
    [ ] Rename to max_tokens_in_colxrow()
    Count tokens in a specified DataFrame column and return 
    the cell with the maximum token count.

    Parameters:
    df (pd.DataFrame): DataFrame with data.
    column_name (str): Column name to count tokens.
    model (str): Tokenization model (default is "gpt-3.5-turbo").

    Returns:
    tuple: Cell value with max tokens and its token count.
    """
    df_funct=df.copy()
    encoding = tiktoken.encoding_for_model(model)
    df_funct['token_count'] = df_funct[column_name].apply(lambda x: len(encoding.encode(x)))
    max_token_row = df_funct.loc[df_funct['token_count'].idxmax()]
    sum_tokens = df_funct['token_count'].sum()
    print(f"MAX Tokens using {model}: {max_token_row['token_count']:,}")
    print(f"TOTAL Tokens using {model}: {sum_tokens:.2e}")
    # print(f"TOTAL Tokens using {model}: {sum_tokens:,}")
    return df_funct
###################################################


