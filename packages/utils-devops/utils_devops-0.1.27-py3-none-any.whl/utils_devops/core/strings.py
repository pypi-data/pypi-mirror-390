# src/utils_devops/core/strings.py
"""
Strings Module for utils_devops.

Provides utilities for advanced string manipulation, templating, and editing
configuration strings (YAML, JSON, INI, .env). Designed for generating scripts
and updating text-based files in automation workflows.

Notes:
- Uses Jinja2 for templating.
- Uses ruamel.yaml for YAML editing (preserves comments where possible).
- Uses python-dotenv for .env parsing.
- Integrates with file helpers (backup/restore/read/write) and systems.run for command execution.
- Functions raise `StringsError` on failure.
"""

from __future__ import annotations

from pathlib import Path
import re
import json
import io
import configparser
import subprocess
from typing import Any, Dict, List, Optional, Union, Iterable

from jinja2 import Environment, Template, TemplateError
from dotenv import dotenv_values  # python-dotenv
import ruamel.yaml  # from extras yaml-rt

from .logs import get_library_logger
from .files import backup_file, restore_file, read_file, write_file, FileOpsError  # Assuming these exist
from .systems import run

log = get_library_logger()

# Public API for IDEs / help()
__all__ = [
    "StringsError",
    "help",
    # Basic ops
    "to_upper",
    "to_lower",
    "strip_whitespace",
    "split_string",
    "join_strings",
    "replace_substring",
    "find_substring",
    "startswith",
    "endswith",
    # Advanced / regex
    "regex_search",
    "regex_replace",
    "regex_findall",
    "format_string",
    "f_format",
    "indent_multiline",
    "dedent_multiline",
    "comment_lines",
    "uncomment_lines",
    # Block manipulation
    "comment_block",
    "insert_block",
    "remove_block",
    "uncomment_block",
    # Templating
    "render_jinja",
    "render_jinja_safe",
    # Parsing / dumping
    "update_json",
    "update_yaml",
    "update_ini",
    "update_env",
    "parse_json",
    "parse_yaml",
    "parse_ini",
    "parse_env",
    "dump_json",
    "dump_yaml",
    "dump_ini",
    "dump_env",
    # Script generation
    "generate_script",
    "add_line",
    "remove_line",
    "update_key_value",
    # File-integrated config update
    "update_config_file",
    # Helpers
    "render_jinja",
    "generate_script",
]

class StringsError(Exception):
    """Custom exception for string operations failures."""
    pass


