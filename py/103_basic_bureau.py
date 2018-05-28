#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 24 18:59:38 2018

@author: kazuki.onodera

bureau

"""

import numpy as np
import pandas as pd
import gc
from multiprocessing import Pool
from glob import glob
import utils
utils.start(__file__)
#==============================================================================
KEY = 'SK_ID_CURR'
PREF = 'bureau'
NTHREAD = 3


col_num = ['DAYS_CREDIT', 'CREDIT_DAY_OVERDUE', 'DAYS_CREDIT_ENDDATE',
           'DAYS_ENDDATE_FACT', 'AMT_CREDIT_MAX_OVERDUE', 'CNT_CREDIT_PROLONG',
           'AMT_CREDIT_SUM', 'AMT_CREDIT_SUM_DEBT', 'AMT_CREDIT_SUM_LIMIT',
           'AMT_CREDIT_SUM_OVERDUE', 'DAYS_CREDIT_UPDATE', 'AMT_ANNUITY']

col_cat = ['CREDIT_ACTIVE', 'CREDIT_CURRENCY', 'CREDIT_TYPE']

col_group = ['CREDIT_ACTIVE', 'CREDIT_CURRENCY', 'CREDIT_TYPE']

# =============================================================================
# feature
# =============================================================================
bureau = utils.read_pickles('../data/bureau')

base = bureau[[KEY]].drop_duplicates().set_index(KEY)


def nunique(x):
    return len(set(x))

def multi_gr2(k):
    gr2 = bureau.groupby([KEY, k])
    gc.collect()
    print(k)
    keyname = 'gby-'+'-'.join([KEY, k])
    # size
    gr1 = gr2.size().groupby(KEY)
    name = f'{PREF}_{keyname}_size'
    base[f'{name}_min']  = gr1.min()
    base[f'{name}_max']  = gr1.max()
    base[f'{name}_max-min']  = base[f'{name}_max'] - base[f'{name}_min']
    base[f'{name}_mean'] = gr1.mean()
    base[f'{name}_std']  = gr1.std()
    base[f'{name}_sum']  = gr1.sum()
    base[f'{name}_nunique']     = gr1.size()
    for v in col_num:
        
        # min
        gr1 = gr2[v].min().groupby(KEY)
        name = f'{PREF}_{keyname}_{v}_min'
        base[f'{name}_max']     = gr1.max()
        base[f'{name}_mean']    = gr1.mean()
        base[f'{name}_std']     = gr1.std()
        base[f'{name}_sum']     = gr1.sum()
        base[f'{name}_nunique'] = gr1.apply(nunique)
        
        # max
        gr1 = gr2[v].max().groupby(KEY)
        name = f'{PREF}_{keyname}_{v}_max'
        base[f'{name}_min']  = gr1.min()
        base[f'{name}_mean'] = gr1.mean()
        base[f'{name}_std']  = gr1.std()
        base[f'{name}_sum']  = gr1.sum()
        base[f'{name}_nunique'] = gr1.apply(nunique)
        
        # mean
        gr1 = gr2[v].mean().groupby(KEY)
        name = f'{PREF}_{keyname}_{v}_mean'
        base[f'{name}_min']  = gr1.min()
        base[f'{name}_max']  = gr1.max()
        base[f'{name}_max-min']  = base[f'{name}_max'] - base[f'{name}_min']
        base[f'{name}_mean'] = gr1.mean()
        base[f'{name}_std']  = gr1.std()
        base[f'{name}_sum']  = gr1.sum()
        base[f'{name}_nunique'] = gr1.apply(nunique)
        
        # std
        gr1 = gr2[v].std().groupby(KEY)
        name = f'{PREF}_{keyname}_{v}_std'
        base[f'{name}_min']  = gr1.min()
        base[f'{name}_max']  = gr1.max()
        base[f'{name}_max-min']  = base[f'{name}_max'] - base[f'{name}_min']
        base[f'{name}_mean'] = gr1.mean()
        base[f'{name}_std']  = gr1.std()
        base[f'{name}_sum']  = gr1.sum()
        base[f'{name}_nunique'] = gr1.apply(nunique)
        
        # sum
        gr1 = gr2[v].sum().groupby(KEY)
        name = f'{PREF}_{keyname}_{v}_sum'
        base[f'{name}_min']  = gr1.min()
        base[f'{name}_max']  = gr1.max()
        base[f'{name}_max-min']  = base[f'{name}_max'] - base[f'{name}_min']
        base[f'{name}_mean'] = gr1.mean()
        base[f'{name}_std']  = gr1.std()
        base[f'{name}_nunique'] = gr1.apply(nunique)
    base.to_pickle(f'../data/tmp_{PREF}_{k}.p')
    
# =============================================================================
# gr2
# =============================================================================
pool = Pool(NTHREAD)
callback = pool.map(multi_gr2, col_group)
pool.close()
        

# =============================================================================
# gr1
# =============================================================================
gr = bureau.groupby(KEY)

# stats
keyname = 'gby-'+KEY
for c in col_num:
    gc.collect()
    print(c)
    base[f'{PREF}_{keyname}_{c}_min'] = gr[c].min()
    base[f'{PREF}_{keyname}_{c}_max'] = gr[c].max()
    base[f'{PREF}_{keyname}_{c}_max-min'] = base[f'{PREF}_{keyname}_{c}_max'] - base[f'{PREF}_{keyname}_{c}_min']
    base[f'{PREF}_{keyname}_{c}_mean'] = gr[c].mean()
    base[f'{PREF}_{keyname}_{c}_std'] = gr[c].std()
    base[f'{PREF}_{keyname}_{c}_sum'] = gr[c].sum()
    base[f'{PREF}_{keyname}_{c}_nunique'] = gr[c].apply(nunique)


# =============================================================================
# cat
# =============================================================================
for c1 in col_cat:
    gc.collect()
    print(c1)
    df_sum = pd.crosstab(bureau[KEY], bureau[c1])
    df_sum.columns = [f'{PREF}_{c1}_{str(c2).replace(" ", "-")}_sum' for c2 in df_sum.columns]
    df_norm = pd.crosstab(bureau[KEY], bureau[c1], normalize='index')
    df_norm.columns = [f'{PREF}_{c1}_{str(c2).replace(" ", "-")}_norm' for c2 in df_norm.columns]
    df = pd.concat([df_sum, df_norm], axis=1)
    col = df.columns.tolist()
    base = pd.concat([base, df], axis=1)
    base[col] = base[col].fillna(-1)


# =============================================================================
# merge
# =============================================================================
df = pd.concat([ pd.read_pickle(f) for f in sorted(glob(f'../data/tmp_{PREF}*.p'))], axis=1)
base = pd.concat([base, df], axis=1)
base.reset_index(inplace=True)
del df; gc.collect()

train = utils.load_train([KEY])
train = pd.merge(train, base, on=KEY, how='left').drop(KEY, axis=1)


test = utils.load_test([KEY])
test = pd.merge(test, base, on=KEY, how='left').drop(KEY, axis=1)

utils.to_pickles(train, '../data/103_train', utils.SPLIT_SIZE)
utils.to_pickles(test,  '../data/103_test',  utils.SPLIT_SIZE)






#==============================================================================
utils.end(__file__)


