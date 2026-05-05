"""
Conftest for pytest - shared fixtures and configuration
"""

import pytest
import os
from pathlib import Path


@pytest.fixture(scope="session")
def project_root():
    """Get project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def aws_credentials():
    """Mock AWS credentials for testing"""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture
def mock_s3_bucket():
    """Create mock S3 bucket for testing"""
    import boto3
    from moto import mock_s3
    
    with mock_s3():
        conn = boto3.resource('s3', region_name='us-east-1')
        conn.create_bucket(Bucket='test-bucket')
        yield conn


@pytest.fixture
def mock_sqs_queue():
    """Create mock SQS queue for testing"""
    import boto3
    from moto import mock_sqs
    
    with mock_sqs():
        conn = boto3.resource('sqs', region_name='us-east-1')
        queue = conn.create_queue(QueueName='test-queue')
        yield queue
