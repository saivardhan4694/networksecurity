from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.entity.config_entity import TrainingPipelineConfig, DataIngestionConfig, DataValidationConfig
from networksecurity.c_logging.logger import logging
from networksecurity.exception.exception import NetworkSecurityException
import sys

if __name__ == "__main__":
    try:
        training_pipeline_config = TrainingPipelineConfig()
        print(training_pipeline_config.artifact_dir)
        data_ingestion_config = DataIngestionConfig(training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config)
        logging.info("Initiating data ingestion phase")
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logging.info("data ingestion phase completed.")

        data_validation_config = DataValidationConfig(training_pipeline_config=training_pipeline_config)
        data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact,data_validation_config=data_validation_config)
        logging.info("Initiating data validation phase")
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("data validation phase completed.")
        print(data_validation_artifact)

    except Exception as e:
        raise NetworkSecurityException(e, sys)
