# Learning Coder's API

Coder is an OSS Cloud Development Environment platform

## Programming language

This example uses Python and is a command line application

## API

Coder has a REST API where a user's session token is provided in a header to authenticate the app to the Coder deployment 

## Authentication

Credential is a session token. It is read as environment variable along with the Coder Access URL, API Route and Organization Id which you place in `.zshrc` or `.bashrc` of the host computer running the Docker daemon.

```sh
# set environment variables
export CODER_URL=""
export CODER_SESSION_TOKEN=""
export CODER_API_ROUTE="api/v2"
export CODER_ORG_ID=""
```

Create a Coder Session Token either:

1. `http://your-access-url/cli-auth` from a browser
1. In the Coder UI or with Coder CLI, create a token `coder token create`

> If using the dev container, you cannot use localhost but instead the tunnel proxy URL or our host machine URL
> where Coder is deployed e.g., `https://*************.pit-1.try.coder.app`

Obtain the Coder deployment's Organization Id with `http://your-access-url/api/v2/users/me` from a browser

## Run the app

### as a binary

> Below are build instructions instead of including a large binary and build artifacts in this repo

1. Use a build tool like 'pip3 install pystaller'
1. 'pyinstaller --onefile --workpath /path/to/build/directory coder-cli.py'
1. Run `./coder-cli` from the `./dist` directory or add the directory to your path and run `coder-cli`

### from source
`cd` into the repo directory and run the app

```sh
python3 coder-cli.py
```

Alternatively, see the dev container approach below which autostarts the app.

## The app 

The app runs as a while loop prompting the user for actions like:
1. list templates
1. list workspaces
1. search workspaces with a filter e.g., `owner:me` or `flask`
1. list all users
1. show authenticated user information
1. list environment variable values with session token partially masked
1. list deployment build information
1. start or stop a workspace from a list
1. quit the app

When the app starts, it checks that environment variables have been entered and does test API calls to retrieve Coder release, # of users, templates and workspaces.

## Dev Container

Notice the `Dockerfile` and `devcontainer.json` which uses a slim Python container image in the Dockerfile, and passes the Coder authentication environment variables into the dev container.

This approach frees you up from having a specific Python version and module on your local machine e.g., Mac and let the dev container set all of this up. You do still need to set the environment variables locally which is more secure and better than putting into the repo with .gitignore. ☠️

## Resources

[Python Mac versions](https://www.python.org/downloads/macos/)

[Coder API docs](https://coder.com/docs/api)

[sharkymark Coder API call examples](https://github.com/sharkymark/v2-templates/blob/main/api.md)

[dev container spec](https://containers.dev/implementors/json_reference/)