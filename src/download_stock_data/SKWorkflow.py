import os

from snakemake import snakemake
from snakemake.io import load_configfile
from snakemake.utils import available_cpu_count

class SKWorkflow:
    """Configures and runs a snakemake workflow.

        This workflow understands the config parameter:
            * symbol
        A caller has to provide the parameter as key/value
        pair in cfg_params, e.g {"symbol": "MUX.DE"}
        
        Furthermore, the tasks supports switches such as
            * delete_all_output
            * dryrun
        They need to be provided as key/value pairs in kwargs, e.g.
        {"delete_all_output": "True"} will delete all workflow's output files.    

    """
    def __init__(self, logger):
        self.logger = logger
        self.sk_config = {}
        self.sk_param = {}
        self.snakefile = "Snakefile"
        self.config_yaml = "config.yaml"
        
    def config_workflow(self, cfg_params):
        self.sk_config = self._get_workflow_config_yaml()
        
        # retrieve key/values from caller
        if 'symbol' in cfg_params is not None:
            self.sk_config['symbol'] = str(cfg_params['symbol'])
        # We accept other params
        # 1. delete_all_output - resets workflow
        # 2. dryrun - test the workflow
        if 'delete_all_output' in cfg_params is not None:
            delete_param_value = cfg_params['delete_all_output']
            if isinstance(delete_param_value, bool):
                self.sk_param['delete_all_output'] = delete_param_value
            else:
                self.sk_param['delete_all_output'] = 'TRUE' == cfg_params['delete_all_output'].upper()
        if 'dryrun' in cfg_params is not None:
            dryrun_param_value = cfg_params['dryrun']
            if isinstance(dryrun_param_value, bool):
                self.sk_param['dryrun'] = dryrun_param_value
            else:
                self.sk_param['dryrun'] = 'TRUE' == cfg_params['dryrun'].upper()
            self.sk_param['printreason'] = True


    def run_workflow(self):
        # Test and start snakemake
        if not os.path.isfile(self.snakefile):
            #msg = "Required file not found: {}".format(self.snakefile)
            raise FileNotFoundError(self.snakefile)

        self.logger.info('Run snakemake ...')
        sk = snakemake(
            snakefile=self.snakefile,
            config=self.sk_config,
            **self.sk_param,
        )
        
        return sk # True/False
        
    def _get_workflow_config_yaml(self):
        """Read the config.yaml file

        Returns the content as dict or empty dict, if file not found.
        """
        cfg = {}
        if os.path.isfile(self.config_yaml):
            self.logger.info("Load snakemake config file: {}".format(self.config_yaml))
            cfg = load_configfile(self.config_yaml)
       
        if 'CORES' in cfg is None:
            n_cores = 1
        else:
            n_cores = available_cpu_count() if cfg["CORES"]=='all' else cfg["CORES"]
        self.sk_param['cores'] = n_cores
        
        return cfg