def help() -> None:
    """Print a quick index of available functions in this module."""
    print(
        """
DevOps Utils — Strings Module
This module provides utilities for advanced string manipulation, formatting, templating, and editing configuration strings (YAML, JSON, INI, .env).
Key functions include:
Basic ops
to_upper(s: str) -> str: Convert string to uppercase.
to_lower(s: str) -> str: Convert string to lowercase.
strip_whitespace(s: str) -> str: Strip leading/trailing whitespace.
split_string(s: str, delimiter: str = ' ') -> List[str]: Split string by delimiter.
join_strings(parts: Iterable[str], delimiter: str = ' ') -> str: Join strings with delimiter.
replace_substring(s: str, old: str, new: str, count: int = -1) -> str: Replace occurrences of substring.
find_substring(s: str, sub: str) -> int: Find first occurrence index (-1 if not found).
startswith(s: str, prefix: str) -> bool: Check if string starts with prefix.
endswith(s: str, suffix: str) -> bool: Check if string ends with suffix.
Advanced / regex
regex_search(s: str, pattern: str) -> Optional[str]: Find first regex match.
regex_replace(s: str, pattern: str, replacement: str) -> str: Replace regex matches.
regex_findall(s: str, pattern: str) -> List[str]: Find all regex matches.
format_string(template: str, **kwargs: Any) -> str: Use str.format with kwargs.
f_format(template: str, **kwargs: Any) -> str: Use f-string like formatting (uses eval, trusted templates only).
indent_multiline(s: str, indent: int = 4) -> str: Indent multi-line string by given spaces.
dedent_multiline(s: str) -> str: Remove common leading whitespace from multi-line string.
comment_lines(s: str, comment_char: str = '#', lines: Optional[Iterable[int]] = None) -> str: Comment specific or all lines.
uncomment_lines(s: str, comment_char: str = '#') -> str: Remove comment prefix from lines.
Block manipulation
comment_block(s: str, start_marker: str, end_marker: str, comment_char: str = '#') -> str: Comment each line between start_marker and end_marker (inclusive).
insert_block(s: str, block_text: str, before_marker: Optional[str] = None, after_marker: Optional[str] = None) -> str: Insert a block of text before or after a marker line in the string.
remove_block(s: str, start_marker: str, end_marker: str) -> str: Remove the block between start_marker and end_marker (inclusive).
uncomment_block(s: str, start_marker: str, end_marker: str, comment_char: str = '#') -> str: Uncomment lines between start_marker and end_marker (inclusive) by removing comment prefix if present.
Templating
render_jinja(template_str: str, context: Dict[str, Any]) -> str: Render a Jinja2 template string with given context.
render_jinja_safe(template_str: str, context: Dict[str, Any]) -> str: Render a Jinja2 template with autoescape enabled (safer for HTML-like content).
Parsing / dumping
update_json(json_str: str, key_path: str, value: Any) -> str: Update a JSON string at dot-notation key_path with value and return updated JSON string.
update_yaml(yaml_str: str, key_path: str, value: Any, preserve_comments: bool = True) -> str: Update YAML string at dot-notation key_path with value and return updated YAML string.
update_ini(ini_str: str, section: str, key: str, value: str) -> str: Update INI section/key and return updated INI string.
update_env(env_str: str, key: str, value: str) -> str: Update .env content and return updated text.
parse_json(s: str) -> Dict[str, Any]: Parse JSON string to dict.
parse_yaml(s: str) -> Dict[str, Any]: Parse YAML string to Python data structure using ruamel.yaml.
parse_ini(s: str) -> Dict[str, Dict[str, str]]: Parse INI string to nested dict.
parse_env(s: str) -> Dict[str, str]: Parse .env string to dict.
dump_json(data: Dict[str, Any], indent: int = 4) -> str: Dump dict to JSON string.
dump_yaml(data: Dict[str, Any]) -> str: Dump dict to YAML string using ruamel.yaml.
dump_ini(data: Dict[str, Dict[str, str]]) -> str: Dump dict to INI formatted string.
dump_env(data: Dict[str, str]) -> str: Dump dict to .env formatted string.
Script generation
generate_script(lines: List[str], shebang: str = '#!/bin/bash') -> str: Build script from lines with shebang and return as string.
add_line(s: str, line: str, after: Optional[str] = None) -> str: Add a line after a marker or at end and return updated string.
remove_line(s: str, line: str) -> str: Remove exact matching line from string and return result.
update_key_value(s: str, key: str, value: str, delimiter: str = '=') -> str: Update or append key=value in text content and return updated string.
File-integrated config update
update_config_file(file_path: Union[str, Path], updates: Dict[str, Any], config_type: str = 'auto', test_cmd: Optional[Union[str, List[str]]] = None, reload_cmd: Optional[Union[str, List[str]]] = None) -> bool: Update variables in a file with safe backup/test/rollback behavior.
"""
    )


# ========================
# Basic String Operations
# ========================

def to_upper(s: str) -> str:
    """Convert string to uppercase."""
    result = s.upper()
    log.debug(f"Converted to upper: {s} -> {result}")
    return result

def to_lower(s: str) -> str:
    """Convert string to lowercase."""
    result = s.lower()
    log.debug(f"Converted to lower: {s} -> {result}")
    return result

def strip_whitespace(s: str) -> str:
    """Strip leading/trailing whitespace."""
    result = s.strip()
    log.debug(f"Stripped whitespace: {s} -> {result}")
    return result

