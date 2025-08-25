"""Core tools for DevAgent specialist agents."""

import subprocess
import glob
import os
from typing import Dict, Any, List
from langchain_core.tools import tool


@tool
def read_file_tool(file_path: str) -> str:
    """Read contents of a file.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File contents as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"


@tool
def write_file_tool(file_path: str, content: str) -> str:
    """Write content to a file.
    
    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        
    Returns:
        Success message or error
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing to {file_path}: {str(e)}"


@tool
def glob_tool(pattern: str, recursive: bool = True) -> List[str]:
    """Find files matching a glob pattern.
    
    Args:
        pattern: Glob pattern (e.g., "**/*.py", "src/*.js")
        recursive: Whether to search recursively
        
    Returns:
        List of matching file paths
    """
    try:
        if recursive:
            files = glob.glob(pattern, recursive=True)
        else:
            files = glob.glob(pattern)
        return sorted(files)
    except Exception as e:
        return [f"Error with glob pattern {pattern}: {str(e)}"]


@tool
def bash_tool(command: str) -> Dict[str, Any]:
    """Execute a bash command.
    
    Args:
        command: The bash command to execute
        
    Returns:
        Dictionary with stdout, stderr, and return_code
    """
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=30  # 30 second timeout
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr, 
            "return_code": result.returncode,
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Command '{command}' timed out after 30 seconds",
            "return_code": -1,
            "success": False
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Error executing command '{command}': {str(e)}",
            "return_code": -1,
            "success": False
        }


@tool
def grep_tool(pattern: str, file_path: str) -> List[str]:
    """Search for pattern in a file.
    
    Args:
        pattern: Search pattern/regex
        file_path: Path to file to search in
        
    Returns:
        List of matching lines
    """
    try:
        import re
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        matches = []
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                matches.append(f"{i}: {line.rstrip()}")
        
        return matches
    except Exception as e:
        return [f"Error searching in {file_path}: {str(e)}"]


# Tool collections for different agent types
RETRIEVER_TOOLS = [read_file_tool, glob_tool, grep_tool, bash_tool]
EDITOR_TOOLS = [read_file_tool, write_file_tool, bash_tool]
EXECUTOR_TOOLS = [bash_tool, read_file_tool]
VERIFIER_TOOLS = [read_file_tool, bash_tool]
PR_BOT_TOOLS = [bash_tool, read_file_tool]