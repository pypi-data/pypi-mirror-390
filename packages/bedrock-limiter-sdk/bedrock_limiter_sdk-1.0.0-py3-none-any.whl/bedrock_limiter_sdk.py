"""
Bedrock Token Limiter SDK - Drop-in replacement for boto3 bedrock-runtime client.

This SDK provides a simple wrapper around boto3's Bedrock client that adds:
1. User identification via X-User-ID header
2. API key authentication via X-API-Key header
3. Automatic routing through your token limiter proxy

The wrapper maintains full compatibility with boto3's Bedrock SDK - all methods
work exactly the same, including streaming.

Installation:
    pip install boto3

Usage:
    from bedrock_limiter_sdk import BedrockClient

    # Create client with your credentials
    bedrock = BedrockClient(
        user_id='alice@example.com',
        api_key='your-api-key-here',
        endpoint_url='http://your-alb.elb.amazonaws.com'
    )

    # Use exactly like normal boto3 Bedrock client
    response = bedrock.converse(
        modelId='anthropic.claude-3-haiku',
        messages=[
            {"role": "user", "content": [{"text": "Hello!"}]}
        ]
    )

    # Streaming works too
    response = bedrock.converse_stream(...)
    for event in response['stream']:
        # Process events normally
        pass

Compatibility:
    ✓ boto3 Bedrock SDK (converse, converse_stream, invoke_model, etc.)
    ✓ Langchain (pass client to ChatBedrock)
    ✓ Strands SDK (pass client to BedrockModel)
    ✓ Any framework that accepts a boto3 client
"""

import boto3
from botocore.config import Config
from typing import Optional


class BedrockClient:
    """
    Bedrock client with automatic user identification and API key authentication.

    This class wraps boto3's bedrock-runtime client and automatically injects
    X-User-ID and X-API-Key headers into every request.

    Args:
        user_id: Your user identifier (email, username, etc.)
        api_key: Your API key (obtain from administrator)
        endpoint_url: Token limiter endpoint URL
        region_name: AWS region (default: us-east-1)
    """

    def __init__(
        self,
        user_id: str,
        api_key: str,
        endpoint_url: str,
        region_name: str = 'us-east-1'
    ):
        """
        Create a Bedrock client with automatic authentication.

        Example:
            bedrock = BedrockClient(
                user_id='alice@example.com',
                api_key='abc123...',
                endpoint_url='http://my-alb.elb.amazonaws.com'
            )
        """
        if not user_id:
            raise ValueError("user_id is required")
        if not api_key:
            raise ValueError("api_key is required")
        if not endpoint_url:
            raise ValueError("endpoint_url is required")

        self.user_id = user_id
        self.api_key = api_key

        # Create underlying boto3 client
        self._client = boto3.client(
            service_name='bedrock-runtime',
            region_name=region_name,
            endpoint_url=endpoint_url,
            config=Config(signature_version='v4')
        )

        # Register event handler to inject authentication headers
        # Use 'before-sign' to ensure headers are added before signature calculation
        self._client.meta.events.register_first('before-sign', self._inject_auth_headers)

    def _inject_auth_headers(self, request, **kwargs):
        """
        Inject authentication headers into every request.

        This runs automatically before each API call.
        """
        if hasattr(request, 'headers'):
            request.headers['X-User-ID'] = self.user_id
            request.headers['X-API-Key'] = self.api_key

    # Proxy all boto3 methods to the underlying client
    def __getattr__(self, name):
        """
        Forward all method calls to the underlying boto3 client.

        This allows the wrapper to behave exactly like boto3.client('bedrock-runtime').
        """
        return getattr(self._client, name)


# Convenience function for backwards compatibility
def get_client(
    user_id: str,
    api_key: str,
    endpoint_url: str,
    region_name: str = 'us-east-1'
) -> BedrockClient:
    """
    Create a Bedrock client with authentication (function-style API).

    Args:
        user_id: Your user identifier
        api_key: Your API key
        endpoint_url: Token limiter endpoint URL
        region_name: AWS region (default: us-east-1)

    Returns:
        BedrockClient instance

    Example:
        from bedrock_limiter_sdk import get_client

        bedrock = get_client(
            user_id='alice@example.com',
            api_key='your-api-key',
            endpoint_url='http://your-alb.elb.amazonaws.com'
        )
    """
    return BedrockClient(
        user_id=user_id,
        api_key=api_key,
        endpoint_url=endpoint_url,
        region_name=region_name
    )


# For Langchain integration
class BedrockClientForLangchain(BedrockClient):
    """
    Bedrock client optimized for Langchain integration.

    Usage with Langchain:
        from bedrock_limiter_sdk import BedrockClientForLangchain
        from langchain_aws import ChatBedrock

        bedrock_client = BedrockClientForLangchain(
            user_id='alice@example.com',
            api_key='your-api-key',
            endpoint_url='http://your-alb.elb.amazonaws.com'
        )

        llm = ChatBedrock(
            client=bedrock_client,
            model_id='anthropic.claude-3-haiku',
            streaming=True
        )

        response = llm.invoke("Hello!")
    """
    pass  # Same functionality, just a separate class for documentation


# For Strands SDK integration
class BedrockClientForStrands(BedrockClient):
    """
    Bedrock client optimized for Strands SDK integration.

    Usage with Strands:
        from bedrock_limiter_sdk import BedrockClientForStrands
        from strands.models import BedrockModel

        bedrock_client = BedrockClientForStrands(
            user_id='alice@example.com',
            api_key='your-api-key',
            endpoint_url='http://your-alb.elb.amazonaws.com'
        )

        model = BedrockModel(
            model_id='anthropic.claude-3-haiku',
            boto_session=None,  # Not needed when passing client directly
        )
        model._client = bedrock_client  # Replace the client

        # Use model normally with Strands
        agent = Agent(model=model, ...)
    """
    pass  # Same functionality, just a separate class for documentation