def split_string(s: str, delimiter: str = ' ') -> List[str]:
    """Split string by delimiter."""
    parts = s.split(delimiter)
    log.debug(f"Split '{s}' by '{delimiter}': {parts}")
    return parts

def join_strings(parts: Iterable[str], delimiter: str = ' ') -> str:
    """Join strings with delimiter."""
    result = delimiter.join(parts)
    log.debug(f"Joined {parts} with '{delimiter}': {result}")
    return result

def replace_substring(s: str, old: str, new: str, count: int = -1) -> str:
    """Replace occurrences of substring."""
    result = s.replace(old, new, count)
    log.debug(f"Replaced '{old}' with '{new}' in '{s}': {result}")
    return result

def find_substring(s: str, sub: str) -> int:
    """Find first occurrence index (-1 if not found)."""
    idx = s.find(sub)
    log.debug(f"Found '{sub}' in '{s}' at {idx}")
    return idx

def startswith(s: str, prefix: str) -> bool:
    """Check if string starts with prefix."""
    result = s.startswith(prefix)
    log.debug(f"'{s}' starts with '{prefix}': {result}")
    return result

def endswith(s: str, suffix: str) -> bool:
    """Check if string ends with suffix."""
    result = s.endswith(suffix)
    log.debug(f"'{s}' ends with '{suffix}': {result}")
    return result


# ========================
# Advanced String Operations
# ========================

def regex_search(s: str, pattern: str) -> Optional[str]:
    """Find first regex match."""
    match = re.search(pattern, s)
    result = match.group(0) if match else None
    log.debug(f"Regex search '{pattern}' in '{s}': {result}")
    return result

def regex_replace(s: str, pattern: str, replacement: str) -> str:
    """Replace regex matches."""
    result = re.sub(pattern, replacement, s)
    log.debug(f"Regex replace '{pattern}' with '{replacement}' in '{s}': {result}")
    return result

def regex_findall(s: str, pattern: str) -> List[str]:
    """Find all regex matches."""
    matches = re.findall(pattern, s)
    log.debug(f"Regex findall '{pattern}' in '{s}': {matches}")
    return matches

def format_string(template: str, **kwargs: Any) -> str:
    """Use str.format with kwargs."""
    result = template.format(**kwargs)
    log.debug(f"Formatted '{template}' with {kwargs}: {result}")
    return result

def f_format(template: str, **kwargs: Any) -> str:
    """
    Use f-string like formatting.

    WARNING: this uses eval() to mimic f-string behavior. Only use trusted templates.
    """
    result = eval(f"f'''{template}'''", {}, kwargs)
    log.debug(f"f-formatted '{template}' with {kwargs}: {result}")
    return result

def indent_multiline(s: str, indent: int = 4) -> str:
    """Indent multi-line string by given spaces."""
    prefix = ' ' * indent
    result = '\n'.join(prefix + line for line in s.splitlines())
    log.debug(f"Indented '{s}' by {indent}: {result}")
    return result

def dedent_multiline(s: str) -> str:
    """Remove common leading whitespace from multi-line string."""
    lines = s.splitlines()
    if not lines:
        return s
    min_indent = min((len(line) - len(line.lstrip())) for line in lines if line.strip()) if any(line.strip() for line in lines) else 0
    result = '\n'.join(line[min_indent:] for line in lines)
    log.debug(f"Dedented '{s}': {result}")
    return result

def comment_lines(s: str, comment_char: str = '#', lines: Optional[Iterable[int]] = None) -> str:
    """Comment specific or all lines."""
    all_lines = s.splitlines()
    if lines is None:
        target = range(len(all_lines))
    else:
        target = set(lines)
    for i in range(len(all_lines)):
        if i in target:
            all_lines[i] = f"{comment_char} {all_lines[i]}"
    result = '\n'.join(all_lines)
    log.debug(f"Commented lines in '{s}': {result}")
    return result

