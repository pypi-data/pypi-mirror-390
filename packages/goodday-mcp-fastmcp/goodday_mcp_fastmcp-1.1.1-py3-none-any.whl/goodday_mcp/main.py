from typing import Any, Optional, List
import httpx
import os
import re
from datetime import datetime, timezone, timedelta
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("goodday-mcp")

# Constants
GOODDAY_API_BASE = "https://api.goodday.work/2.0"
USER_AGENT = "goodday-mcp/1.1.0"

async def make_goodday_request(endpoint: str, method: str = "GET", data: dict = None, subfolders: bool = True) -> dict[str, Any] | list[Any] | None:
    """Make a request to the Goodday API with proper error handling."""
    api_token = os.getenv("GOODDAY_API_TOKEN")
    if not api_token:
        raise ValueError("GOODDAY_API_TOKEN environment variable is required")
    
    headers = {
        "User-Agent": USER_AGENT,
        "gd-api-token": api_token,
        "Content-Type": "application/json"
    }
    
    # Automatically add subfolders=true for project task and document endpoints if not already present
    if subfolders and endpoint.startswith("project/") and ("/tasks" in endpoint or "/documents" in endpoint):
        if "?" in endpoint:
            if "subfolders=" not in endpoint:
                endpoint += "&subfolders=true"
        else:
            endpoint += "?subfolders=true"
    
    url = f"{GOODDAY_API_BASE}/{endpoint.lstrip('/')}"
    
    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "POST":
                response = await client.post(url, headers=headers, json=data, timeout=30.0)
            elif method.upper() == "PUT":
                response = await client.put(url, headers=headers, json=data, timeout=30.0)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=headers, timeout=30.0)
            else:
                response = await client.get(url, headers=headers, timeout=30.0)

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise Exception(f"Request error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")

