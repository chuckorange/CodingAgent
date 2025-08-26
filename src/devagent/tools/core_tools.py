"""Core tools for DevAgent specialist agents."""

import subprocess
import glob
import os
import logging
from typing import Dict, Any, List
from langchain_core.tools import tool

# Set up basic logging for tools to stdout
logger = logging.getLogger("devagent.tools")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


@tool
def read_file_tool(file_path: str) -> str:
    """Read contents of a file.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File contents as string
    """
    logger.info(f"📖 READ_FILE: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            logger.info(f"✅ READ_FILE: Success ({len(content)} chars)")
            return content
    except Exception as e:
        error_msg = f"Error reading file {file_path}: {str(e)}"
        logger.error(f"❌ READ_FILE: {error_msg}")
        return error_msg


@tool
def write_file_tool(file_path: str, content: str) -> str:
    """Write content to a file.
    
    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        
    Returns:
        Success message or error
    """
    logger.info(f"✍️ WRITE_FILE: {file_path} ({len(content)} chars)")
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        success_msg = f"Successfully wrote to {file_path}"
        logger.info(f"✅ WRITE_FILE: {success_msg}")
        return success_msg
    except Exception as e:
        error_msg = f"Error writing to {file_path}: {str(e)}"
        logger.error(f"❌ WRITE_FILE: {error_msg}")
        return error_msg


@tool
def glob_tool(pattern: str, recursive: bool = True) -> List[str]:
    """Find files matching a glob pattern.
    
    Args:
        pattern: Glob pattern (e.g., "**/*.py", "src/*.js")
        recursive: Whether to search recursively
        
    Returns:
        List of matching file paths
    """
    logger.info(f"🔍 GLOB: {pattern} (recursive={recursive})")
    try:
        if recursive:
            files = glob.glob(pattern, recursive=True)
        else:
            files = glob.glob(pattern)
        sorted_files = sorted(files)
        logger.info(f"✅ GLOB: Found {len(sorted_files)} files")
        return sorted_files
    except Exception as e:
        error_msg = f"Error with glob pattern {pattern}: {str(e)}"
        logger.error(f"❌ GLOB: {error_msg}")
        return [error_msg]


@tool
def bash_tool(command: str) -> Dict[str, Any]:
    """Execute a bash command.
    
    Args:
        command: The bash command to execute
        
    Returns:
        Dictionary with stdout, stderr, and return_code
    """
    logger.info(f"💻 BASH: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=30  # 30 second timeout
        )
        result_dict = {
            "stdout": result.stdout,
            "stderr": result.stderr, 
            "return_code": result.returncode,
            "success": result.returncode == 0
        }
        
        if result.returncode == 0:
            output_preview = result.stdout.strip()[:100] + "..." if len(result.stdout.strip()) > 100 else result.stdout.strip()
            logger.info("✅ BASH: Success")
            logger.info("```")
            logger.info(result.stdout)
            logger.info("```")
        else:
            logger.error(f"❌ BASH: Failed (code {result.returncode}) - {result.stderr.strip()[:100]}")
            
        return result_dict
    except subprocess.TimeoutExpired:
        error_result = {
            "stdout": "",
            "stderr": f"Command '{command}' timed out after 30 seconds",
            "return_code": -1,
            "success": False
        }
        logger.error(f"❌ BASH: Timeout - {command}")
        return error_result
    except Exception as e:
        error_result = {
            "stdout": "",
            "stderr": f"Error executing command '{command}': {str(e)}",
            "return_code": -1,
            "success": False
        }
        logger.error(f"❌ BASH: Exception - {str(e)}")
        return error_result


@tool
def grep_tool(pattern: str, file_path: str) -> List[str]:
    """Search for pattern in a file.
    
    Args:
        pattern: Search pattern/regex
        file_path: Path to file to search in
        
    Returns:
        List of matching lines
    """
    logger.info(f"🔎 GREP: '{pattern}' in {file_path}")
    try:
        import re
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        matches = []
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                matches.append(f"{i}: {line.rstrip()}")
        
        logger.info(f"✅ GREP: Found {len(matches)} matches")
        return matches
    except Exception as e:
        error_msg = f"Error searching in {file_path}: {str(e)}"
        logger.error(f"❌ GREP: {error_msg}")
        return [error_msg]


# Tool collections for different agent types
RETRIEVER_TOOLS = [read_file_tool, glob_tool, grep_tool, bash_tool]
EDITOR_TOOLS = [read_file_tool, write_file_tool, bash_tool]
EXECUTOR_TOOLS = [bash_tool, read_file_tool]
VERIFIER_TOOLS = [read_file_tool, bash_tool]
PR_BOT_TOOLS = [bash_tool, read_file_tool]