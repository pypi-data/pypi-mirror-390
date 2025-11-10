# Basecamp API

This package allows interaction with the [Basecamp 3 API](https://github.com/basecamp/bc3-api) using Python.

## Installation

The package can be installed from your terminal by typing:

```bash
pip install bcapi
```

You need to have Python 3.11 or higher installed.

## Set up your environment

You need to create a `.env` file in the root of your project and add your Basecamp account ID, client ID, client secret, and redirect URI. You'll find these on [your OAuth app page](https://launchpad.37signals.com/integrations/<your-app-id>). You'll need to login with your Basecamp account to access this.

Your `.env` file should contain:
```
BASECAMP_ACCOUNT_ID=your_account_id
BASECAMP_CLIENT_ID=your_client_id
BASECAMP_CLIENT_SECRET=your_client_secret
BASECAMP_REDIRECT_URI=your_redirect_uri
BASECAMP_APP_NAME=your_app_name
BASECAMP_REFRESH_TOKEN=your_refresh_token_once_obtained
BASECAMP_API_URL=https://3.basecampapi.com/your_account_id
BASECAMP_AUTH_URL=https://launchpad.37signals.com/authorization/new
BASECAMP_TOKEN_URL=https://launchpad.37signals.com/authorization/token
BASECAMP_USER_AGENT=YourAppName (your-email@example.com)
```

### Get a refresh token

You also need a refresh token. To interact with Basecamp's API, you must provide an access token for every API request. Access tokens expire after two weeks.

A refresh token allows you to automatically regenerate new access tokens. You only have to generate the refresh token once and after that you can use it to gain access to Basecamp each time you run your script. If you already have a refresh token in your `.env` file, skip this step.

To begin the authentication process, use the `bcapi-auth` command:

```bash
bcapi-auth
```

Since your `.env` file does not contain a `BASECAMP_REFRESH_TOKEN`, an error will be raised which contains a link for the authorization of your app. Open that link in the browser and click on "Yes, I'll allow access".

After allowing access, you'll be redirected to your redirect URI where you'll find a verification code in the URL. Use this code to complete the authentication. Run the `bcapi-auth` command again with the verification code as an argument:

```bash
bcapi-auth 17beb4cd
```

This will generate your refresh token and use that token right away to generate the access token for your current session. You should now save the refresh token in your `.env` file as `BASECAMP_REFRESH_TOKEN`.

## Using the API

Once you have authentication set up, you can start interacting with Basecamp. Here are some examples:

### Working with Projects

```python
from bcapi.client import Client
from bcapi.projects import Projects

# Use the client as a context manager
with Client() as client:
    projects = Projects(client=client)
    
    # List all projects
    all_projects = projects.list()
    
    # Get a specific project
    project = projects.get(project_id=123456)
    
    # Create a new project
    new_project = projects.create(
        name="New Project",
        description="Project description"
    )
```

### Working with Messages

```python
from bcapi.client import Client
from bcapi.messages import Messages

with Client() as client:
    messages = Messages(client=client)
    
    # List messages in a message board
    message_list = messages.list(
        project_id=123456,
        message_board_id=789012
    )
    
    # Create a new message
    new_message = messages.create(
        project_id=123456,
        message_board_id=789012,
        subject="Important Update",
        content="<p>Here's the latest project update...</p>",
        status="active"  # Use "drafted" for draft
    )
    
    # Get a specific message
    message = messages.get(
        project_id=123456,
        message_id=789012
    )
    
    # Update a message
    updated_message = messages.update(
        project_id=123456,
        message_id=789012,
        subject="Updated: Important Update",
        content="<p>Here's the revised project update...</p>"
    )
    
    # Pin a message
    messages.pin(project_id=123456, message_id=789012)
    
    # Unpin a message
    messages.unpin(project_id=123456, message_id=789012)
```

### Working with Message Boards

```python
from bcapi.client import Client
from bcapi.message_boards import MessageBoards

with Client() as client:
    message_boards = MessageBoards(client=client)
    
    # Get message board details
    board = message_boards.get(
        project_id=123456,
        message_board_id=789012
    )
```

### Working with People

```python
from bcapi.client import Client
from bcapi.people import People

with Client() as client:
    people = People(client=client)
    
    # Get current user's profile
    profile = people.get_profile()
```

### Working with Card Tables (Kanban Boards)

```python
from bcapi.client import Client
from bcapi.card_tables import CardTables
from bcapi.card_table_columns import CardTableColumns
from bcapi.card_table_cards import CardTableCards
from bcapi.card_table_steps import CardTableSteps

with Client() as client:
    # Get a card table (Kanban board)
    card_tables = CardTables(client=client)
    board = card_tables.get(
        project_id=123456,
        card_table_id=789012
    )
    
    # Work with columns
    columns = CardTableColumns(client=client)
    
    # Get a column
    column = columns.get(project_id=123456, column_id=111111)
    
    # Create a new column
    new_column = columns.create(
        project_id=123456,
        card_table_id=789012,
        title="In Progress",
        description="Tasks we're actively working on"
    )
    
    # Update a column
    columns.update(
        project_id=123456,
        column_id=111111,
        title="Updated Title",
        description="New description"
    )
    
    # Set column color
    columns.set_color(
        project_id=123456,
        column_id=111111,
        color="orange"
    )
    
    # Subscribe/unsubscribe to column
    columns.subscribe(project_id=123456, column_id=111111)
    columns.unsubscribe(project_id=123456, column_id=111111)
    
    # Work with cards
    cards = CardTableCards(client=client)
    
    # List cards in a column
    card_list = cards.list(
        project_id=123456,
        column_id=111111
    )
    
    # Get a specific card
    card = cards.get(project_id=123456, card_id=222222)
    
    # Create a new card
    new_card = cards.create(
        project_id=123456,
        column_id=111111,
        title="Implement new feature",
        content="Detailed description of the feature",
        due_on="2024-12-31",
        notify=True
    )
    
    # Update a card
    cards.update(
        project_id=123456,
        card_id=222222,
        title="Updated feature name",
        assignee_ids=[12345, 67890]
    )
    
    # Move card to different column
    cards.move(
        project_id=123456,
        card_id=222222,
        column_id=333333
    )
    
    # Work with steps (sub-tasks within cards)
    steps = CardTableSteps(client=client)
    
    # Create a step
    new_step = steps.create(
        project_id=123456,
        card_id=222222,
        title="Research requirements",
        due_on="2024-12-15",
        assignees="12345,67890"  # Comma-separated IDs
    )
    
    # Update a step
    steps.update(
        project_id=123456,
        step_id=444444,
        title="Updated step title"
    )
    
    # Complete/uncomplete a step
    steps.complete(project_id=123456, step_id=444444)
    steps.uncomplete(project_id=123456, step_id=444444)
    
    # Reposition a step
    steps.reposition(
        project_id=123456,
        card_id=222222,
        source_id=444444,
        position=0  # Zero-indexed
    )
```

## Currently available endpoints

- **Card Tables** - Get Kanban board details
- **Card Table Columns** - Create, read, update, move columns; manage subscriptions, on-hold sections, and colors
- **Card Table Cards** - List, create, read, update, move cards within columns
- **Card Table Steps** - Create, update, complete, reposition steps/sub-tasks within cards
- **Messages** - Create, read, update, list, pin/unpin messages
- **MessageBoards** - Get message board details
- **People** - Get user profiles
- **Projects** - List, create, read, update, delete projects
- **Recordings** - Generic recording operations
- **Schedules** - Work with project schedules
- **Schedule Entries** - Manage schedule entries
- **TodoSets** - Access todo sets
- **TodoList Groups** - Manage todo list groups
- **TodoLists** - Work with todo lists
- **Todos** - Manage individual todos
- **Message Types** - Work with message categories

## Features

- **OAuth2 Authentication** - Automatic token refresh
- **Response Caching** - Built-in caching with ETag support
- **Pagination Handling** - Automatic pagination for list endpoints
- **Context Manager Support** - Clean resource management

## Error Handling

The client raises two main exception types:

- `AuthorizationRequiredError` - Raised when authentication is needed
- `BasecampAPIError` - Raised when API requests fail

```python
from bcapi.client import Client, AuthorizationRequiredError, BasecampAPIError

try:
    with Client() as client:
        # Your API calls here
        pass
except AuthorizationRequiredError as e:
    print(f"Authorization required: {e}")
except BasecampAPIError as e:
    print(f"API error: {e}")
```
