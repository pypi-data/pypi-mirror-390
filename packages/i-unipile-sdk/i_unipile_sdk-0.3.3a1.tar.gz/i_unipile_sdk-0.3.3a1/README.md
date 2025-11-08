# Unipile Python SDK

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An unofficial, fully functional Python SDK for the Unipile API.

## Why?

Integrating with powerful APIs can be complex, unfortunately Unipile does not
provide an official Python client (actual for 2025), only
[Node.JS](https://developer.unipile.com/docs/sdk) based official client.

When I started working with the Unipile API and Python to automate LinkedIn
interactions, I found myself writing a lot of boilerplate code to handle
authentication, make HTTP requests, and parse responses. It was repetitive and
error-prone. I wanted a simpler way to interact with the API, so I could focus
on building features, not on the underlying HTTP calls.

That's why I built this SDK. It's a Pythonic wrapper around the Unipile API
that handles the heavy lifting for you. Now, you can retrieve user profiles,
search for candidates, and send messages with just a few lines of code. It's
the tool I wish I had when I started, and I hope it makes your life easier too.

## QuickStart

Get up and running with the Unipile Python SDK in just a few steps.

### Installation

It is recommended to use [uv](https://github.com/astral-sh/uv), a fast, next-generation Python package installer.

```bash
# Using uv (recommended)
uv pip install i-unipile-sdk
```

Alternatively, you can use `pip`:

```bash
pip install i-unipile-sdk
```

### Configuration

#### 1. Getting required credentials

You need to generate your API token (`auth`), get DNS (`base_url`), connect
account and get it's id (`default_account_id`).

All related information can be found in the
[getting-started](https://developer.unipile.com/docs/getting-started)
documentation. I recommended to watch a quick start video first.

#### 2. Initialize client

You can configure the client by passing an `ClientOptions` object directly:

```python
from unipile_sdk import Client
from unipile_sdk.client import ClientOptions

options = ClientOptions(
    auth="your_api_key_here", # Your Unipile API Key
    base_url="https://api.unipile.com", # The Unipile API base URL
    default_account_id="your_account_id_here", # The ID of the account to use
)

client = Client(options=options)
```

Alternatively for convenience, especially in development and testing, you can
also configure the client using environment variables. The client will
automatically pick them up if no direct configuration is provided.

```bash
export UNIPILE_BASE_URL="api.unipile.com"
export UNIPILE_ACCESS_TOKEN="your_api_key_here"
export UNIPILE_ACCOUNT="your_account_id_here"

client = Client()
```

## Usage

This section showcases some of the more advanced features of the SDK.

### Advanced LinkedIn Search

Perform a detailed search for people on LinkedIn. The SDK will handle pagination for you.

```python
from unipile_sdk.models import LinkedinSearchPayload
from unipile_sdk.helpers import iterate_paginated_api

payload = LinkedinSearchPayload(
    api="classic",
    category="people",
    keywords="Software Engineer in Test"
)

for person in iterate_paginated_api(client.search.search, payload=payload, max_total=50):
    print(f"Found Person: {person.name} ({person.id})")
```

### Send a LinkedIn Message

Send a message to a LinkedIn user. You'll need the user's URN.

```python
# Note: This is a simplified example. You'll need a valid chat_id.
# You can get a chat_id by listing chats for an attendee.
try:
    chat_id = "some_chat_id"
    client.messages.send_message(
        chat_id=chat_id,
        text="Hello from the Unipile SDK!"
    )
    print("Message sent successfully!")
except Exception as e:
    print(f"Failed to send message: {e}")

```

### Error Handling

The SDK raises custom exceptions for different types of errors.

```python
from unipile_sdk.errors import APIResponseError
from unipile_sdk.models import NotFoundType

try:
    client.search.retrieve_company(identifier="a-company-that-does-not-exist")
except APIResponseError as e:
    if e.error == NotFoundType.ERRORS_RESOURCE_NOT_FOUND:
        print("Caught a 'Not Found' error, as expected.")
    else:
        raise e
```

## Drawbacks

This SDK is currently under development and should be considered a work in
progress. Here are a few things to keep in mind:

- **Incomplete API Coverage:** The SDK does not cover the entire Unipile API.
  The primary focus has been on the LinkedIn-related endpoints.
- **Potential for Bugs:** As with any active development project, there may be
  bugs or incomplete features.

Contributions to improve the SDK and expand its coverage are welcome.

## Contributing

Contributions are welcome! Here's how you can get started with the development of the SDK.

### Development Setup

1.  Clone the repository.
2.  Install the development dependencies:

    ```bash
    git clone repo-url
    cd repo-directory
    uv pip install -e ".[dev]" # or `pip install -e ".[dev]"`
    ```

### Running Tests

To run the tests, you need to set up your test environment variables. Create a `.tests.env` file in the root of the project:

```
UNIPILE_BASE_URL=api.unipile.com
UNIPILE_ACCESS_TOKEN=your_api_key_here
UNIPILE_ACCOUNT=your_default_account_id_here
UNIPILE_TEST_LN_ATTENDEE=an_attendee_id
```

Then, run the tests using `pytest`:

```bash
pytest
```

Some tests that perform actions like sending messages are marked as `messaging` and are skipped by default. To run them, use the `--messaging` flag:

```bash
pytest --messaging
```
