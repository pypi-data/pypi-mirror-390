import os
import yaml
import warnings
import logging
from pathlib import Path
from typing import List, Tuple

import pandas as pd

from xurpas_data_quality.report import get_report, get_empty_report, get_comparison_report, get_error_report, get_test_report
from xurpas_data_quality.data import check_dtypes, describe, load_dataframe,validate_dataframe,sample_dataframe ,check_col_names, describe_invalid, check_data, convert_to_pandas
from xurpas_data_quality.config import Settings

warnings.filterwarnings("ignore", category=UserWarning, module='visions')

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

class DataReport:
    def __init__(self, 
                 file:str=None, 
                 df:pd.DataFrame|List[pd.DataFrame]|Tuple[pd.DataFrame,pd.DataFrame,List] =None, 
                 report_name:str=None, 
                 file_path:str=None,
                 data_types:dict=None,
                 description: str = None,
                 minimal: bool=None,
                 sample_mode: str = 'auto',
                 sample_size: float = None,
                 auto_sample_dataset_length: int = None,
                 config_file: str = None,
                 **kwargs):
        
        logger.info("Initializing DataReport object")
        """
        Initializes the DataReport object
        Args
            file:        The path of the file you want to analyze. If empty, df parameter must exist.
                         Only supports .csv, .xlsx, .parquet, and .orc file formats
            df:          Pandas DataFrame object of data to be analyzed, If using df, file must be empty.
            report_name: Name of the report. Defaults to 'Data Quality Report'
            file_path:   Path/ directory of where the report is to be saved
            data_types:  A dictionary containing the column names and their corresponding data types.
                         If empty, then the data types will be inferred.
            minimal:     Default is True. Check if you want minimal mode as your data report.
            sample_mode: The mode of sampling. Choose between 'auto', 'manual', or 'none'. Default is 'auto'.
                         If 'Manual', you must provide a sample_size parameter. If none, no sampling is done to the data.
            sample_size: The fraction of the data to be sampled. Only used when sample_mode is 'manual'.
            auto_sample_dataset_length: The length of the dataset to be sampled. Only used when sample_mode is 'auto'. If empty, defaults to 100000.
            config_file: Optional. The path of the configuration file. If empty, default values will be used.
        """

        """Loading the config Section"""
        """The loading of config priority goes with highest priority first:
            - initialization DataReport parameters
            - config file
            - default values"""
        
        __non_config_params__ = ["self","kwargs","df","file", "config_file","sample_size", "sample_mode", "auto_sample_dataset_length","description","__non_config_params__"]
        __user_set_params__ = {key: value for key, value in locals().items() if value is not None and key not in __non_config_params__}
        logger.debug(f"__user_set_params__: {__user_set_params__}")
        if config_file != None:
            try:
                with open(config_file) as f:
                    __config_file_params__ = yaml.load(f, Loader=yaml.FullLoader)
                
                if __config_file_params__ is None:
                    raise ValueError(f"{config_file} is empty! proceeding with report generation.")

                logger.debug("Config file before being loaded in settings")
                logger.debug(__config_file_params__)
                self.config = Settings(**__config_file_params__)
                logger.debug("After loading it into Settings class")
                logger.debug(self.config)
                logger.info(f"Loaded configuration from {config_file}")

                for key, value in __user_set_params__.items():
                    setattr(self.config, key, value)

            except FileNotFoundError:
                logger.warning(f"{config_file} does not exist! continuing with generating report without it")

            except Exception as e:
                logger.error(f"Error loading config file: {e}")

            finally:
                self.__load_config__(__user_set_params__, sample_mode, auto_sample_dataset_length, sample_size)
        else:
            self.__load_config__(__user_set_params__, sample_mode, auto_sample_dataset_length, sample_size)

        """Checking dataframe input"""
        if description is None:
            self.dataset_description = None
        else:  
            self.dataset_description = [description]

        if isinstance(df, dict):
            df_frames = list(df.values())
            self.df = []
            for frame in df_frames:
                self.df.append(frame if isinstance(frame, pd.DataFrame) else convert_to_pandas(frame) )
                
            self.df_names = list(df.keys())
            self.render_empty = False

        elif isinstance(df, tuple):
            self.df = df[0] if isinstance(df[0], pd.DataFrame) else convert_to_pandas(df[0])
            self.df_invalid = df[1] if isinstance(df[1], pd.DataFrame) else convert_to_pandas(df[1])
            self.errors = df[2] if isinstance(df[2],list) else [df[2]]
            self.empty_df_invalid = True if not validate_dataframe(self.df_invalid, self.config) else False
            self.render_empty = True if not validate_dataframe(self.df, self.config) else False
        
        else:
            if file is not None:
                if df is not None:
                    raise KeyError("Only 'file' or 'df' should be used one at a time!")
                self.df = load_dataframe(file)
                self.render_empty = False

            else:
                if df is None:
                    raise ValueError("Please provide your data in 'file' or 'df' parameters!")
                
                self.df = df
                self.render_empty = True if not validate_dataframe(df, self.config) else False # checks if dataframe is empty

        if self.config.sampling.get_sampling:
            self.df, sample_description = sample_dataframe(self.df, self.config)
            if sample_description is not None:
                if self.dataset_description is None:
                    self.dataset_description = [sample_description]
                elif isinstance(self.dataset_description, list):
                    self.dataset_description.append(sample_description)
                else:
                    self.dataset_description = [self.dataset_description, sample_description]
                print(f"after: {self.dataset_description}")

        """checking data types"""
        if data_types is not None:
            self.data_types = check_dtypes(check_col_names(data_types, df.columns))
        else:
            self.data_types = None

        logger.debug(f"self.render_empty: {self.render_empty}")
        logger.info("DataReport object initialized successfully")

    def __load_config__(self, __user_set_params__:dict, sample_mode, auto_sample_dataset_length, sample_size):
        logger.debug(f"sample_mode: {sample_mode}")
        for key, value in __user_set_params__.items():
            self.config = self.config.model_copy(update=__user_set_params__)
        logger.debug("Config Loaded:")
        logger.debug(self.config)
        logger.debug(f"sample_mode == 'auto': {sample_mode == 'auto'}")
        sample_mode = sample_mode.lower() if sample_mode is not None else None

        """Sampling settings"""
        if sample_mode == "auto":
            logger.debug("auto sampling chosen")
            if auto_sample_dataset_length is not None:
                self.config.sampling.auto_length = auto_sample_dataset_length

        elif sample_mode == "manual":
            if sample_size is not None:
                if sample_size > 1:
                    raise ValueError("Sample size should be a fraction less than 1")
                self.config.sampling.size = sample_size
            else:
                raise ValueError("Manual sample_mode requires you to provide a sample_size (fraction between 0 and 1)")
            
        elif sample_mode is None or sample_mode == "none":
            self.config.sampling.get_sampling = False

        else:
            raise ValueError("Invalid sample_mode. Please choose between 'auto', 'manual', or 'none'")

    def describe_dataframe(self):
        logger.info("Describing dataframe")
        self.description = describe(df=self.df, data_types=self.data_types, config=self.config)
        if self.dataset_description is not None and self.dataset_description != "":
            if self.description.description is None:
                self.description.description = []
            
            self.description.description.extend(self.dataset_description)

        logger.info("Dataframe described successfully")

    def describe_invalid_dataframe(self):
        logger.info("Describing invalid dataframe")
        self.description_invalid = describe_invalid(df=self.df_invalid, errors=self.errors, config=self.config)
        logger.info("Invalid dataframe described successfully")

    def get_data_quality_report(self, config:dict, **kwargs):
        logger.info("Generating data quality report")
        self.describe_dataframe()
        report = get_report(self.description, config)
        logger.info("Data quality report generated successfully")
        return report.render()
    
    def _render_empty_report(self, config:dict):
        logger.info("Rendering empty report")
        report = get_empty_report(self.df, config)
        logger.info("Empty report rendered successfully")
        return report.render()
    
    def _render_comparison(self, config:dict):
        logger.info("Rendering comparison report")
        self.describe_dataframe()
        report = get_comparison_report(self.description, self.df_names, config)
        logger.info("Comparison report rendered successfully")
        return report.render()
    
    def _render_error_report(self, config:dict):
        logger.info("Rendering error report")
        self.describe_invalid_dataframe()
        if self.render_empty:
            report = get_error_report(data=self.df,
                            invalid_data=self.description_invalid,
                            errors=self.errors, 
                            is_empty=self.render_empty,
                            config=config)
        
        else:
            self.describe_dataframe()
            report = get_error_report(data=self.description,
                                    invalid_data=self.description_invalid,
                                    errors=self.errors, 
                                    is_empty=self.render_empty, 
                                    config=config)
        logger.info("Error report rendered successfully")
        return report.render()
    
    def __render_test_report(self):
        logger.info("Rendering test report")
        self.describe_dataframe()
        report = get_test_report(df=self.description, name=None)
        rendered_report = report.render(self.config)
        logger.info("Test report rendered successfully")
        return rendered_report

    def to_file_test(self):
        logger.info(f"Saving test report to {self.config.file_path}")
        output = Path(self.config.file_path)
        output.write_text(self.__render_test_report(), encoding='utf-8')
        logger.info("Test report saved successfully")

    def to_file(self):
        logger.info(f"Saving report to {self.config.file_path}")
        output = Path(self.config.file_path)
        if hasattr(self, 'errors'):
            logger.info(f"saving error report as {self.config.file_path}")
            output.write_text(self._render_error_report(config=self.config), encoding='utf-8')
            logger.info(f"saved!")

        elif self.render_empty:
            logger.info(f"saving empty report as {self.config.file_path}")
            output.write_text(self._render_empty_report(config=self.config), encoding='utf-8')
            logger.info("saved!")

        elif isinstance(self.df, list):
            logger.info(f"saving comparison report!")
            output.write_text(self._render_comparison(config=self.config), encoding='utf-8')
            logger.info('saved!')
        
        else:
            logger.info(f"saving as {self.config.file_path}")
            if self.config.minimal:
                logger.info("saving minimal version of report!")
                from minify_html import minify
                minified_report = minify(self.get_data_quality_report(config=self.config))
                output.write_text(minified_report, encoding='utf-8')
            else:
                output.write_text(self.get_data_quality_report(config=self.config), encoding='utf-8')
            
            logger.info(f"saved!")