def uncomment_lines(s: str, comment_char: str = '#') -> str:
    """Remove comment prefix from lines."""
    lines = s.splitlines()
    result = '\n'.join(line.lstrip().removeprefix(comment_char).lstrip() for line in lines)
    log.debug(f"Uncommented '{s}': {result}")
    return result


# ========================
# Block Manipulation in Strings
# ========================

def insert_block(s: str, block_text: str, before_marker: Optional[str] = None, after_marker: Optional[str] = None) -> str:
    """Insert a block of text before or after a marker line in the string.
    
    If before_marker is provided, insert before the first line containing it.
    If after_marker is provided, insert after the first line containing it.
    If neither, append to the end. Block is indented to match the marker's indent if possible.
    """
    lines = s.splitlines(keepends=True)
    insert_idx = len(lines)  # Default: append
    matched_indent = 0
    if before_marker:
        for i, line in enumerate(lines):
            if before_marker in line:
                insert_idx = i
                matched_indent = len(line) - len(line.lstrip())
                break
    elif after_marker:
        for i, line in enumerate(lines):
            if after_marker in line:
                insert_idx = i + 1
                matched_indent = len(line) - len(line.lstrip())
                break

    # Indent block to match
    block_lines = block_text.splitlines(keepends=True)
    indented_block = [f"{' ' * matched_indent}{bl}" for bl in block_lines]

    # Insert
    lines[insert_idx:insert_idx] = indented_block
    result = ''.join(lines)
    log.debug(f"Inserted block into '{s}' at idx {insert_idx} (indent={matched_indent}): {result}")
    return result

def comment_block(s: str, start_marker: str, end_marker: str, comment_char: str = '#') -> str:
    """Comment each line between start_marker and end_marker (inclusive) by adding comment prefix.
    
    Assumes first occurrence and markers on own lines.
    """
    lines = s.splitlines(keepends=True)
    new_lines = []
    inside = False
    for line in lines:
        if inside:
            new_lines.append(f"{comment_char} {line}")
            if end_marker in line:
                inside = False
        else:
            new_lines.append(line)
            if start_marker in line:
                inside = True
    result = ''.join(new_lines)
    log.info(f"Commented block in '{s}' between '{start_marker}' and '{end_marker}'")
    return result

def uncomment_block(s: str, start_marker: str, end_marker: str, comment_char: str = '#') -> str:
    """Uncomment lines between start_marker and end_marker (inclusive) by removing comment prefix if present.
    
    Assumes first occurrence and markers on own lines.
    """
    lines = s.splitlines(keepends=True)
    new_lines = []
    inside = False
    for line in lines:
        if inside:
            if line.lstrip().startswith(comment_char):
                new_line = line.lstrip().removeprefix(comment_char).lstrip()
                # Preserve original indent
                orig_indent = len(line) - len(line.lstrip())
                new_line = ' ' * orig_indent + new_line
            else:
                new_line = line
            new_lines.append(new_line)
            if end_marker in line:
                inside = False
        else:
            new_lines.append(line)
            if start_marker in line:
                inside = True
    result = ''.join(new_lines)
    log.info(f"Uncommented block in '{s}' between '{start_marker}' and '{end_marker}'")
    return result

def remove_block(s: str, start_marker: str, end_marker: str) -> str:
    """Remove the block between start_marker and end_marker (inclusive).
    
    Assumes first occurrence and markers on own lines.
    """
    lines = s.splitlines(keepends=True)
    new_lines = []
    inside = False
    for line in lines:
        if inside:
            if end_marker in line:
                inside = False
            continue
        if start_marker in line:
            inside = True
            continue
        new_lines.append(line)
    result = ''.join(new_lines)
    log.info(f"Removed block in '{s}' between '{start_marker}' and '{end_marker}'")
    return result


# ========================
# Templating
# ========================

env = Environment(autoescape=False)  # For configs, no HTML escape

