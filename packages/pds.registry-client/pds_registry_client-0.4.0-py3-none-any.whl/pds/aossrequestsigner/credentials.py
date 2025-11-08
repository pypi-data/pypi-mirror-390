"""Credentials.

Get user credentials from Cognito
"""
import boto3
from botocore.credentials import Credentials


def get_credentials_via_cognito_userpass_flow(
    region: str, account_id: str, client_id: str, identity_pool_id: str, user_pool_id: str, username: str, password: str
) -> Credentials:
    """Get creds via Cognito."""
    # Initialize a Cognito identity provider client
    idp_client = boto3.client("cognito-idp", region_name=region)
    id_client = boto3.client("cognito-identity", region_name=region)

    # Authenticate as cognito user-pool user
    response = idp_client.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH", AuthParameters={"USERNAME": username, "PASSWORD": password}, ClientId=client_id
    )

    # Commenting out, but leaving in for potential testing purposes
    # access_token = response['AuthenticationResult']['AccessToken']
    # refresh_token = response['AuthenticationResult']['RefreshToken']
    id_token = response["AuthenticationResult"]["IdToken"]

    # Authenticate as identity-pool IAM identity
    response_identity_get_id = id_client.get_id(
        AccountId=account_id,
        IdentityPoolId=identity_pool_id,
        Logins={f"cognito-idp.{region}.amazonaws.com/{user_pool_id}": id_token},
    )
    identity_id = response_identity_get_id["IdentityId"]

    # Obtain credentials for IAM identity
    response = id_client.get_credentials_for_identity(
        IdentityId=identity_id,
        Logins={f"cognito-idp.{idp_client.meta.region_name}.amazonaws.com/{user_pool_id}": id_token},
    )

    aws_access_key_id = response["Credentials"]["AccessKeyId"]
    aws_secret_access_key = response["Credentials"]["SecretKey"]
    aws_session_token = response["Credentials"]["SessionToken"]

    return Credentials(aws_access_key_id, aws_secret_access_key, aws_session_token)
