# Bolt for Python Search Template

> ⚠️ **Beta Notice**: This template demonstrates search functionality that is currently in beta and not yet widely available to all developers. The features shown here are being tested and may change before general availability.

This is a Slack app template for building search functionality using Bolt for Python. It demonstrates how to create custom functions for search and filtering capabilities.

Before getting started, make sure you have a development workspace where you have permissions to install apps. If you don’t have one setup, go ahead and [create one](https://slack.com/create).

## Installation

### Using Slack CLI

Install the latest version of the Slack CLI for your operating system:

- [Slack CLI for macOS & Linux](https://docs.slack.dev/tools/slack-cli/guides/installing-the-slack-cli-for-mac-and-linux/)
- [Slack CLI for Windows](https://docs.slack.dev/tools/slack-cli/guides/installing-the-slack-cli-for-windows/)

You'll also need to log in if this is your first time using the Slack CLI.

```sh
slack login
```

#### Initializing the project

```sh
slack create bolt-python-search --template slack-samples/bolt-python-search-template -branch init
cd bolt-python-search

# Setup your python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the dependencies
pip install .
```

#### Creating the Slack app

```sh
slack install
```

#### Running the app

```sh
slack run
```

<details>
<summary><h3>Using Terminal</h3></summary>

1. Open [https://api.slack.com/apps/new](https://api.slack.com/apps/new) and choose "From an app manifest"
2. Choose the workspace you want to install the application to
3. Copy the contents of [manifest.json](./manifest.json) into the text box that says `*Paste your manifest code here*` (within the JSON tab) and click _Next_
4. Review the configuration and click _Create_
5. Click _Install to Workspace_ and _Allow_ on the screen that follows. You'll then be redirected to the App Configuration dashboard.

#### Environment Variables

Before you can run the app, you'll need to store some environment variables.

1. Open your apps configuration page from this list, click **OAuth & Permissions** in the left hand menu, then copy the Bot User OAuth Token. You will store this in your environment as `SLACK_BOT_TOKEN`.
2. Click ***Basic Information** from the left hand menu and follow the steps in the App-Level Tokens section to create an app-level token with the `connections:write` scope. Copy this token. You will store this in your environment as `SLACK_APP_TOKEN`.

```zsh
# Replace with your app token and bot token
export SLACK_BOT_TOKEN=<your-bot-token>
export SLACK_APP_TOKEN=<your-app-token>
```

### Setup Your Local Project

```sh
# Clone this project onto your machine
git clone https://github.com/slack-samples/bolt-python-search-template.git

# Change into this project directory
cd bolt-python-search-template

# Setup your python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the dependencies
pip install .

# Start your local server
python3 app.py
```

</details>

## Linting

```sh
# Run ruff from root directory for linting
ruff check

# Run ruff from root directory for formatting
ruff format && ruff check --fix
```

## Testing

```sh
# Run pytest from root directory for unit testing
pytest .
```

## Project Structure

### `manifest.json`

`manifest.json` is a configuration for Slack apps. With a manifest, you can create an app with a pre-defined configuration, or adjust the configuration of an existing app.

### `app.py`

`app.py` is the entry point for the application and is the file you'll run to start the server. This project aims to keep this file as thin as possible, primarily using it as a way to route inbound requests.

### `/listeners`

Every incoming request is routed to a "listener". Inside this directory, we group each listener based on the Slack Platform feature used, so `/listeners/events` handles incoming [Events](https://docs.slack.dev/reference/events) requests, `/listeners/functions` handles [custom steps](https://docs.slack.dev/tools/bolt-js/concepts/custom-steps) and so on.

### `/test`

The `/test` directory contains the test suite for this project. It mirrors the structure of the source code, with test files corresponding to their implementation counterparts. For example, tests for files in `/listeners/functions` are located in `/test/listeners/functions`.
