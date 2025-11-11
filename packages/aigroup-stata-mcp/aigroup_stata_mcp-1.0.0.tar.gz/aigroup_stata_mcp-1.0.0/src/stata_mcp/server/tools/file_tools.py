#!/usr/bin/python3
# -*- coding: utf-8 -*-


import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from mcp.server.fastmcp import Context, FastMCP, Image
from mcp.server.session import ServerSession
from pydantic import BaseModel, Field


class ReadFileResult(BaseModel):
   
   
    """Result model for file reading operation."""
    
    file_path: str = Field(description="The path to the file that was read")
    content: str = Field(description="The content of the file")
    encoding: str = Field(description="The encoding used to read the file")


class WriteDofileResult(BaseModel):
   
   
    """Result model for dofile writing operation."""
    
    file_path: str = Field(description="The path to the created dofile")
    content_length: int = Field(description="The length of the content written")
    timestamp: str = Field(description="The timestamp when the file was created")


class AppendDofileResult(BaseModel):
   
   
    """Result model for dofile appending operation."""
    
    new_file_path: str = Field(description="The path to the new dofile")
    original_exists: bool = Field(description="Whether the original file existed")
    total_content_length: int = Field(description="Total length of content after appending")


def register_file_tools(server: FastMCP) -> None:
    """Register file-related tools with the MCP server."""
    
    @server.tool()
    def read_file(ctx: Context[ServerSession, Dict], file_path: str, encoding: str = "utf-8") -> ReadFileResult:
        """
        Reads a file and returns its content as a string.
        
        Args:
            file_path: The full path to the file to be read.
            encoding: The encoding used to decode the file. Defaults to "utf-8".
            
        Returns:
            ReadFileResult: Structured result containing file content and metadata.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file at {file_path} does not exist.")

        try:
            with open(file_path, "r", encoding=encoding) as file:
                log_content = file.read()
            
            return ReadFileResult(
                file_path=file_path,
                content=log_content,
                encoding=encoding
            )
        except IOError as e:
            raise IOError(f"An error occurred while reading the file: {e}")

    @server.tool()
    def write_dofile(ctx: Context[ServerSession, Dict], content: str, encoding: str = "utf-8") -> WriteDofileResult:
        """
        Write stata code to a dofile and return the do-file path.
        
        Args:
            content: The stata code content which will be written to the designated do-file.
            encoding: The encoding method for the dofile, default -> 'utf-8'
            
        Returns:
            WriteDofileResult: Structured result containing file path and metadata.
        """
        stata_context = ctx.request_context.lifespan_context["stata_context"]
        dofile_base_path = stata_context.output_base_path / "stata-mcp-dofile"
        
        file_path = dofile_base_path / f"{datetime.now().strftime('%Y%m%d%H%M%S')}.do"
        
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
        
        return WriteDofileResult(
            file_path=str(file_path),
            content_length=len(content),
            timestamp=datetime.now().isoformat()
        )

    @server.tool()
    def append_dofile(ctx: Context[ServerSession, Dict], original_dofile_path: str, content: str, encoding: str = "utf-8") -> AppendDofileResult:
        """
        Append stata code to an existing dofile or create a new one.
        
        Args:
            original_dofile_path: Path to the original dofile to append to.
                If empty or invalid, a new file will be created.
            content: The stata code content which will be appended to the designated do-file.
            encoding: The encoding method for the dofile, default -> 'utf-8'
            
        Returns:
            AppendDofileResult: Structured result containing new file path and metadata.
        """
        stata_context = ctx.request_context.lifespan_context["stata_context"]
        dofile_base_path = stata_context.output_base_path / "stata-mcp-dofile"
        
        # Create a new file path for the output
        new_file_path = dofile_base_path / f"{datetime.now().strftime('%Y%m%d%H%M%S')}.do"
        
        # Check if original file exists and is valid
        original_exists = False
        original_content = ""
        if original_dofile_path and os.path.exists(original_dofile_path):
            try:
                with open(original_dofile_path, "r", encoding=encoding) as f:
                    original_content = f.read()
                original_exists = True
            except Exception:
                # If there's any error reading the file, we'll create a new one
                original_exists = False

        # Write to the new file (either copying original content + new content, or just new content)
        with open(new_file_path, "w", encoding=encoding) as f:
            if original_exists:
                f.write(original_content)
                # Add a newline if the original file doesn't end with one
                if original_content and not original_content.endswith("\n"):
                    f.write("\n")
            f.write(content)
        
        total_length = len(original_content) + len(content) if original_exists else len(content)
        
        return AppendDofileResult(
            new_file_path=str(new_file_path),
            original_exists=original_exists,
            total_content_length=total_length
        )

    @server.tool()
    def load_figure(ctx: Context[ServerSession, Dict], figure_path: str) -> Image:
        """
        Load figure from device.
        
        Args:
            figure_path: the figure file path, only support png and jpg format
            
        Returns:
            Image: the figure thumbnail
        """
        if not os.path.exists(figure_path):
            raise FileNotFoundError(f"{figure_path} not found")
        return Image(figure_path)