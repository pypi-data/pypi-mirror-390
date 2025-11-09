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

That's why I built this SDK. It's a Pythonic wrapper around the Unipile API that
handles the heavy lifting for you. Now, you can retrieve user profiles, search
for candidates, and send messages with just a few lines of code. It's the tool I
wish I had when I started, and I hope it makes your life easier too.

## QuickStart

Get up and running with the Unipile Python SDK in just a few steps.

Demonstration of the work:

https://github.com/user-attachments/assets/4c15716a-d314-429e-9fe4-c6cf654073fd

### Installation

```bash
pip install i-unipile-sdk  # or add it into requirements and install it
```

Alternatively, you can use [uv](https://docs.astral.sh/uv/guides/projects/) and
add unipile SDK into your existing project.

```bash
uv add i-unipile-sdk
```

### Configuration

#### 1. Getting required credentials

You need to get some data before processing:

- Get DNS (`base_url`), can be copied from
  [dashboard](https://dashboard.unipile.com/).
- Generate your API token (`auth`) in
  [access tokens](https://dashboard.unipile.com/access-tokens)
- Connect account and get it's id (`default_account_id`), can be copied next to
account name in the [accounts](https://dashboard.unipile.com/accounts) section.

All related information can be found in the
[getting-started](https://developer.unipile.com/docs/getting-started)
documentation. I recommended to watch a quick start video first.

#### 2. Initialize client

You can configure the client by passing an `ClientOptions` object directly:

```python
from unipile_sdk import Client
from unipile_sdk.client import ClientOptions

options = ClientOptions(
    auth="your_api_key_here",  # Your Unipile API Key
    base_url="https://your_base_url_here",  # The Unipile API base URL
    default_account_id="your_account_id_here",  # The ID of the account to use
)

client = Client(options=options)

me = client.users.me()
print(f"My occupation is: {me.occupation}")
```

## Usage Examples

This section showcases some of the more advanced features of the SDK. For
brevity, it is assumed that the `client` object has been initialized as shown
in the [QuickStart](#quickstart) section.

To use examples, you need to import the relevant models and functions from the
SDK, e.g., `LinkedinSearchPayload`, `iterate_paginated_api`, and `Client`:

```python
from unipile_sdk.models import LinkedinSearchPayload, NotFoundType
from unipile_sdk.helpers import iterate_paginated_api
from unipile_sdk.errors import APIResponseError
```

### List Accounts

Retrieve a list of all connected accounts.

```python
accounts = client.accounts.accounts(limit=100)
for account in accounts.items:
    print(f"Account: {account.type} - {account.name}")
```

### LinkedIn Search

Perform a detailed search for people on LinkedIn. The SDK will handle pagination
for you.

```python
payload = LinkedinSearchPayload(
    api="classic", category="people", keywords="Software Engineer, Programmer"
)

for person in iterate_paginated_api(
    client.ln_search.search, payload=payload, max_total=10
):
    print(f"Found Person: {person.name} ({person.id})")
```

### Retrieve Company by Name

Fetch company details using its name.

```python
company = client.ln_search.retrieve_company(identifier="LinkedIn")
print(f"Company: {company.name} ({company.id})")
```

> For more examples, please check the `tests/integration` directory. The
> following examples are also available as Python files in the `examples`
> directory.

## Drawbacks

This SDK is currently under development and should be considered a work in
progress. Here are a few things to keep in mind:

- **Incomplete API Coverage:** The SDK does not cover the entire Unipile API.
  The primary focus has been on the LinkedIn-related endpoints.
- **Potential for Bugs:** As with any active development project, there may be
  bugs or incomplete features.

Contributions to improve the SDK and expand its coverage are welcome.

## Contributing

Contributions are welcome! Here's how you can get started with the development
of the SDK.

### Development Setup

1. Clone the repository.
2. Install the development dependencies:

   ```bash
   git clone repo-url
   cd repo-directory
   uv pip install -e ".[dev]" # or `pip install -e ".[dev]"`
   ```

### Running Tests

To run the tests, you need to set up your test environment variables. Create a
`.tests.env` file in the root of the project:

`UNIPILE_BASE_URL` should be without protocol (like api.unipile.com...).


```
UNIPILE_ACCESS_TOKEN=your_api_token_here
UNIPILE_BASE_URL=your_unipile_api_basi_url
UNIPILE_ACCOUNT=your__account_id_here

UNIPILE_LN_DEFAULT_USER_URN=your_default_user_urn_here
UNIPILE_LN_USER_URN_TO_MESSAGE=your_target_user_urn_here
```

Then, run the tests using `pytest`:

```bash
pytest
```

#### Activities tests

Some tests that perform actions like sending messages are marked as `messaging`
and are skipped by default. To run them, use the `--activities` flag:

If you specify `UNIPILE_LN_USER_URN_TO_MESSAGE`, you can test messaging
functionality by sending a message to that user URN. Be careful this can
actually send a many same messages on LinkedIn. Use a test account or a
controlled recipient.

There additional `test_send_message_to_attendees` test, which sends messages
with specific logic. If there found only one message (usually invite message),
it sends a test message to that attendee and asserts success. So expect some
"thank you for connection" messages if `--activities` flag is used.

```bash
pytest --messaging
```
