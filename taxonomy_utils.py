from typing import Union, List


import pandas as pd
import numpy as np


def get_non_repeated_words(taxonomy):
    """
        Let's check if category have unique words
    """
    df = pd.DataFrame(taxonomy, columns = ['query','level','category_name'])
    df['query'] = df['query'] + ", "
    df = df.groupby('category_name')['query'].sum()
    
    arr_queries = df.values
    
    arr_queries = [x.replace(","," ").split(" ") for x in arr_queries]
    arr_queries = [[y.strip() for y in query if len(y.strip())>=3] for query in arr_queries ]
    arr_queries = [list(set(query)) for query in arr_queries ]


    lst = []
    for x in arr_queries:
        lst += x 

    arr_queries = lst

    pd_words_count = pd.value_counts(arr_queries)
    pd_words_count = pd_words_count[pd_words_count==1]
    set_unique = set(pd_words_count.index)
    
    return set_unique


def query_split(queries: Union[list, str]):
    """
        Receive query as text or list of texts and get back list of all queries 
    """
    if isinstance(queries, str):
        queries = [queries]
    
    queries = [x.strip() for query in queries for x in query.split(",")]
    return queries


def query_words(queries: Union[list, str]):
    """
        split query into separate words
    """
    if isinstance(queries, str):
        queries = [queries]
        
    words = [x.strip() for query in queries for x in query.split(" ") if len(x.strip())>0]
    words = list(set(words))
    return words


def word_to_token(word: str):
    """
        tokenize word - we will search in the description the token, not the original word
    """
    word = word.lower()
    token = " " + word if len(word)>3 else " " + word + " " 
    return token


def cache_words(df: pd.DataFrame, dict_cache: dict, words: List[str]):
    
    if len(dict_cache) == 0:
        ## nothing to cache
        return dict_cache

    words_to_cache = [word for word in words if word in dict_cache and dict_cache[word] is None]  

    for word in words_to_cache: 

        token = word_to_token(word)
        filt = [token in txt for txt in df['descr'].tolist()]
        dict_cache[word] = filt  

    return dict_cache    


def get_words_cache_dict(taxonomy, is_cache):

    ## building words for caching
    if is_cache == True:
        all_queries = [x[0] for x in taxonomy]
        all_queries = query_split(all_queries)
        all_words = [y.strip() for query in all_queries for y in query.split(" ")]
        
        pd_words_count = pd.value_counts(np.array(all_words))
        pd_words_count = pd_words_count[pd_words_count>1]
        
        del all_words
        del all_queries
        
        words_to_cache = pd_words_count.index.values
        n_words = len(words_to_cache)
        
        print (f"Count words to cache {n_words}")
        dict_cache = {word: None for word in words_to_cache}
    else:
        dict_cache = {}

    return dict_cache     