def render_jinja(template_str: str, context: Dict[str, Any]) -> str:
    """Render a Jinja2 template string with given context."""
    try:
        template = Template(template_str)
        result = template.render(context)
        log.debug(f"Rendered Jinja template with {context}: {result}")
        return result
    except TemplateError as e:
        log.error(f"Failed to render Jinja: {e}")
        raise StringsError(f"Jinja render failed: {e}") from e

def render_jinja_safe(template_str: str, context: Dict[str, Any]) -> str:
    """Render a Jinja2 template with autoescape enabled (safer for HTML-like content)."""
    env_local = Environment(autoescape=True)
    try:
        template = env_local.from_string(template_str)
        result = template.render(context)
        log.debug(f"Rendered safe Jinja with {context}: {result}")
        return result
    except TemplateError as e:
        log.error(f"Failed to render safe Jinja: {e}")
        raise StringsError(f"Jinja safe render failed: {e}") from e


# ========================
# Config Editing (String Input/Output)
# ========================

def update_json(json_str: str, key_path: str, value: Any) -> str:
    """
    Update a JSON string at dot-notation key_path with value and return updated JSON string.
    """
    try:
        data = json.loads(json_str)
        keys = key_path.split('.')
        d = data
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value
        result = json.dumps(data, indent=4)
        log.info(f"Updated JSON key '{key_path}' to {value}")
        return result
    except json.JSONDecodeError as e:
        log.error(f"Invalid JSON: {e}")
        raise StringsError(f"Invalid JSON: {e}") from e

def update_yaml(yaml_str: str, key_path: str, value: Any, preserve_comments: bool = True) -> str:
    """
    Update YAML string at dot-notation key_path with value and return updated YAML string.
    Uses ruamel.yaml to preserve comments where possible.
    """
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    try:
        data = yaml.load(yaml_str) or {}
        keys = key_path.split('.')
        d = data
        for k in keys[:-1]:
            if k not in d or d[k] is None:
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value
        output = io.StringIO()
        yaml.dump(data, output)
        result = output.getvalue()
        log.info(f"Updated YAML key '{key_path}' to {value}")
        return result
    except ruamel.yaml.YAMLError as e:
        log.error(f"Invalid YAML: {e}")
        raise StringsError(f"Invalid YAML: {e}") from e

def update_ini(ini_str: str, section: str, key: str, value: str) -> str:
    """Update INI section/key and return updated INI string."""
    config = configparser.ConfigParser()
    try:
        config.read_string(ini_str)
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, key, value)
        output = io.StringIO()
        config.write(output)
        result = output.getvalue()
        log.info(f"Updated INI [{section}] {key} = {value}")
        return result
    except configparser.Error as e:
        log.error(f"INI error: {e}")
        raise StringsError(f"INI error: {e}") from e

def update_env(env_str: str, key: str, value: str) -> str:
    """Update .env content and return updated text."""
    data = dotenv_values(stream=io.StringIO(env_str))
    data = dict(data)
    data[key] = value
    result = '\n'.join(f"{k}={v}" for k, v in data.items() if v is not None)
    log.info(f"Updated .env {key} = {value}")
    return result


def parse_json(s: str) -> Dict[str, Any]:
    """Parse JSON string to dict."""
    try:
        data = json.loads(s)
        log.debug(f"Parsed JSON: {data}")
        return data
    except json.JSONDecodeError as e:
        log.error(f"Invalid JSON: {e}")
        raise StringsError(f"Invalid JSON: {e}") from e

def parse_yaml(s: str) -> Dict[str, Any]:
    """Parse YAML string to Python data structure using ruamel.yaml."""
    yaml = ruamel.yaml.YAML()
    try:
        data = yaml.load(s)
        log.debug(f"Parsed YAML: {data}")
        return data
    except ruamel.yaml.YAMLError as e:
        log.error(f"Invalid YAML: {e}")
        raise StringsError(f"Invalid YAML: {e}") from e

