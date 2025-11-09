import logging
import os
from typing import Optional, List
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BigQueryManager:
    """
    A manager class for interacting with Google BigQuery, providing methods to upload DataFrames and CSV files.
    """

    def __init__(self, credentials_file: Optional[str] = None):
        self.credentials_file = credentials_file or os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
        if not self.credentials_file:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON not set in .env")
        self.client = self._get_bq_client()

    def _get_bq_client(self):
        """Initialize and return the BigQuery client."""
        try:
            creds = service_account.Credentials.from_service_account_file(self.credentials_file)
            return bigquery.Client(credentials=creds)
        except Exception as e:
            logger.error("Failed to load BigQuery client credentials: %s", e)
            raise

    def upload_dataframe(self, df: pd.DataFrame, dataset_id: str, table_id: str, project_id: Optional[str] = None, if_exists: str = 'replace') -> str:
        """
        Upload a pandas DataFrame to BigQuery.

        :param df: The DataFrame to upload.
        :param dataset_id: The BigQuery dataset ID.
        :param table_id: The BigQuery table ID.
        :param project_id: The Google Cloud project ID. If None, uses the client's project.
        :param if_exists: What to do if the table exists. Options: 'replace', 'append', 'fail'.
        :return: The job ID of the load job.
        """
        try:
            project = project_id or self.client.project
            table_id_full = f"{project}.{dataset_id}.{table_id}"

            job_config = bigquery.LoadJobConfig()
            if if_exists == 'replace':
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
            elif if_exists == 'append':
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
            elif if_exists == 'fail':
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_EMPTY
            else:
                raise ValueError("if_exists must be 'replace', 'append', or 'fail'")

            job = self.client.load_table_from_dataframe(df, table_id_full, job_config=job_config)
            job.result()  # Wait for the job to complete
            logger.info("Uploaded DataFrame to BigQuery table %s.%s", dataset_id, table_id)
            return job.job_id
        except Exception as e:
            logger.error("Error uploading DataFrame: %s", e)
            raise

    def upload_csv(self, csv_path: str, dataset_id: str, table_id: str, project_id: Optional[str] = None, if_exists: str = 'replace', skip_leading_rows: int = 1) -> str:
        """
        Upload a CSV file to BigQuery.

        :param csv_path: Path to the CSV file.
        :param dataset_id: The BigQuery dataset ID.
        :param table_id: The BigQuery table ID.
        :param project_id: The Google Cloud project ID. If None, uses the client's project.
        :param if_exists: What to do if the table exists. Options: 'replace', 'append', 'fail'.
        :param skip_leading_rows: Number of rows to skip at the beginning of the CSV (e.g., header).
        :return: The job ID of the load job.
        """
        try:
            project = project_id or self.client.project
            table_id_full = f"{project}.{dataset_id}.{table_id}"

            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.CSV,
                skip_leading_rows=skip_leading_rows,
                autodetect=True,
            )
            if if_exists == 'replace':
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
            elif if_exists == 'append':
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
            elif if_exists == 'fail':
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_EMPTY

            with open(csv_path, 'rb') as source_file:
                job = self.client.load_table_from_file(source_file, table_id_full, job_config=job_config)
            job.result()  # Wait for the job to complete
            logger.info("Uploaded CSV to BigQuery table %s.%s", dataset_id, table_id)
            return job.job_id
        except Exception as e:
            logger.error("Error uploading CSV: %s", e)
            raise

    def list_datasets(self, project_id: Optional[str] = None) -> List[str]:
        """
        List all datasets in the project.

        :param project_id: The Google Cloud project ID. If None, uses the client's project.
        :return: List of dataset IDs.
        """
        try:
            project = project_id or self.client.project
            datasets = self.client.list_datasets(project=project)
            return [dataset.dataset_id for dataset in datasets]
        except Exception as e:
            logger.error("Error listing datasets: %s", e)
            raise

    def list_tables(self, dataset_id: str, project_id: Optional[str] = None) -> List[str]:
        """
        List all tables in a dataset.

        :param dataset_id: The BigQuery dataset ID.
        :param project_id: The Google Cloud project ID. If None, uses the client's project.
        :return: List of table IDs.
        """
        try:
            project = project_id or self.client.project
            dataset_ref = bigquery.DatasetReference(project, dataset_id)
            tables = self.client.list_tables(dataset_ref)
            return [table.table_id for table in tables]
        except Exception as e:
            logger.error("Error listing tables: %s", e)
            raise

    def create_dataset(self, dataset_id: str, project_id: Optional[str] = None) -> None:
        """
        Create a new dataset in BigQuery.

        :param dataset_id: The BigQuery dataset ID.
        :param project_id: The Google Cloud project ID. If None, uses the client's project.
        """
        try:
            project = project_id or self.client.project
            dataset_ref = bigquery.DatasetReference(project, dataset_id)
            dataset = bigquery.Dataset(dataset_ref)
            self.client.create_dataset(dataset)
            logger.info("Created dataset %s in project %s", dataset_id, project)
        except Exception as e:
            logger.error("Error creating dataset: %s", e)
            raise

    def create_table(self, dataset_id: str, table_id: str, schema: List[bigquery.SchemaField], project_id: Optional[str] = None) -> None:
        """
        Create a new table in BigQuery with the given schema.

        :param dataset_id: The BigQuery dataset ID.
        :param table_id: The BigQuery table ID.
        :param schema: List of SchemaField objects defining the table schema.
        :param project_id: The Google Cloud project ID. If None, uses the client's project.
        """
        try:
            project = project_id or self.client.project
            table_ref = bigquery.TableReference(bigquery.DatasetReference(project, dataset_id), table_id)
            table = bigquery.Table(table_ref, schema=schema)
            self.client.create_table(table)
            logger.info("Created table %s.%s in project %s", dataset_id, table_id, project)
        except Exception as e:
            logger.error("Error creating table: %s", e)
            raise