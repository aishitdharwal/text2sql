"""
CloudWatch-based logging configuration for the application
"""
import logging
import sys
import json
import os
from datetime import datetime
from typing import Optional
import boto3
from botocore.exceptions import ClientError

class CloudWatchHandler(logging.Handler):
    """
    Custom handler that sends logs to AWS CloudWatch Logs
    """
    def __init__(
        self, 
        log_group: str, 
        log_stream: str,
        region_name: str = 'ap-south-1',
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None
    ):
        super().__init__()
        
        self.log_group = log_group
        self.log_stream = log_stream
        
        # Initialize CloudWatch Logs client
        session_kwargs = {'region_name': region_name}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs['aws_access_key_id'] = aws_access_key_id
            session_kwargs['aws_secret_access_key'] = aws_secret_access_key
        
        self.client = boto3.client('logs', **session_kwargs)
        self.sequence_token = None
        
        # Ensure log group and stream exist
        self._ensure_log_group_exists()
        self._ensure_log_stream_exists()
    
    def _ensure_log_group_exists(self):
        """Create log group if it doesn't exist"""
        try:
            self.client.create_log_group(logGroupName=self.log_group)
            print(f"Created CloudWatch log group: {self.log_group}")
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass  # Log group already exists
        except ClientError as e:
            print(f"Error creating log group: {e}")
    
    def _ensure_log_stream_exists(self):
        """Create log stream if it doesn't exist"""
        try:
            self.client.create_log_stream(
                logGroupName=self.log_group,
                logStreamName=self.log_stream
            )
            print(f"Created CloudWatch log stream: {self.log_stream}")
        except self.client.exceptions.ResourceAlreadyExistsException:
            # Get the sequence token for existing stream
            self._get_sequence_token()
        except ClientError as e:
            print(f"Error creating log stream: {e}")
    
    def _get_sequence_token(self):
        """Get the current sequence token for the log stream"""
        try:
            response = self.client.describe_log_streams(
                logGroupName=self.log_group,
                logStreamNamePrefix=self.log_stream
            )
            if response['logStreams']:
                self.sequence_token = response['logStreams'][0].get('uploadSequenceToken')
        except ClientError as e:
            print(f"Error getting sequence token: {e}")
    
    def emit(self, record):
        """Send log record to CloudWatch"""
        try:
            log_entry = {
                'timestamp': int(record.created * 1000),  # CloudWatch expects milliseconds
                'message': self.format(record)
            }
            
            # Prepare the request
            put_kwargs = {
                'logGroupName': self.log_group,
                'logStreamName': self.log_stream,
                'logEvents': [log_entry]
            }
            
            if self.sequence_token:
                put_kwargs['sequenceToken'] = self.sequence_token
            
            # Send to CloudWatch
            response = self.client.put_log_events(**put_kwargs)
            self.sequence_token = response.get('nextSequenceToken')
            
        except ClientError as e:
            # If sequence token is invalid, get a new one and retry
            if e.response['Error']['Code'] == 'InvalidSequenceTokenException':
                self._get_sequence_token()
                self.emit(record)  # Retry
            else:
                print(f"CloudWatch logging error: {e}")
        except Exception as e:
            print(f"Unexpected error in CloudWatch logging: {e}")

class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging
    """
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)

def setup_logging(
    app_name: str = "text2sql",
    log_level: str = "INFO",
    log_group: Optional[str] = None,
    region_name: str = 'ap-south-1',
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    enable_console: bool = True
):
    """
    Setup CloudWatch-based logging configuration
    
    Args:
        app_name: Name of the application
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_group: CloudWatch log group name (defaults to /aws/text2sql/{app_name})
        region_name: AWS region for CloudWatch
        aws_access_key_id: AWS access key (optional, uses IAM role if not provided)
        aws_secret_access_key: AWS secret key (optional, uses IAM role if not provided)
        enable_console: Whether to also log to console (useful for development)
    """
    
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Default log group name
    if log_group is None:
        log_group = f"/aws/text2sql/{app_name}"
    
    # Create log stream name with timestamp for uniqueness
    log_stream = f"{app_name}-{datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')}"
    
    # Create formatters
    console_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    json_formatter = JSONFormatter()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all levels
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler (optional, for development)
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # CloudWatch handler
    try:
        cloudwatch_handler = CloudWatchHandler(
            log_group=log_group,
            log_stream=log_stream,
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        cloudwatch_handler.setLevel(numeric_level)
        cloudwatch_handler.setFormatter(json_formatter)
        root_logger.addHandler(cloudwatch_handler)
        
        print(f"✓ CloudWatch logging configured")
        print(f"  Log Group: {log_group}")
        print(f"  Log Stream: {log_stream}")
        print(f"  Region: {region_name}")
        
    except Exception as e:
        print(f"✗ Failed to setup CloudWatch logging: {e}")
        print("  Falling back to console-only logging")
        if not enable_console:
            # Add console handler as fallback
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(numeric_level)
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
    
    # Set third-party library log levels to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured for {app_name}", extra={
        "extra_fields": {
            "log_level": log_level,
            "log_group": log_group,
            "log_stream": log_stream,
            "region": region_name
        }
    })
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

def log_with_context(logger: logging.Logger, level: str, message: str, **kwargs):
    """
    Log a message with additional context
    
    Args:
        logger: Logger instance
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        **kwargs: Additional context to include in the log
    """
    log_func = getattr(logger, level.lower())
    log_func(message, extra={"extra_fields": kwargs})
