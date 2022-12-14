"""Utility functions for the snakemake workflow

"""

import os
import pathlib
import re
import requests
import pandas as pd


def last_run_result(exp_outdir):
    """Retrieve last run result directory from previous runs in exp_outdir

    The result directories follow the pattern:
    {EXPERIMENT_NAME}_{MODEL_NAME}
    {EXPERIMENT_NAME}_{MODEL_NAME}_0
    {EXPERIMENT_NAME}_{MODEL_NAME}_1
    ...
    
    Parameters
    ----------
    exp_outdir :  str  
        Full path directory containing all result run directories from previous runs
    
    Returns
    -------
    str
        the name of the most recent result run directory, name only, not path,
        or empty string, if the directory does not exist.
    
    """
    try:
        results_dirs = [d for d in pathlib.Path(exp_outdir).iterdir() if d.is_dir()]
        results_dirs = sorted(results_dirs, key=os.path.getmtime)
    except Exception:
        results_dirs = []
    if not results_dirs:
        return ''
    
    return os.path.basename(results_dirs[-1])


def current_run_result(lrr, exp_outdir, exp_name, mod_name):
    """Retrieve current run result directory

    If last run result is {EXPERIMENT_NAME}_{MODEL_NAME}_n,
    the current run result dir is {EXPERIMENT_NAME}_{MODEL_NAME}_n+1
    
    Special cases:
    1. If last run result does not exist,
        the current run result dir is {EXPERIMENT_NAME}_{MODEL_NAME}
    2. If last run result is {EXPERIMENT_NAME}_{MODEL_NAME},
        the current run result dir is {EXPERIMENT_NAME}_{MODEL_NAME}_0

    Parameters
    ----------
    lrr: str
        The name of the most recent run result directory from previous runs

    exp_outdir :  str  
        EXPERIMENT_OUTDIR, full path directory containing all result run directories

    exp_name : str
        EXPERIMENT_NAME
        
    mod_name : str
        MODEL_NAME
    
    Returns
    -------
    str
        full path of the result directory of the current run
    
    """

    if not lrr:
        subdir = exp_name + "_" + mod_name
    else:
        x = re.search(r"\d+$", lrr)
        num = -1 if x is None else int(x.group())
        next_num = num + 1
        subdir = exp_name + "_" + mod_name + "_" + str(next_num)

    return os.path.join(exp_outdir, subdir)


def predict_csv_files(result_dir, sub_str='_predictions.csv'):
    """Return predictions csv files from result_dir with full path

    
    Parameters
    ----------
    result_dir :  str  
        Full path result run directory, e.g. {EXPERIMENT_NAME}_{MODEL_NAME}_n
    
    sub_str :  str, optional 
        substring to search in all files within the result_dir 

    Returns
    -------
    list
        full file paths of all files machting the sub_str in result_dir
        
    """
    predict_csv = [f for f in next(os.walk(result_dir))[2] if sub_str in f]
    return [os.path.join(result_dir, f) for f in predict_csv]

def url_avail(url):
    """Returns true, if head request to url results in 200 OK


    Parameters
    ----------
    url :  str  
        The URL of a website to test
    
    Returns
    -------
    bool
        True, if 200 OK status is retrieved, otherwise false
    
    """
    try:
        r = requests.head(url, timeout=2)
        return r.status_code == 200
    except Exception:
        pass

    return False

########################################################################
#
# Helper functions for setupyaml.sk
#
########################################################################

def all_targets_vars():
    """All possible target variable names
    
    Returns
    -------
    list
        all possible target variable names  
    
    """

    # classification targets
    l = ['retgt'+str(i) for i in range(1,100)]
    # regression target
    l.append('return')
    return l
    
def get_header(pqfile):
    """Return the header names list as a from the parquet file.

    Parameters
    ----------
    pqfile :  path  
        Full path of the train parquet file
    

    Returns
    -------
    list
        the header as a list of columns names 
    
    """    
    # open file, read header columns and create list, return list
    df = pd.read_parquet(pqfile)
    header_columns = list(df.columns)
    return header_columns

def get_target_vars(header, targets=all_targets_vars()):
    """Returns availabe targets vars from the header.
    
    This function selects the availabe targets vars from all possible target vars.

    Parameters
    ----------
    header :  list
        header as a list of columns names from the parquet file containing the data
        
    targets : list
        all possible target variable names

    Returns
    -------
    list
        the availabe target vars  

    """

    target_vars = [t for t in header if t in targets]
    return target_vars

def get_input_vars(header, targets=all_targets_vars()):
    """Removs all possible target variable from the form header columns names.
    
    As a result, this function return the availabe input variables.
    
    Parameters
    ----------
    header :  list
        header as a list of columns names from the parquet file containing the data
        
    targets : list
        all possible target variable names

    Returns
    -------
    list
        the availabe input vars    
    """
    
    input_vars = [c for c in header if c not in targets]
    return input_vars