def parse_ini(s: str) -> Dict[str, Dict[str, str]]:
    """Parse INI string to nested dict."""
    config = configparser.ConfigParser()
    try:
        config.read_string(s)
        data = {sec: dict(config[sec]) for sec in config.sections()}
        log.debug(f"Parsed INI: {data}")
        return data
    except configparser.Error as e:
        log.error(f"INI error: {e}")
        raise StringsError(f"INI error: {e}") from e

def parse_env(s: str) -> Dict[str, str]:
    """Parse .env string to dict."""
    data = dotenv_values(stream=io.StringIO(s))
    log.debug(f"Parsed .env: {data}")
    return dict(data)

def dump_json(data: Dict[str, Any], indent: int = 4) -> str:
    """Dump dict to JSON string."""
    result = json.dumps(data, indent=indent)
    log.debug(f"Dumped JSON: {result}")
    return result

def dump_yaml(data: Dict[str, Any]) -> str:
    """Dump dict to YAML string using ruamel.yaml."""
    yaml = ruamel.yaml.YAML()
    output = io.StringIO()
    yaml.dump(data, output)
    result = output.getvalue()
    log.debug(f"Dumped YAML: {result}")
    return result

def dump_ini(data: Dict[str, Dict[str, str]]) -> str:
    """Dump dict to INI formatted string."""
    config = configparser.ConfigParser()
    for sec, items in data.items():
        config[sec] = items
    output = io.StringIO()
    config.write(output)
    result = output.getvalue()
    log.debug(f"Dumped INI: {result}")
    return result

def dump_env(data: Dict[str, str]) -> str:
    """Dump dict to .env formatted string."""
    result = '\n'.join(f"{k}={v}" for k, v in data.items() if v is not None)
    log.debug(f"Dumped .env: {result}")
    return result


# ========================
# Script Generation
# ========================

def generate_script(lines: List[str], shebang: str = '#!/bin/bash') -> str:
    """Build script from lines with shebang and return as string."""
    result = shebang + '\n' + '\n'.join(lines)
    log.info(f"Generated script: {result}")
    return result

def add_line(s: str, line: str, after: Optional[str] = None) -> str:
    """Add a line after a marker or at end and return updated string."""
    lines = s.splitlines()
    if after:
        for i, l in enumerate(lines):
            if after in l:
                lines.insert(i + 1, line)
                break
        else:
            lines.append(line)
    else:
        lines.append(line)
    result = '\n'.join(lines)
    log.debug(f"Added line '{line}' to '{s}': {result}")
    return result

def remove_line(s: str, line: str) -> str:
    """Remove exact matching line from string and return result."""
    lines = [l for l in s.splitlines() if l.strip() != line.strip()]
    result = '\n'.join(lines)
    log.debug(f"Removed line '{line}' from '{s}': {result}")
    return result

def update_key_value(s: str, key: str, value: str, delimiter: str = '=') -> str:
    """Update or append key=value in text content and return updated string."""
    lines = []
    updated = False
    for l in s.splitlines():
        if l.strip().startswith(key + delimiter):
            lines.append(f"{key}{delimiter}{value}")
            updated = True
        else:
            lines.append(l)
    if not updated:
        lines.append(f"{key}{delimiter}{value}")
    result = '\n'.join(lines)
    log.debug(f"Updated key '{key}' to '{value}' in '{s}': {result}")
    return result


# ========================
# Advanced Config Editing with File Integration
# ========================

def _apply_updates_to_json_content(content: str, updates: Dict[str, Any]) -> str:
    out = content
    for key_path, value in updates.items():
        out = update_json(out, key_path, value)
    return out

def _apply_updates_to_yaml_content(content: str, updates: Dict[str, Any]) -> str:
    out = content
    for key_path, value in updates.items():
        out = update_yaml(out, key_path, value)
    return out