async def make_search_request(method: str = "GET", params: dict = None) -> dict:
    """Make a request to the search API with bearer token authentication."""
    search_url = os.getenv("GOODDAY_SEARCH_URL", "")
    bearer_token = os.getenv("GOODDAY_SEARCH_BEARER_TOKEN", "")
    
    if not bearer_token:
        raise ValueError("GOODDAY_SEARCH_BEARER_TOKEN environment variable is required for search API")
    
    if not search_url:
        raise ValueError("GOODDAY_SEARCH_URL environment variable is required for search API")
    
    headers = {
        "User-Agent": USER_AGENT,
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    
    url = str(search_url).strip()
    
    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
            else:
                response = await client.request(method.upper(), url, headers=headers, params=params, timeout=30.0)
            
            response.raise_for_status()
            return response.json()
        
        except httpx.HTTPStatusError as e:
            raise Exception(f"Search API HTTP error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise Exception(f"Search API request error: {str(e)}")
        except Exception as e:
            raise Exception(f"Search API unexpected error: {str(e)}")

def format_task(task: dict) -> str:
    """Format a task into a readable string with safe checks."""
    if not isinstance(task, dict):
        return f"Invalid task data: {repr(task)}"

    # Defensive defaults in case nested keys are not dicts
    status = task.get('status') if isinstance(task.get('status'), dict) else {}
    project = task.get('project') if isinstance(task.get('project'), dict) else {}

    return f"""
**Task ID:** {task.get('shortId', 'N/A')}
**Title:** {task.get('name', 'N/A')}
**Status:** {status.get('name', 'N/A')}
**Project:** {project.get('name', 'N/A')}
**Assigned To:** {task.get('assignedToUserId', 'N/A')}
**Priority:** {task.get('priority', 'N/A')}
**Start Date:** {task.get('startDate', 'N/A')}
**End Date:** {task.get('endDate', 'N/A')}
**Description:** {task.get('message', 'No description')}
""".strip()

def format_project(project: dict) -> str:
    """Format a project into a readable string with safe checks."""
    if not isinstance(project, dict):
        return f"Invalid project data: {repr(project)}"

    # Defensive defaults in case nested keys are not dicts
    status = project.get('status') if isinstance(project.get('status'), dict) else {}
    owner = project.get('owner') if isinstance(project.get('owner'), dict) else {}

    return f"""
Project ID: {project.get('id', 'N/A')}
Name: {project.get('name', 'N/A')}
Health: {project.get('health', 'N/A')}
Status: {status.get('name', 'N/A')}
Start Date: {project.get('startDate', 'N/A')}
End Date: {project.get('endDate', 'N/A')}
Progress: {project.get('progress', 0)}%
Owner: {owner.get('name', 'N/A')}
""".strip()

def format_user(user: dict) -> str:
    """Format a user into a readable string with safe checks."""
    if not isinstance(user, dict):
        return f"Invalid user data: {repr(user)}"

    # Defensive defaults in case nested keys are not dicts
    role = user.get('role') if isinstance(user.get('role'), dict) else {}

    return f"""
User ID: {user.get('id', 'N/A')}
Name: {user.get('name', 'N/A')}
Email: {user.get('email', 'N/A')}
Role: {role.get('name', 'N/A')}
Status: {user.get('status', 'N/A')}
""".strip()

def format_timestamp_ist(timestamp_str: str) -> str:
    """Format timestamp to IST timezone."""
    if not timestamp_str or timestamp_str == 'N/A':
        return 'N/A'
    try:
        # Parse the timestamp (assuming it's in ISO format)
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        # Convert to IST (UTC+5:30)
        ist_offset = timedelta(hours=5, minutes=30)
        ist_time = dt + ist_offset
        return ist_time.strftime('%Y-%m-%d %H:%M:%S IST')
    except Exception:
        return timestamp_str

async def get_user_mapping() -> dict:
    """Get mapping of user IDs to names."""
    data = await make_goodday_request("users")
    user_id_to_name = {}
    if isinstance(data, list):
        for u in data:
            if isinstance(u, dict):
                user_id_to_name[u.get("id")] = u.get("name", "Unknown")
    return user_id_to_name

async def get_project_mapping() -> dict:
    """Get mapping of project IDs to names."""
    data = await make_goodday_request("projects")
    project_id_to_name = {}
    if isinstance(data, list):
        for p in data:
            if isinstance(p, dict):
                project_id_to_name[p.get("id")] = p.get("name", "Unknown")
    return project_id_to_name

async def find_project_by_name(project_name: str) -> tuple[Optional[dict], List[str]]:
    """Find project by name (case-insensitive)."""
    projects_data = await make_goodday_request("projects")
    if not projects_data or not isinstance(projects_data, list):
        return None, []
    
    # Filter out system projects (like sprints) to avoid overwhelming the AI
    filtered_projects = [
        proj for proj in projects_data 
        if isinstance(proj, dict) and proj.get("systemType") != "PROJECT"
    ]
    
    project_name_lower = project_name.lower().strip()
    matched_project = None
    for proj in filtered_projects:
        if not isinstance(proj, dict):
            continue
        current_project_name = proj.get("name", "").lower().strip()
        if current_project_name == project_name_lower:
            matched_project = proj
            break
        if (
            project_name_lower in current_project_name
            or current_project_name in project_name_lower
        ):
            matched_project = proj
            break
    
    available_projects = [
        p.get("name", "Unknown")
        for p in projects_data
        if isinstance(p, dict)
    ]
    return matched_project, available_projects

async def find_sprint_by_name(parent_project_id: str, sprint_name: str) -> tuple[Optional[dict], List[str]]:
    """Find sprint project by name within a parent project."""
    projects_data = await make_goodday_request("projects")
    if not projects_data or not isinstance(projects_data, list):
        return None, []
    
    normalized_sprint_name = sprint_name.lower().strip()
    if not normalized_sprint_name.startswith("sprint"):
        normalized_sprint_name = f"sprint {normalized_sprint_name}"

    available_sprints = []
    search_number = re.search(r"(\d+)", normalized_sprint_name)
    exact_match = None
    substring_match = None

    for proj in projects_data:
        if isinstance(proj, dict) and proj.get("systemType") == "PROJECT":
            sprint_proj_name = proj.get("name", "").lower().strip()
            if sprint_proj_name.startswith("sprint"):
                available_sprints.append(proj.get("name", ""))
                project_number = re.search(r"(\d+)", sprint_proj_name)
                # Prefer exact number match
                if (
                    search_number
                    and project_number
                    and search_number.group(1) == project_number.group(1)
                ):
                    exact_match = proj
                # Fallback: search number as substring anywhere in the sprint name
                elif (
                    search_number and search_number.group(1) in sprint_proj_name
                ):
                    if not substring_match:
                        substring_match = proj
                elif normalized_sprint_name == sprint_proj_name:
                    if not exact_match:
                        exact_match = proj
                elif (
                    normalized_sprint_name in sprint_proj_name
                    or sprint_proj_name in normalized_sprint_name
                ):
                    if not substring_match:
                        substring_match = proj

    if exact_match:
        return exact_match, available_sprints
    if substring_match:
        return substring_match, available_sprints
    return None, available_sprints

async def find_user_by_name_or_email(user_identifier: str) -> Optional[dict]:
    """Find user by name or email (case-insensitive)."""
    users_data = await make_goodday_request("users")
    if not users_data or not isinstance(users_data, list):
        return None
    
    user_identifier_lower = user_identifier.lower().strip()
    for user in users_data:
        if isinstance(user, dict):
            user_name = user.get("name", "").lower().strip()
            user_email = user.get("email", "").lower().strip()
            if user_identifier_lower in user_name or user_identifier_lower in user_email:
                return user
    return None

# Project Management Tools
@mcp.tool()
async def get_projects(archived: bool = False, root_only: bool = False) -> str:
    """Get list of projects from Goodday.

    Args:
        archived: Set to true to retrieve archived/closed projects
        root_only: Set to true to return only root projects
    """
    params = []
    if archived:
        params.append("archived=true")
    if root_only:
        params.append("rootOnly=true")
    
    endpoint = "projects"
    if params:
        endpoint += "?" + "&".join(params)
    
    data = await make_goodday_request(endpoint)
    
    if not data:
        return "No projects found."
        
    if isinstance(data, dict):
        if "error" in data:
            return f"Unable to fetch projects: {data.get('error', 'Unknown error')}"
    elif isinstance(data, str):
        return f"Unexpected string response from API: {data}"
    elif not isinstance(data, list):
        return f"Unexpected response format: {type(data).__name__} - {str(data)}"
    
    projects = [format_project(project) for project in data]
    return "\n---\n".join(projects)

@mcp.tool()
async def get_project(project_id: str) -> str:
    """Get details of a specific project.

    Args:
        project_id: The ID of the project to retrieve
    """
    data = await make_goodday_request(f"project/{project_id}")
    
    if not data:
        return "Project not found."
    
    if isinstance(data, dict) and "error" in data:
        return f"Unable to fetch project: {data.get('error', 'Unknown error')}"
    
    return format_project(data)

@mcp.tool()
async def create_project(
    name: str,
    created_by_user_id: str,
    project_template_id: str,
    parent_project_id: Optional[str] = None,
    color: Optional[int] = None,
    project_owner_user_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    deadline: Optional[str] = None
) -> str:
    """Create a new project in Goodday.

    Args:
        name: Project name
        created_by_user_id: ID of user creating the project
        project_template_id: Project template ID (found in Organization settings → Project templates)
        parent_project_id: Parent project ID to create a sub project
        color: Project color (1-24)
        project_owner_user_id: Project owner user ID
        start_date: Project start date (YYYY-MM-DD)
        end_date: Project end date (YYYY-MM-DD)
        deadline: Project deadline (YYYY-MM-DD)
    """
    data = {
        "name": name,
        "createdByUserId": created_by_user_id,
        "projectTemplateId": project_template_id
    }
    
    if parent_project_id:
        data["parentProjectId"] = parent_project_id
    if color:
        data["color"] = color
    if project_owner_user_id:
        data["projectOwnerUserId"] = project_owner_user_id
    if start_date:
        data["startDate"] = start_date
    if end_date:
        data["endDate"] = end_date
    if deadline:
        data["deadline"] = deadline
    
    result = await make_goodday_request("projects/new-project", "POST", data)
    
    if not result:
        return "Unable to create project: No response received"
    
    if isinstance(result, dict) and "error" in result:
        return f"Unable to create project: {result.get('error', 'Unknown error')}"
    
    return f"Project created successfully: {format_project(result)}"

# Task Management Tools
@mcp.tool()
async def get_project_tasks(project_id: str, closed: bool = False, subfolders: bool = False) -> str:
    """Get tasks from a specific project.

    Args:
        project_id: The ID of the project
        closed: Set to true to retrieve all open and closed tasks
        subfolders: Set to true to return tasks from project subfolders
    """
    params = []
    if closed:
        params.append("closed=true")
    if subfolders:
        params.append("subfolders=true")
    
    endpoint = f"project/{project_id}/tasks"
    if params:
        endpoint += "?" + "&".join(params)
    
    data = await make_goodday_request(endpoint)
    
    if not data:
        return "No tasks found."
    
    if isinstance(data, dict) and "error" in data:
        return f"Unable to fetch tasks: {data.get('error', 'Unknown error')}"
    
    if not isinstance(data, list):
        return f"Unexpected response format: {str(data)}"
    
    tasks = [format_task(task) for task in data]
    return "\n---\n".join(tasks)

@mcp.tool()
async def get_user_assigned_tasks(user_id: str, closed: bool = False) -> str:
    """Get tasks assigned to a specific user.

    Args:
        user_id: The ID of the user
        closed: Set to true to retrieve all open and closed tasks
    """
    params = []
    if closed:
        params.append("closed=true")
    
    endpoint = f"user/{user_id}/assigned-tasks"
    if params:
        endpoint += "?" + "&".join(params)
    
    data = await make_goodday_request(endpoint)
    
    if not data:
        return "No assigned tasks found."
    
    if isinstance(data, dict) and "error" in data:
        return f"Unable to fetch assigned tasks: {data.get('error', 'Unknown error')}"
    
    if not isinstance(data, list):
        return f"Unexpected response format: {str(data)}"
    
    tasks = [format_task(task) for task in data]
    return "\n---\n".join(tasks)

@mcp.tool()
async def get_user_action_required_tasks(user_id: str) -> str:
    """Get action required tasks for a specific user.

    Args:
        user_id: The ID of the user
    """
    data = await make_goodday_request(f"user/{user_id}/action-required-tasks")
    
    if not data:
        return "No action required tasks found."
    
    if isinstance(data, dict) and "error" in data:
        return f"Unable to fetch action required tasks: {data.get('error', 'Unknown error')}"
    
    if not isinstance(data, list):
        return f"Unexpected response format: {str(data)}"
    
    tasks = [format_task(task) for task in data]
    return "\n---\n".join(tasks)

@mcp.tool()
async def get_task(task_id: str) -> str:
    """Get details of a specific task.

    Args:
        task_id: The ID of the task to retrieve
    """
    data = await make_goodday_request(f"task/{task_id}")
    
    if not data:
        return "Task not found."
    
    if isinstance(data, dict) and "error" in data:
        return f"Unable to fetch task: {data.get('error', 'Unknown error')}"
    
    return format_task(data)

@mcp.tool()
async def create_task(
    project_id: str,
    title: str,
    from_user_id: str,
    parent_task_id: Optional[str] = None,
    message: Optional[str] = None,
    to_user_id: Optional[str] = None,
    task_type_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    deadline: Optional[str] = None,
    estimate: Optional[int] = None,
    story_points: Optional[int] = None,
    priority: Optional[int] = None
) -> str:
    """Create a new task in Goodday.

    Args:
        project_id: Task project ID
        title: Task title
        from_user_id: Task created by user ID  
        parent_task_id: Parent task ID to create a subtask
        message: Task description/initial message
        to_user_id: Assigned To/Action required user ID
        task_type_id: Task type ID
        start_date: Task start date (YYYY-MM-DD)
        end_date: Task end date (YYYY-MM-DD)
        deadline: Task deadline (YYYY-MM-DD)
        estimate: Task estimate in minutes
        story_points: Task story points estimate
        priority: Task priority (1-10), 50 - Blocker, 100 - Emergency
    """
    data = {
        "projectId": project_id,
        "title": title,
        "fromUserId": from_user_id
    }
    
    if parent_task_id:
        data["parentTaskId"] = parent_task_id
    if message:
        data["message"] = message
    if to_user_id:
        data["toUserId"] = to_user_id
    if task_type_id:
        data["taskTypeId"] = task_type_id
    if start_date:
        data["startDate"] = start_date
    if end_date:
        data["endDate"] = end_date
    if deadline:
        data["deadline"] = deadline
    if estimate:
        data["estimate"] = estimate
    if story_points:
        data["storyPoints"] = story_points
    if priority:
        data["priority"] = priority
    
    result = await make_goodday_request("tasks", "POST", data)
    
    if not result:
        return "Unable to create task: No response received"
    
    if isinstance(result, dict) and "error" in result:
        return f"Unable to create task: {result.get('error', 'Unknown error')}"
    
    return f"Task created successfully: {format_task(result)}"

@mcp.tool()
async def update_task_status(task_id: str, user_id: str, status_id: str, message: Optional[str] = None) -> str:
    """Update the status of a task.

    Args:
        task_id: The ID of the task to update
        user_id: User on behalf of whom API will execute update
        status_id: New status ID
        message: Optional comment
    """
    data = {
        "userId": user_id,
        "statusId": status_id
    }
    
    if message:
        data["message"] = message
    
    result = await make_goodday_request(f"task/{task_id}/status", "PUT", data)
    
    if not result:
        return "Unable to update task status: No response received"
    
    if isinstance(result, dict) and "error" in result:
        return f"Unable to update task status: {result.get('error', 'Unknown error')}"
    
    return "Task status updated successfully"

@mcp.tool()
async def add_task_comment(task_id: str, user_id: str, message: str) -> str:
    """Add a comment to a task.

    Args:
        task_id: The ID of the task
        user_id: User on behalf of whom API will execute update
        message: Comment text
    """
    data = {
        "userId": user_id,
        "message": message
    }
    
    result = await make_goodday_request(f"task/{task_id}/comment", "POST", data)
    
    if not result:
        return "Unable to add comment: No response received"
    
    if isinstance(result, dict) and "error" in result:
        return f"Unable to add comment: {result.get('error', 'Unknown error')}"
    
    return "Comment added successfully"

# User Management Tools
@mcp.tool()
async def get_users() -> str:
    """Get list of organization users."""
    data = await make_goodday_request("users")
    
    if not data:
        return "No users found."
    
    if isinstance(data, dict) and "error" in data:
        return f"Unable to fetch users: {data.get('error', 'Unknown error')}"
    
    if not isinstance(data, list):
        return f"Unexpected response format: {str(data)}"
    
    users = [format_user(user) for user in data]
    return "\n---\n".join(users)

@mcp.tool()
async def get_user(user_id: str) -> str:
    """Get details of a specific user.

    Args:
        user_id: The ID of the user to retrieve
    """
    data = await make_goodday_request(f"user/{user_id}")
    
    if not data:
        return "User not found."
    
    if isinstance(data, dict) and "error" in data:
        return f"Unable to fetch user: {data.get('error', 'Unknown error')}"
    
    return format_user(data)

@mcp.tool()
async def get_project_users(project_id: str) -> str:
    """Get users associated with a specific project.

    Args:
        project_id: The ID of the project
    """
    data = await make_goodday_request(f"project/{project_id}/users")
    
    if not data:
        return "No users found for this project."
    
    if isinstance(data, dict) and "error" in data:
        return f"Unable to fetch project users: {data.get('error', 'Unknown error')}"
    
    if not isinstance(data, list):
        return f"Unexpected response format: {str(data)}"
    
    users = [format_user(user) for user in data]
    return "\n---\n".join(users)

# Enhanced Task Management Tools
@mcp.tool()
async def get_task_details(task_short_id: str, project_name: str) -> str:
    """Get comprehensive task details including subtasks, custom fields, and full metadata.

    Args:
        task_short_id: The short ID of the task (e.g., RAD-434)
        project_name: The name of the project containing the task (required, case-insensitive)
    """
    # Find the project
    matched_project, available_projects = await find_project_by_name(project_name)
    if not matched_project:
        return f"Project '{project_name}' not found. Available projects: {', '.join(available_projects[:10])}{'...' if len(available_projects) > 10 else ''}"
    
    project_id = matched_project.get("id")
    found_in_project = matched_project.get("name")

    # Find the task
    tasks_data = await make_goodday_request(f"project/{project_id}/tasks")
    if not tasks_data or not isinstance(tasks_data, list):
        return f"Unable to fetch tasks for project '{found_in_project}'."
    
    task_id = None
    task_data = None
    for task in tasks_data:
        if isinstance(task, dict) and task.get("shortId") == task_short_id:
            task_id = task.get("id")
            task_data = task
            break
    
    if not task_id or not task_data:
        return f"Task with short ID '{task_short_id}' not found in project '{found_in_project}'."

    # Get detailed task information
    detailed_data = await make_goodday_request(f"task/{task_id}")
    if not detailed_data:
        return f"No details found for task '{task_short_id}'."
    
    if isinstance(detailed_data, dict) and "error" in detailed_data:
        return f"Unable to fetch task details: {detailed_data.get('error', 'Unknown error')}"

    # Get task messages for description
    messages_data = await make_goodday_request(f"task/{task_id}/messages")
    first_message = "No description"
    if messages_data and isinstance(messages_data, list) and len(messages_data) > 0:
        first_msg = messages_data[0]
        if isinstance(first_msg, dict):
            first_message = first_msg.get("message", "No description")

    # Get user mapping
    user_id_to_name = await get_user_mapping()
    
    def user_display(user_id):
        if not user_id:
            return "N/A"
        name = user_id_to_name.get(user_id)
        return f"{name} ({user_id})" if name else user_id

    # Format comprehensive details
    status = detailed_data.get("status", {}) if isinstance(detailed_data.get("status"), dict) else {}
    task_type = detailed_data.get("taskType", {}) if isinstance(detailed_data.get("taskType"), dict) else {}
    custom_fields = detailed_data.get("customFieldsData", {}) if isinstance(detailed_data.get("customFieldsData"), dict) else {}
    subtasks = detailed_data.get("subtasks", []) if isinstance(detailed_data.get("subtasks"), list) else []
    users = detailed_data.get("users", []) if isinstance(detailed_data.get("users"), list) else []

    formatted_details = f"""
**Task ID:** {detailed_data.get('shortId', 'N/A')}
**Name:** {detailed_data.get('name', 'N/A')}
**Project:** {found_in_project}
**Status:** {status.get('name', 'N/A')}
**Task Type:** {task_type.get('name', 'N/A')}
**Priority:** {detailed_data.get('priority', 'N/A')}
**Assigned To:** {user_display(detailed_data.get('assignedToUserId'))}
**Action Required:** {user_display(detailed_data.get('actionRequiredUserId'))}
**Created By:** {user_display(detailed_data.get('createdByUserId'))}
**Start Date:** {detailed_data.get('startDate', 'N/A')}
**End Date:** {detailed_data.get('endDate', 'N/A')}
**Deadline:** {detailed_data.get('deadline', 'N/A')}
**Estimate:** {detailed_data.get('estimate', 'N/A')}
**Reported Time:** {detailed_data.get('reportedTime', 'N/A')}
**Users:** {', '.join([user_display(uid) for uid in users]) if users else 'N/A'}
**Subtasks Count:** {len(subtasks)}
**Description:** {first_message}
""".strip()

    # Add custom fields if they exist
    if custom_fields:
        formatted_details += "\n\n**Custom Fields:**"
        for field_id, field_value in custom_fields.items():
            formatted_details += f"\n- {field_id}: {field_value}"

    # Add subtasks if they exist
    if subtasks:
        formatted_details += f"\n\n**Subtasks ({len(subtasks)}):**"
        for i, subtask in enumerate(subtasks[:10]):
            if isinstance(subtask, dict):
                formatted_details += f"\n- {subtask.get('shortId', 'N/A')}: {subtask.get('name', 'N/A')}"
        if len(subtasks) > 10:
            formatted_details += f"\n... and {len(subtasks) - 10} more subtasks"

    return f"**Task Details for '{task_short_id}' in project '{found_in_project}':**\n\n{formatted_details}"

@mcp.tool()
async def get_task_messages(task_short_id: str, project_name: Optional[str] = None) -> str:
    """Retrieve all messages/comments for a specific task.

    Args:
        task_short_id: The short ID of the task (e.g., RAD-434)
        project_name: Optional project name for disambiguation
    """
    task_id = None
    found_in_project = None
    
    # If project name is provided, use it to find the project
    if project_name:
        matched_project, available_projects = await find_project_by_name(project_name)
        if not matched_project:
            return f"Project '{project_name}' not found. Available projects: {', '.join(available_projects[:10])}{'...' if len(available_projects) > 10 else ''}"
        project_id = matched_project.get("id")
        found_in_project = matched_project.get("name")
        
        # Find the task in the specified project
        tasks_data = await make_goodday_request(f"project/{project_id}/tasks")
        if isinstance(tasks_data, list):
            for task in tasks_data:
                if isinstance(task, dict) and task.get("shortId") == task_short_id:
                    task_id = task.get("id")
                    break
        
        if not task_id:
            return f"Task with short ID '{task_short_id}' not found in project '{found_in_project}'."
    else:
        # Search across all projects
        projects_data = await make_goodday_request("projects")
        if not projects_data or not isinstance(projects_data, list):
            return "Unable to fetch projects."
        
        for proj in projects_data:
            if isinstance(proj, dict):
                proj_id = proj.get("id")
                tasks_data = await make_goodday_request(f"project/{proj_id}/tasks")
                if isinstance(tasks_data, list):
                    for task in tasks_data:
                        if isinstance(task, dict) and task.get("shortId") == task_short_id:
                            task_id = task.get("id")
                            found_in_project = proj.get("name")
                            break
            if task_id:
                break
        
        if not task_id:
            return f"Task with short ID '{task_short_id}' not found in any project."

    # Get task messages
    messages_data = await make_goodday_request(f"task/{task_id}/messages")
    if not messages_data:
        return f"No messages found for task '{task_short_id}'."
    
    if isinstance(messages_data, dict) and "error" in messages_data:
        return f"Unable to fetch messages: {messages_data.get('error', 'Unknown error')}"
    
    if not isinstance(messages_data, list):
        return f"Unexpected response format: {str(messages_data)}"

    # Get user mapping
    user_id_to_name = await get_user_mapping()
    
    def user_display(user_id):
        if not user_id:
            return "N/A"
        name = user_id_to_name.get(user_id)
        return f"{name} ({user_id})" if name else user_id

    # Format messages
    formatted_messages = []
    for msg in messages_data:
        if not isinstance(msg, dict):
            continue

        formatted_msg = f"""
**Message ID:** {msg.get('id', 'N/A')}
**Date Created:** {format_timestamp_ist(msg.get('dateCreated', 'N/A'))}
**From User:** {user_display(msg.get('fromUserId'))}
**To User:** {user_display(msg.get('toUserId'))}
**Message:** {msg.get('message', 'No message content')}
**Task Status ID:** {msg.get('taskStatusId', 'N/A')}
""".strip()
        formatted_messages.append(formatted_msg)

    result = "\n---\n".join(formatted_messages)
    return f"**Messages for Task '{task_short_id}' in project '{found_in_project}' - {len(messages_data)} messages:**\n\n{result}"

# Sprint Management Tools
@mcp.tool()
async def get_goodday_sprint_tasks(project_name: str, sprint_name: str, include_closed: bool = True) -> str:
    """Get tasks from a specific sprint by project name and sprint name/number.

    Args:
        project_name: The name of the main project (e.g., "ASTRA")
        sprint_name: The name or number of the sprint (e.g., "Sprint 233", "233")
        include_closed: Whether to include closed tasks (default: True)
    """
    # Find main project
    matched_project, available_projects = await find_project_by_name(project_name)
    if not matched_project:
        return f"Project '{project_name}' not found. Available projects: {', '.join(available_projects[:10])}{'...' if len(available_projects) > 10 else ''}"

    main_project_id = matched_project.get("id")
    actual_project_name = matched_project.get("name")

    # Find sprint project
    sprint_project, available_sprints = await find_sprint_by_name(main_project_id, sprint_name)
    if not sprint_project:
        if available_sprints:
            return f"Sprint '{sprint_name}' not found. Available sprints: {', '.join(available_sprints)}"
        else:
            return f"No sprints found under project '{actual_project_name}'."

    sprint_id = sprint_project.get("id")
    actual_sprint_name = sprint_project.get("name")

    # Get tasks from sprint
    params = []
    if include_closed:
        params.append("closed=true")
    endpoint = f"project/{sprint_id}/tasks"
    if params:
        endpoint += "?" + "&".join(params)

    tasks_data = await make_goodday_request(endpoint)
    if not tasks_data:
        return f"No tasks found in sprint '{actual_sprint_name}'."
    
    if isinstance(tasks_data, dict) and "error" in tasks_data:
        return f"Unable to fetch sprint tasks: {tasks_data.get('error', 'Unknown error')}"
    
    if not isinstance(tasks_data, list):
        return f"Unexpected response format: {str(tasks_data)}"

    # Get user mapping
    user_id_to_name = await get_user_mapping()
    
    def user_display(user_id):
        if not user_id:
            return "Unassigned"
        name = user_id_to_name.get(user_id)
        return name if name else f"User {user_id}"

    # Format tasks
    formatted_tasks = []
    for task in tasks_data:
        if not isinstance(task, dict):
            continue

        status = task.get("status", {}) if isinstance(task.get("status"), dict) else {}
        status_name = status.get("name", "Unknown Status")
        assigned_user_id = task.get("assignedToUserId")
        assigned_user = user_display(assigned_user_id)

        formatted_task = f"""
**{task.get('shortId', 'N/A')}**: {task.get('name', 'No title')}
- **Status**: {status_name}
- **Assigned To**: {assigned_user}
- **Priority**: {task.get('priority', 'N/A')}
""".strip()
        formatted_tasks.append(formatted_task)

    result = "\n---\n".join(formatted_tasks)
    return f"**Tasks in Sprint '{actual_sprint_name}' (Project: '{actual_project_name}') - {len(tasks_data)} tasks:**\n\n{result}"

@mcp.tool()
async def get_goodday_sprint_summary(project_name: str, sprint_name: str) -> str:
    """Generate a comprehensive sprint summary with task details, status distribution, and key metrics.

    Args:
        project_name: The name of the main project (e.g., "ASTRA")
        sprint_name: The name or number of the sprint (e.g., "Sprint 233", "233")
    """
    # Find main project
    matched_project, available_projects = await find_project_by_name(project_name)
    if not matched_project:
        return f"Project '{project_name}' not found. Available projects: {', '.join(available_projects[:10])}{'...' if len(available_projects) > 10 else ''}"

    main_project_id = matched_project.get("id")
    actual_project_name = matched_project.get("name")

    # Find sprint project
    sprint_project, available_sprints = await find_sprint_by_name(main_project_id, sprint_name)
    if not sprint_project:
        if available_sprints:
            return f"Sprint '{sprint_name}' not found. Available sprints: {', '.join(available_sprints)}"
        else:
            return f"No sprints found under project '{actual_project_name}'."

    sprint_id = sprint_project.get("id")
    actual_sprint_name = sprint_project.get("name")

    # Get all tasks with closed tasks included
    endpoint = f"project/{sprint_id}/tasks?closed=true"
    tasks_data = await make_goodday_request(endpoint)
    if not tasks_data:
        return f"No tasks found in sprint '{actual_sprint_name}'."
    
    if isinstance(tasks_data, dict) and "error" in tasks_data:
        return f"Unable to fetch sprint tasks: {tasks_data.get('error', 'Unknown error')}"
    
    if not isinstance(tasks_data, list):
        return f"Unexpected response format: {str(tasks_data)}"

    # Get user mapping
    user_id_to_name = await get_user_mapping()
    
    def user_display(user_id):
        if not user_id:
            return "Unassigned"
        name = user_id_to_name.get(user_id)
        return name if name else f"User {user_id}"

    # Analyze tasks
    status_counts = {}
    user_task_counts = {}
    task_summaries = []

    for task in tasks_data:
        if not isinstance(task, dict):
            continue

        task_short_id = task.get("shortId", "N/A")
        task_name = task.get("name", "No title")
        status = task.get("status", {}) if isinstance(task.get("status"), dict) else {}
        status_name = status.get("name", "Unknown Status")
        assigned_user_id = task.get("assignedToUserId")
        assigned_user = user_display(assigned_user_id)

        # Count statistics
        status_counts[status_name] = status_counts.get(status_name, 0) + 1
        user_task_counts[assigned_user] = user_task_counts.get(assigned_user, 0) + 1

        # Get task description
        task_description = "No description available"
        task_id = task.get("id")
        if task_id:
            try:
                messages_endpoint = f"task/{task_id}/messages"
                messages_data = await make_goodday_request(messages_endpoint)
                if messages_data and isinstance(messages_data, list) and len(messages_data) > 0:
                    first_msg = messages_data[0]
                    if isinstance(first_msg, dict):
                        task_description = first_msg.get("message", "No description available")
            except Exception:
                pass

        task_summary = f"""
**{task_short_id}**: {task_name}
- **Status**: {status_name}
- **Assigned To**: {assigned_user}
- **Description**: {task_description}
""".strip()
        task_summaries.append(task_summary)

    # Build summary
    summary_parts = []
    summary_parts.append(f"**Sprint Overview:**\n- **Sprint**: {actual_sprint_name}\n- **Project**: {actual_project_name}\n- **Total Tasks**: {len(tasks_data)}")

    if status_counts:
        status_list = [f"  - {status}: {count}" for status, count in sorted(status_counts.items())]
        summary_parts.append(f"**Status Distribution:**\n{chr(10).join(status_list)}")

    if user_task_counts:
        user_list = [f"  - {user}: {count} tasks" for user, count in sorted(user_task_counts.items(), key=lambda x: x[1], reverse=True)]
        summary_parts.append(f"**Task Assignment:**\n{chr(10).join(user_list)}")

    if task_summaries:
        summary_parts.append(f"**Task Details:**\n{chr(10).join(['---'] + task_summaries)}")

    result = "\n\n".join(summary_parts)
    return f"**Sprint Summary for '{actual_sprint_name}' in '{actual_project_name}':**\n\n{result}"

# Smart Query Tool
@mcp.tool()
async def get_goodday_smart_query(query: str) -> str:
    """Natural language interface for common project management queries.

    Args:
        query: Natural language query (e.g., "show me all tasks assigned to John", "what projects do I have")
    """
    query_lower = query.lower().strip()
    
    # Parse common query patterns
    if "projects" in query_lower and ("my" in query_lower or "i have" in query_lower):
        return await get_projects()
    elif "users" in query_lower or "team members" in query_lower:
        return await get_users()
    elif "assigned to" in query_lower:
        # Extract user name from query
        user_match = re.search(r"assigned to (\w+)", query_lower)
        if user_match:
            user_name = user_match.group(1)
            user = await find_user_by_name_or_email(user_name)
            if user:
                return await get_user_assigned_tasks(user.get("id"))
            else:
                return f"User '{user_name}' not found."
        else:
            return "Please specify a user name for assigned tasks query."
    elif "action required" in query_lower:
        # Extract user name from query
        user_match = re.search(r"action required (?:for|by) (\w+)", query_lower)
        if user_match:
            user_name = user_match.group(1)
            user = await find_user_by_name_or_email(user_name)
            if user:
                return await get_user_action_required_tasks(user.get("id"))
            else:
                return f"User '{user_name}' not found."
        else:
            return "Please specify a user name for action required tasks query."
    else:
        return f"Query not recognized. Try queries like:\n- 'show me all projects'\n- 'show me all users'\n- 'show tasks assigned to [user]'\n- 'show action required tasks for [user]'"

# Vector Search Tool
@mcp.tool()
async def search_goodday_tasks(
    query: str, 
    limit: int = 10, 
    project_name: Optional[str] = None, 
    user_name: Optional[str] = None,
    include_closed: bool = False
) -> str:
    """Search for tasks using vector similarity search with optional filters.

    Args:
        query: Search query (natural language)
        limit: Maximum number of results to return (default: 10, max: 50)
        project_name: Optional project name filter (case-insensitive partial match)
        user_name: Optional user name/email filter for assigned tasks
        include_closed: Whether to include closed/completed tasks (default: False)
    """
    # Validate limit
    if limit > 50:
        limit = 50
    elif limit < 1:
        limit = 1

    # Build search parameters
    search_params = {
        "query": query,
        "limit": limit,
        "include_closed": include_closed
    }

    # Add optional filters
    if project_name:
        search_params["project_name"] = project_name
    if user_name:
        search_params["user_name"] = user_name

    try:
        # Make search request
        search_results = await make_search_request("GET", search_params)
        
        if not search_results:
            return "No results found for your search query."
        
        if isinstance(search_results, dict) and "error" in search_results:
            return f"Search error: {search_results.get('error', 'Unknown error')}"
        
        # Handle different response formats
        results = []
        if isinstance(search_results, dict):
            if "results" in search_results:
                results = search_results["results"]
            elif "tasks" in search_results:
                results = search_results["tasks"]
            else:
                # If it's a single result wrapped in a dict
                results = [search_results]
        elif isinstance(search_results, list):
            results = search_results
        else:
            return f"Unexpected search results format: {type(search_results)}"

        if not results:
            return "No tasks found matching your search criteria."

        # Get user mapping for display
        user_id_to_name = await get_user_mapping()
        
        def user_display(user_id):
            if not user_id:
                return "Unassigned"
            name = user_id_to_name.get(user_id)
            return name if name else f"User {user_id}"

        # Format results
        formatted_results = []
        for i, task in enumerate(results, 1):
            if not isinstance(task, dict):
                continue

            # Extract task information
            task_id = task.get("shortId", task.get("id", "N/A"))
            task_name = task.get("name", "No title")
            
            # Handle status information
            status = task.get("status", {})
            if isinstance(status, dict):
                status_name = status.get("name", "Unknown")
            else:
                status_name = str(status) if status else "Unknown"
            
            # Handle project information
            project = task.get("project", {})
            if isinstance(project, dict):
                project_name = project.get("name", "Unknown Project")
            else:
                project_name = str(project) if project else "Unknown Project"
            
            # Handle assigned user
            assigned_user_id = task.get("assignedToUserId")
            assigned_user = user_display(assigned_user_id)
            
            # Handle priority
            priority = task.get("priority", "N/A")
            
            # Handle dates
            start_date = format_timestamp_ist(task.get("startDate")) if task.get("startDate") else "N/A"
            end_date = format_timestamp_ist(task.get("endDate")) if task.get("endDate") else "N/A"
            
            # Handle description/message
            description = task.get("message", task.get("description", "No description"))
            
            # Handle similarity score if available
            score_info = ""
            if "score" in task:
                score_info = f" (Similarity: {task['score']:.3f})"
            elif "_score" in task:
                score_info = f" (Similarity: {task['_score']:.3f})"

            formatted_result = f"""
**{i}. {task_id}**: {task_name}{score_info}
- **Project**: {project_name}
- **Status**: {status_name}
- **Assigned To**: {assigned_user}
- **Priority**: {priority}
- **Start Date**: {start_date}
- **End Date**: {end_date}
- **Description**: {description[:200]}{'...' if len(description) > 200 else ''}
""".strip()
            formatted_results.append(formatted_result)

        result_text = "\n---\n".join(formatted_results)
        filter_info = []
        if project_name:
            filter_info.append(f"Project: {project_name}")
        if user_name:
            filter_info.append(f"User: {user_name}")
        if include_closed:
            filter_info.append("Including closed tasks")
        
        filter_text = f" (Filters: {', '.join(filter_info)})" if filter_info else ""
        
        return f"**Search Results for '{query}'{filter_text}:**\nFound {len(results)} result(s)\n\n{result_text}"

    except Exception as e:
        return f"Search error: {str(e)}"

# Document Management Tools
@mcp.tool()
async def search_project_documents(project_name: str, document_name: Optional[str] = None, include_content: bool = False) -> str:
    """Search for documents in a specific project.

    Args:
        project_name: The name of the project to search in (case-insensitive)
        document_name: Optional document name to filter by (case-insensitive partial match)
        include_content: Whether to include the full content of each document
    """
    # Find project
    projects_data = await make_goodday_request("projects?archived=true")
    if not projects_data or not isinstance(projects_data, list):
        return "Unable to fetch projects."

    project_type_projects = [p for p in projects_data if isinstance(p, dict) and p.get('systemType') in ['PROJECT', 'FOLDER']]
    matching_projects = []
    search_term = project_name.lower()
    for project in project_type_projects:
        if isinstance(project, dict) and search_term in project.get('name', '').lower():
            matching_projects.append(project)

    if not matching_projects:
        return f"No projects found containing '{project_name}' in their name."

    target_project = matching_projects[0]
    actual_project_name = target_project.get('name')
    project_id = target_project.get('id')

    # Get documents
    documents_data = await make_goodday_request(f"project/{project_id}/documents")
    if not documents_data:
        return f"No documents found in project '{actual_project_name}'."

    if isinstance(documents_data, dict) and "error" in documents_data:
        return f"Unable to fetch documents: {documents_data.get('error', 'Unknown error')}"

    if not isinstance(documents_data, list):
        return f"Unexpected response format for documents: {str(documents_data)}"

    # Filter by document name if specified
    if document_name:
        filtered_documents = []
        for doc in documents_data:
            if isinstance(doc, dict) and document_name.lower() in doc.get('name', '').lower():
                filtered_documents.append(doc)
        documents_data = filtered_documents

    if not documents_data:
        return f"No documents found matching '{document_name}' in project '{actual_project_name}'."

    # Get mappings
    user_id_to_name = await get_user_mapping()
    project_id_to_name = await get_project_mapping()

    # Format documents
    formatted_docs = []
    for doc in documents_data:
        if isinstance(doc, dict):
            doc_id = doc.get('id', 'N/A')
            doc_content = ""
            
            if include_content and doc_id != 'N/A':
                try:
                    content_data = await make_goodday_request(f"document/{doc_id}")
                    if content_data:
                        if isinstance(content_data, dict):
                            doc_content = content_data.get('content', content_data.get('text', str(content_data)))
                        else:
                            doc_content = str(content_data)
                except Exception as e:
                    doc_content = f"Error fetching content: {str(e)}"
            
            project_id_val = doc.get('projectId', 'N/A')
            project_name_val = project_id_to_name.get(project_id_val, f"Project {project_id_val}") if project_id_val != 'N/A' else 'N/A'
            
            created_by_id = doc.get('createdByUserId', 'N/A')
            created_by_name = user_id_to_name.get(created_by_id, f"User {created_by_id}") if created_by_id != 'N/A' else 'N/A'
            
            formatted_doc = f"""
**Document ID:** {doc_id}
**Name:** {doc.get('name', 'N/A')}
**Project:** {project_name_val}
**Created By:** {created_by_name}
**Created:** {format_timestamp_ist(doc.get('momentCreated', 'N/A'))}
**Updated:** {format_timestamp_ist(doc.get('momentUpdated', 'N/A'))}"""
            
            if include_content:
                formatted_doc += f"\n**Content:**\n{doc_content}"
            
            formatted_docs.append(formatted_doc.strip())

    result = "\n---\n".join(formatted_docs)
    filter_text = f" matching '{document_name}'" if document_name else ""
    return f"**Documents in project '{actual_project_name}'{filter_text}:**\n\n{result}"

@mcp.tool()
async def get_document_content(document_id: str) -> str:
    """Get the content of a specific document by its ID.

    Args:
        document_id: The ID of the document to retrieve
    """
    data = await make_goodday_request(f"document/{document_id}")

    if not data:
        return "Document not found or no content available."

    if isinstance(data, dict) and "error" in data:
        return f"Unable to fetch document: {data.get('error', 'Unknown error')}"

    if isinstance(data, dict):
        content = data.get('content', data.get('text', str(data)))
    else:
        content = str(data)

    return f"**Document Content:**\n\n{content}"

def run_cli():
    """CLI entry point for the goodday-mcp server."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    run_cli()
