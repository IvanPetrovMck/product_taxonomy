import pandas as pd
import numpy as np

from taxonomy_utils import query_split, query_words, cache_words, word_to_token
import time
from copy import deepcopy


def simple_search(df: pd.DataFrame(), 
                  taxonomy: list,
                  taxonomy_gen: list,
                  words_non_repeated: set = set(),
                  dict_cache: dict = {}):


    dict_cache = deepcopy(dict_cache)
    words_non_repeated = deepcopy(words_non_repeated)

    ## list of genders
    ## ['women', 'men', 'kids', 'baby']
    lst_profile = [x[2] for x in taxonomy_gen]
    
    is_cache = len(dict_cache) > 0

    delta = 0
    
    is_cache = True
    df['taxonomy'] = None
    df['tax_weight'] = 0
    df['filt'] = None

    n_rules = len(taxonomy)
    print (f"Total rules {n_rules}")

    ## we will save results in this array
    arr_weight = np.full(df.shape[0], fill_value=0)
    arr_tag = np.full(df.shape[0], fill_value=None, dtype=object)
    arr_query = np.full(df.shape[0], fill_value=None, dtype=object)
    arr_profile = np.full(df.shape[0], fill_value=None, dtype=object)

    for i, rule in enumerate(taxonomy):
        
        print (f"Cnt words processed {(i+1)/n_rules * 100:.1f}%",end = "\r")
        
        lst_queries = query_split(rule[0])
        tag_name = rule[2]
        level_val = rule[1]

        val_profile = None
        for gen in lst_profile:

            len_before = len(tag_name)
            tag_name = tag_name.replace(f"-> {gen} ->", "->")
            len_after = len(tag_name)
            if len_after < len_before:
                val_profile = gen

    
        for query in lst_queries:
            
            words = query_words(query)

            ## if has some unique keyword in search
            is_non_rep = any(True for word in words if word in words_non_repeated)
            

            ## count words + count letters
            if level_val>1:
                new_weight = len(words) + 1/20 * sum([len(x) for x in words]) + 2 * is_non_rep
            elif level_val == 1:
                new_weight = 1/20 * sum([len(x) for x in words]) + 2 * is_non_rep
            else: 
                new_weight = 0


            if is_cache:
                ## 5s / 20s of time
                dict_cache = cache_words(df, dict_cache, words)
                words_in_cache = [word for word in words if dict_cache.get(word,None) is not None]  
                words_no_cache = [word for word in words if word not in words_in_cache]  
            else:
                words_no_cache = words
                
            if len(words_in_cache)>0:
                filt_cache = [dict_cache[word] for word in words_in_cache]

                
            ## short words should be present full
            tokens_no_cache = [word_to_token(x) for x in words_no_cache]

            
            ## 15s / 20s of time
            ## using tolist() is very fast
            all_filt = [[x in txt for txt in df['descr'].tolist()] for x in tokens_no_cache] 
            
            if len(words_in_cache)>0:
                all_filt += filt_cache

            all_filt += [arr_weight < new_weight]

            ## 
            filt = fast_np_all(all_filt)

            ## very fast
            arr_weight[filt] = new_weight
            arr_tag[filt] = tag_name
            arr_query[filt] = query
            arr_profile[filt] = val_profile    



    ##
    ## -- Separately searching for customer gender and age
    ## 
    for i, rule in enumerate(taxonomy_gen):
        
         ### ['women, wmn, woman, female]', 
        lst_queries = query_split(rule[0])

        ### ['women', 'men', 'kids', 'baby']
        val_profile = rule[2]

        for query in lst_queries:
            words = query_words(query)

            ## short words should be present full
            tokens = [word_to_token(x) for x in words]

            all_filt = [[x in txt for txt in df['descr'].tolist()] for x in tokens]

            filt = fast_np_all(all_filt)
            arr_profile[filt] = val_profile      


    df['taxonomy'] = arr_tag
    df['tax_weight'] = arr_weight
    df['query'] = arr_query
    df['profile'] = arr_profile

    n_zeros = df['taxonomy'].isna().sum() / df.shape[0]
    n_non_prof = df['profile'].isna().sum() / df.shape[0]

    print (f"Non matched products {round(n_zeros * 100, 1)} %")
    print (f"Non matched gender/age {round(n_non_prof * 100, 1)} %")
    print (f"Delta time {delta}s")

    return df


def fast_np_all(lst_arr_bools):
    """
        Very fast version of standard numpy.all
    """
    if len(lst_arr_bools) == 0:
        return None

    output = lst_arr_bools[0]
    for w in range(1, len(lst_arr_bools)):   # logical combination with other elements
        output = np.logical_and(output, lst_arr_bools[w])

    return output