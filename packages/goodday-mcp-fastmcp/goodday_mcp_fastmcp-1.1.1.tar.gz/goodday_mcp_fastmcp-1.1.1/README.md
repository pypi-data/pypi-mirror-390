[![Add to Cursor](https://fastmcp.me/badges/cursor_dark.svg)](https://fastmcp.me/MCP/Details/1371/goodday)
[![Add to VS Code](https://fastmcp.me/badges/vscode_dark.svg)](https://fastmcp.me/MCP/Details/1371/goodday)
[![Add to Claude](https://fastmcp.me/badges/claude_dark.svg)](https://fastmcp.me/MCP/Details/1371/goodday)
[![Add to ChatGPT](https://fastmcp.me/badges/chatgpt_dark.svg)](https://fastmcp.me/MCP/Details/1371/goodday)
[![Add to Codex](https://fastmcp.me/badges/codex_dark.svg)](https://fastmcp.me/MCP/Details/1371/goodday)
[![Add to Gemini](https://fastmcp.me/badges/gemini_dark.svg)](https://fastmcp.me/MCP/Details/1371/goodday)

# Goodday MCP Server

A Model Context Protocol (MCP) server for integrating with Goodday project management platform. This server provides tools for managing projects, tasks, and users through the Goodday API v2.

## Features

### Project Management
- **get_projects**: Retrieve list of projects (with options for archived and root-only filtering)
- **get_project**: Get detailed information about a specific project
- **create_project**: Create new projects with customizable templates and settings
- **get_project_users**: Get users associated with a specific project

### Task Management
- **get_project_tasks**: Retrieve tasks from specific projects (with options for closed tasks and subfolders)
- **get_user_assigned_tasks**: Get tasks assigned to a specific user
- **get_user_action_required_tasks**: Get action-required tasks for a user
- **get_task**: Get detailed information about a specific task
- **get_task_details**: Get comprehensive task details including subtasks, custom fields, and full metadata
- **get_task_messages**: Retrieve all messages/comments for a specific task
- **create_task**: Create new tasks with full customization (subtasks, assignments, dates, priorities)
- **update_task_status**: Update task status with optional comments
- **add_task_comment**: Add comments to tasks

### Sprint Management
- **get_goodday_sprint_tasks**: Get tasks from specific sprints by project name and sprint name/number
- **get_goodday_sprint_summary**: Generate comprehensive sprint summaries with task details, status distribution, and key metrics

### User Management
- **get_users**: Retrieve list of organization users
- **get_user**: Get detailed information about a specific user

### Smart Query & Search
- **get_goodday_smart_query**: Natural language interface for common project management queries
- **search_goodday_tasks**: Semantic search across tasks using VectorDB backend
- **search_project_documents**: Search for documents within specific projects
- **get_document_content**: Retrieve full content of specific documents

## OpenWebUI Integration

This package also includes an OpenWebUI tool that provides a complete interface for Goodday project management directly in chat interfaces. The OpenWebUI tool includes:

### Features
- **Project Management**: Get projects, project tasks, and project details
- **Sprint Management**: Get tasks from specific sprints by name/number, comprehensive sprint summaries
- **User Management**: Get tasks assigned to specific users, user details
- **Task Details**: Get comprehensive task information including subtasks, custom fields, and metadata
- **Task Messages**: Retrieve all messages and comments for tasks
- **Smart Query**: Natural language interface for common project management requests
- **Semantic Search**: Search across tasks using VectorDB backend with embeddings
- **Document Management**: Search project documents and retrieve document content
- **Advanced Filtering**: Support for archived projects, closed tasks, subfolders, and more

### Setup
1. Copy `openwebui/goodday_openwebui_complete_tool.py` to your OpenWebUI tools directory
2. Configure the valves with your API credentials:
   - `api_key`: Your Goodday API token
   - `search_url`: Your VectorDB search endpoint (optional)
   - `bearer_token`: Bearer token for search API (optional)

### Vector Database Setup (Optional)
For semantic search functionality, you can set up a vector database using the provided n8n workflow (`openwebui/n8n-workflow-goodday-vectordb.json`). This workflow:
- Fetches all Goodday projects and tasks
- Extracts task messages and content
- Creates embeddings using Ollama
- Stores in Qdrant vector database
- Provides search API endpoint

See `openwebui/OPENWEBUI_TOOL_README.md` for detailed usage instructions.

## Installation

### From PyPI (Recommended)

```bash
pip install goodday-mcp
```

### From Source

#### Prerequisites
- Python 3.10 or higher
- UV package manager (recommended) or pip
- Goodday API token

#### Setup with UV

1. **Install UV** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and set up the project**:
   ```bash
   git clone https://github.com/cdmx1/goodday-mcp.git
   cd goodday-mcp
   
   # Create virtual environment and install dependencies
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync
   ```

#### Setup with pip

```bash
git clone https://github.com/cdmx1/goodday-mcp.git
cd goodday-mcp
pip install -e .
```

### Configuration

1. **Set up environment variables**:
   Create a `.env` file in your project root or export the variable:
   ```bash
   export GOODDAY_API_TOKEN=your_goodday_api_token_here
   ```

   To get your Goodday API token:
   - Go to your Goodday organization
   - Navigate to Settings → API
   - Click the generate button to create a new token

## Usage

### Running the Server Standalone

If installed from PyPI:
```bash
goodday-mcp
```

If running from source with UV:
```bash
uv run goodday-mcp
```

### Using with Claude Desktop

1. **Configure Claude Desktop** by editing your configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add the server configuration**:

   **Option A: If installed from PyPI:**
   ```json
   {
     "mcpServers": {
       "goodday": {
         "command": "goodday-mcp",
         "env": {
           "GOODDAY_API_TOKEN": "your_goodday_api_token_here"
         }
       }
     }
   }
   ```

   **Option B: If running from source:**
   ```json
   {
     "mcpServers": {
       "goodday": {
         "command": "uv",
         "args": ["run", "goodday-mcp"],
         "env": {
           "GOODDAY_API_TOKEN": "your_goodday_api_token_here"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop** to load the new server.

### Using with Other MCP Clients

The server communicates via stdio transport and can be integrated with any MCP-compatible client. Refer to the [MCP documentation](https://modelcontextprotocol.io/) for client-specific integration instructions.

## API Reference

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOODDAY_API_TOKEN` | Your Goodday API token | Yes |

### Tool Examples

#### Get Projects
```python
# Get all active projects
get_projects()

# Get archived projects
get_projects(archived=True)

# Get only root-level projects
get_projects(root_only=True)
```

#### Create a Task
```python
create_task(
    project_id="project_123",
    title="Implement new feature",
    from_user_id="user_456",
    message="Detailed description of the task",
    to_user_id="user_789",
    deadline="2025-06-30",
    priority=5
)
```

#### Update Task Status
```python
update_task_status(
    task_id="task_123",
    user_id="user_456",
    status_id="status_completed",
    message="Task completed successfully"
)
```

## Data Formats

### Date Format
All dates should be provided in `YYYY-MM-DD` format (e.g., `2025-06-16`).

### Priority Levels
- 1-10: Normal priority levels
- 50: Blocker
- 100: Emergency

### Project Colors
Project colors are specified as integers from 1-24, corresponding to Goodday's color palette.

## Error Handling

The server includes comprehensive error handling:
- **Authentication errors**: When API token is missing or invalid
- **Network errors**: When Goodday API is unreachable
- **Validation errors**: When required parameters are missing
- **Permission errors**: When user lacks permissions for requested operations

All errors are returned as descriptive strings to help with troubleshooting.

## Development

### Project Structure
```
goodday-mcp/
├── goodday_mcp/         # Main package directory
│   ├── __init__.py      # Package initialization
│   └── main.py          # Main MCP server implementation
├── pyproject.toml       # Project configuration and dependencies
├── README.md           # This file
├── LICENSE             # MIT license
├── uv.lock            # Dependency lock file
└── .env               # Environment variables (create this)
```

### Adding New Tools

To add new tools to the server:

1. **Add the tool function** in `goodday_mcp/main.py` using the `@mcp.tool()` decorator:
   ```python
   @mcp.tool()
   async def your_new_tool(param1: str, param2: Optional[int] = None) -> str:
       """Description of what the tool does.
       
       Args:
           param1: Description of parameter 1
           param2: Description of optional parameter 2
       """
       # Implementation here
       return "Result"
   ```

2. **Test the tool** by running the server and testing with an MCP client.

### Testing

Test the server by running it directly:
```bash
# If installed from PyPI
goodday-mcp

# If running from source
uv run goodday-mcp
```

The server will start and wait for MCP protocol messages via stdin/stdout.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues related to:
- **MCP Server**: Create an issue in this repository
- **Goodday API**: Refer to [Goodday API documentation](https://www.goodday.work/developers/api-v2)
- **MCP Protocol**: Refer to [MCP documentation](https://modelcontextprotocol.io/)

## Changelog

### v1.1.0 (Current)
- **Enhanced Task Management**: Added `get_task_details` and `get_task_messages` for comprehensive task information
- **Sprint Management**: Added `get_goodday_sprint_tasks` and `get_goodday_sprint_summary` for sprint tracking
- **Smart Query Interface**: Added `get_goodday_smart_query` for natural language project queries
- **Semantic Search**: Added `search_goodday_tasks` with VectorDB integration for intelligent task search
- **Document Management**: Added `search_project_documents` and `get_document_content` for document handling
- **Improved Error Handling**: Enhanced error messages and status reporting
- **Advanced Filtering**: Support for archived projects, closed tasks, and subfolder inclusion

### v1.0.0
- Initial release
- Full project management capabilities
- Task management with comments and status updates
- User management
- Comprehensive error handling
- UV support with modern Python packaging