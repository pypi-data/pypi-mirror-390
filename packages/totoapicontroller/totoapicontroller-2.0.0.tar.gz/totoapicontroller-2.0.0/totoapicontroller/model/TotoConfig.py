from enum import Enum
import json
import os
from abc import ABC, abstractmethod
from totoapicontroller.TotoLogger import TotoLogger
from totoapicontroller.model.singleton import singleton
from google.cloud import secretmanager

import boto3
from botocore.exceptions import ClientError

class CloudProvider(Enum):
    AWS = 1
    GCP = 2

class TotoConfig(ABC): 
    
    jwt_key: str
    jwt_expected_audience: str
    environment: str
    
    def __init__(self) -> None:
        
        self.logger = TotoLogger(self.get_api_name())
        self.environment = os.getenv("ENVIRONMENT", 'dev')
        self.hyperscaler = os.getenv('HYPERSCALER', 'gcp') 
        self.region = os.getenv('AWS_REGION', 'eu-north-1') if self.hyperscaler == 'aws' else os.getenv('GCP_REGION', 'europe-west1')

        self.logger.log("INIT", f"Loading Configuration.. Hyperscaler: {self.hyperscaler}, Environment: {self.environment}, Region: {self.region}")

        self.jwt_key = self.access_secret_version("jwt-signing-key")
        self.jwt_expected_audience = self.access_secret_version("toto-expected-audience")
        
    
    @abstractmethod
    def get_api_name(self) -> str: 
        pass
    
    def is_path_excluded(self, path: str) -> bool:
        return False
    
    def access_secret_version(self, secret_id: str):
        """Retrieves a secret from the right cloud provider, based on the environment

        Args:
            secret_id (str): _description_

        Returns:
            _type_: _description_
        """
        
        if self.hyperscaler == 'gcp':
            self.logger.log("INIT", f"Accessing secret {secret_id} for hyperscaler {self.hyperscaler}")
            return self.access_gcp_secret_version(secret_id)
        else:
            aws_region = os.getenv('AWS_REGION', 'eu-north-1')
            self.logger.log("INIT", f"Accessing secret {self.environment}/{secret_id} for hyperscaler {self.hyperscaler} in region {aws_region}")
            return self.access_aws_secret_version(f"{self.environment}/{secret_id}", aws_region)

    def access_gcp_secret_version(self, secret_id, version_id="latest"):
        """
        Retrieves a Secret on GCP Secret Manager
        """

        project_id = os.environ["GCP_PID"]

        # Create the Secret Manager client
        client = secretmanager.SecretManagerServiceClient()

        # Build the resource name of the secret version
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

        # Access the secret version
        response = client.access_secret_version(name=name)

        # Extract the secret payload
        payload = response.payload.data.decode("UTF-8")

        return payload


    def access_aws_secret_version(self, secret_name, region_name):
        """
        Retrieves a Secret on AWS Secrets Manager
        """

        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name, 
        )

        try:
            get_secret_value_response = client.get_secret_value( SecretId=secret_name )
        except ClientError as e:
            raise e

        secret = get_secret_value_response['SecretString']
        
        return secret
