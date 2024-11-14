import os
import sys
from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.c_logging.logger import logging
from networksecurity.constants import training_pipeline
from networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file

from scipy.stats import ks_2samp
import pandas as pd

class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_config: DataValidationConfig):
        
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(training_pipeline.SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def validate_no_of_columns(self, df: pd.DataFrame) -> bool:
        try:
            no_of_columns = len(self._schema_config)
            logging.info(f"required no.of columns {no_of_columns}")
            logging.info(f"data frame has columns: {len(df.columns)}")

            if len(df.columns) == no_of_columns :
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def validate_data_type(self, df: pd.DataFrame) -> bool:
        try:
            data_columns = list(df.columns.to_list())
            schema_columns_list = self._schema_config["columns"]
            expected_schema_dict = {column_name: data_type for column_info_dict in schema_columns_list for column_name, data_type in column_info_dict.items()}
            for column in data_columns:
                if df[column].dtype != expected_schema_dict[column]:
                    return False
            return True
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def detect_dataset_drift(self, base_df, current_df, threshold = 0.05) -> bool:
        try:
            status = True
            report = {}
            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]
                is_sample_dist = ks_2samp(d1, d2)
                if threshold <= is_sample_dist.pvalue:
                    data_drift_found = False
                else:
                    data_drift_found = True
                    status = False
                report.update({column:{
                    "p_value" : float(is_sample_dist.pvalue),
                    "drift_status": data_drift_found
                }})
            drift_report_file_path = self.data_validation_config.drift_report_file_path
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path, exist_ok= True)
            write_yaml_file(file_path= drift_report_file_path, content=report)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            ## read the train and test data from the folder path
            train_dataframe = DataValidation.read_data(train_file_path)
            test_dataframe = DataValidation.read_data(test_file_path)
            
            ## Validate no.of columns
            status = self.validate_no_of_columns(df=train_dataframe)
            if not status:
                error_message = f"Train dataframe does not contain all columns./n"
            status = self.validate_no_of_columns(df=test_dataframe)
            if not status:
                error_message = f"Test dataframe does not contain all columns./n"

            ## Validate data types
            status = self.validate_data_type(df=train_dataframe)
            if not status:
                error_message = f"Train dataframe has some inconsistent data types./n"
            status = self.validate_data_type(df=test_dataframe)
            if not status:
                error_message = f"Test dataframe has some inconsistent data types./n"

            ## check for datadrift
            status = self.detect_dataset_drift(base_df=train_dataframe, current_df=test_dataframe)
            dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path, exist_ok= True)

            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path, index=False, header=True
            )
            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path, index=False, header=True
            )

            if not status:
                error_message = f"Data drift detected./n"

                data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_ingestion_artifact.trained_file_path,
                valid_test_file_path=self.data_ingestion_artifact.test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )
            return data_validation_artifact
        
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
        
