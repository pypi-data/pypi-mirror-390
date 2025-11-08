"""run.py.

Command-line runner
"""
import argparse
import json
import os
import sys
import urllib.parse
from http import HTTPStatus
from typing import Dict
from typing import Iterable
from typing import Optional

import requests
from opensearchpy import RequestsAWSV4SignerAuth
from pds.aossrequestsigner.credentials import get_credentials_via_cognito_userpass_flow  # type: ignore
from pds.aossrequestsigner.errors import Non200HttpStatusError  # type: ignore
from pds.aossrequestsigner.utils import get_checked_filepath  # type: ignore
from pds.aossrequestsigner.utils import parse_path
from pds.aossrequestsigner.utils import process_data_arg


def run(
        aws_region: str,
        aws_account_id: str,
        client_id: str,
        identity_pool_id: str,
        user_pool_id: str,
        cognito_user: str,
        cognito_password: str,
        aoss_endpoint: str,
        request_path: str,
        data: Optional[Dict] = None,
        additional_headers: Optional[Iterable[str]] = None,
        output_filepath: Optional[str] = None,
        verbose: bool = False,
        silent: bool = False,
        prettify_output: bool = False,
):
    """Runner."""
    credentials = get_credentials_via_cognito_userpass_flow(
        aws_region, aws_account_id, client_id, identity_pool_id, user_pool_id, cognito_user, cognito_password
    )

    auth = RequestsAWSV4SignerAuth(credentials, aws_region, "aoss")

    request_f = requests.post if data else requests.get
    url = urllib.parse.urljoin(aoss_endpoint, request_path)
    if verbose:
        print(f"Making {'POST' if data else 'GET'} request to url: {url}", file=sys.stderr)

    body = json.dumps(data)
    if verbose:
        print(f"Including body: {body}", file=sys.stderr)

    headers = {"Content-Type": "application/json"}
    if additional_headers is not None:
        for raw_header_str in additional_headers:
            k, v = raw_header_str.split(":", maxsplit=1)
            headers[k] = v.strip()
    if verbose:
        print(f"Including headers: {json.dumps(headers)}", file=sys.stderr)

    response = request_f(url=url, data=body, auth=auth, headers=headers)  # type: ignore
    if response.status_code != HTTPStatus.OK:
        response_msg = response.content or None
        raise Non200HttpStatusError(response.status_code, description=response_msg)

    output = json.dumps(response.json(), indent=2) if prettify_output else json.dumps(response.json())

    if output_filepath is not None:
        if verbose:
            print(f"Writing response content to {output_filepath}", file=sys.stderr)
        with open(output_filepath, "w+") as out_file:
            out_file.write(output)

    if not silent:
        print(output)


def parse_args() -> argparse.Namespace:
    """Parse arguments."""
    args = argparse.ArgumentParser()

    verbosity_group = args.add_mutually_exclusive_group()
    verbosity_group.add_argument("-v", "--verbose", action="store_true", help="Provide verbose stdout output")
    verbosity_group.add_argument("-s", "--silent", action="store_true", help="Suppress stdout output")

    data_group = args.add_mutually_exclusive_group()

    args.add_argument(
        "path",
        type=parse_path,
        help=(
            "either a full URL (<scheme>://<host>/<path>) or a host-relative path (/<path>) for the request. "
            "Providing a full URL will not override the host endpoint provided as an environment variable "
            "(this may change in future)"
        ),
    )
    data_group.add_argument(
        "-d",
        "--data",
        type=process_data_arg,
        default={},
        help=(
            "Optional body to include in the request.  "
            "See https://opensearch.org/docs/latest/query-dsl/ for details."
        ),
    )
    args.add_argument(
        "-o",
        "--output",
        dest="output_filepath",
        type=get_checked_filepath,
        default=None,
        help="Output filepath for response content",
    )
    args.add_argument(
        "-H",
        "--header",
        dest="headers",
        default=[],
        action="append",
        nargs="*",
        help=(
            'Add an extra header to use in the request, in format "Key: Value". "Content-Type: application/json" is '
            "included by default but may be overwritten."
        ),
    )

    args.add_argument("-p", "--pretty", action="store_true", help="Prettify output with a 2-space-indent JSON format")
    args.add_argument("--noencode", dest="no_url_encode", action="store_true", help="Do not apply url-encoding to path")
    data_group.add_argument("--matchall", dest="apply_match_all", action="store_true", help="Apply match-all OpenSearch query")

    return args.parse_args()


def main():
    """Main."""
    args = parse_args()

    cognito_user = os.environ["REQUEST_SIGNER_COGNITO_USER"]
    cognito_password = os.environ["REQUEST_SIGNER_COGNITO_PASSWORD"]

    aws_account_id = os.environ["REQUEST_SIGNER_AWS_ACCOUNT"]
    aws_region = os.environ.get("AWS_REGION", "us-west-2")
    client_id = os.environ["REQUEST_SIGNER_CLIENT_ID"]
    user_pool_id = os.environ["REQUEST_SIGNER_USER_POOL_ID"]
    identity_pool_id = os.environ["REQUEST_SIGNER_IDENTITY_POOL_ID"]

    aoss_endpoint = os.environ["REQUEST_SIGNER_AOSS_ENDPOINT"]

    match_all_query = {"query": {"match_all": {}}}

    try:
        run(
            aws_region,
            aws_account_id,
            client_id,
            identity_pool_id,
            user_pool_id,
            cognito_user,
            cognito_password,
            aoss_endpoint,
            args.path if args.no_url_encode else urllib.parse.quote(args.path, safe='/'),
            data=match_all_query if args.apply_match_all else args.data,
            additional_headers=args.headers,
            output_filepath=args.output_filepath,
            verbose=args.verbose,
            silent=args.silent,
            prettify_output=args.pretty,
        )
    except Non200HttpStatusError as err:
        if not args.silent:
            print(err, file=sys.stderr)
        exit(1)


if __name__ == '__main__':
    main()