def update_config_file(
    file_path: Union[str, Path],
    updates: Dict[str, Any],
    config_type: str = 'auto',
    test_cmd: Optional[Union[str, List[str]]] = None,
    reload_cmd: Optional[Union[str, List[str]]] = None
) -> bool:
    """
    Update variables in a file with safe backup/test/rollback behavior.

    Args:
        file_path: path to the configuration file.
        updates: For json/yaml: mapping of 'dot.path' -> value.
                 For ini: either {section: {key: value}} or {'section.key': value}.
                 For env: mapping of key -> value.
        config_type: 'auto'|'json'|'yaml'|'ini'|'env'|'nginx'|'keyvalue'
        test_cmd: optional command (str or list) to validate config after write.
        reload_cmd: optional command (str or list) to reload service after write.
    Returns:
        True on success, False on test failure (and rollback).
    """
    file_path = Path(file_path)
    bak_path = None
    try:
        # Backup
        bak_path = backup_file(file_path)
        log.info(f"Backed up {file_path} to {bak_path}")

        # Read content
        content = read_file(file_path)

        # Detect type if auto
        if config_type == 'auto':
            ext = file_path.suffix.lower()
            if ext == '.json':
                config_type = 'json'
            elif ext in ('.yaml', '.yml'):
                config_type = 'yaml'
            elif ext == '.ini':
                config_type = 'ini'
            elif ext == '.env':
                config_type = 'env'
            else:
                config_type = 'keyvalue'  # Fallback to key=value

        # Update based on type
        updated_content = content
        if config_type == 'json':
            if not isinstance(updates, dict):
                raise StringsError("For JSON updates must be dict of key_path->value")
            updated_content = _apply_updates_to_json_content(content, updates)
        elif config_type == 'yaml':
            if not isinstance(updates, dict):
                raise StringsError("For YAML updates must be dict of key_path->value")
            updated_content = _apply_updates_to_yaml_content(content, updates)
        elif config_type == 'ini':
            # support two forms: nested dict {section: {k:v}} or flat {'section.key': value}
            if all(isinstance(v, dict) for v in updates.values()):
                # nested form
                data = updates
                updated_content = content
                for section, items in data.items():
                    for k, v in items.items():
                        updated_content = update_ini(updated_content, section, k, str(v))
            else:
                # flat form
                updated_content = content
                for key, val in updates.items():
                    if '.' in key:
                        section, k = key.split('.', 1)
                        updated_content = update_ini(updated_content, section, k, str(val))
                    else:
                        # Unknown: append to DEFAULT or top-level
                        updated_content = update_key_value(updated_content, key, str(val))
        elif config_type == 'env':
            if not isinstance(updates, dict):
                raise StringsError("For env updates must be dict of key->value")
            updated_content = content
            for k, v in updates.items():
                updated_content = update_env(updated_content, k, str(v))
        elif config_type in ('nginx', 'keyvalue'):
            updated_content = content
            for key, val in updates.items():
                updated_content = update_key_value(updated_content, key, str(val))
        else:
            raise StringsError(f"Unsupported config_type: {config_type}")

        # Write updated
        write_file(file_path, updated_content)

        # Test if provided
        if test_cmd:
            # run() returns CompletedProcess
            res = run(test_cmd if isinstance(test_cmd, (str, list)) else str(test_cmd), capture=True)
            if res.returncode != 0:
                log.error(f"Test command failed (rc={res.returncode}): {res.stderr if hasattr(res, 'stderr') else ''}. Rolling back.")
                restore_file(file_path, bak_path)
                return False
            log.info(f"Test command succeeded: {test_cmd}")

        # Reload if provided
        if reload_cmd:
            run(reload_cmd if isinstance(reload_cmd, (str, list)) else str(reload_cmd), elevated=True)
            log.info(f"Reloaded with: {reload_cmd}")

        return True
    except Exception as e:
        log.error(f"Config update failed: {e}. Rolling back.")
        if bak_path is not None:
            try:
                restore_file(file_path, bak_path)
            except Exception as rexc:
                log.error(f"Failed to restore backup {bak_path}: {rexc}")
        raise StringsError(f"Config update failed: {e}") from e