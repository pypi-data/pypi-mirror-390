"""DataLab Python SDK.

A Python client for interacting with the DataLab API.
"""

from __future__ import annotations

import io
import json
import os
import time
from collections.abc import Iterable
from pathlib import Path
from typing import BinaryIO
from urllib.parse import urljoin

import pandas as pd
from tqdm.auto import tqdm

from .entry import Entries
from .gfhub import Client as _RustClient
from .gfhub import get_settings_py

__all__ = ["Client", "get_settings"]

# Load .env file if it exists
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv not installed, skip


def get_settings() -> tuple[str, str]:
    """Get settings from config files and environment variables.

    Returns:
        Tuple of (api_key, base_url) read from:
        - ~/.gdsfactory/gdsfactoryplus.toml (global)
        - pyproject.toml (local, base_url only)
        - Environment variables (GFP_API_KEY, GFH_BASE_URL)

    Priority: env vars > local > global (api_key only from global/env)
    """
    return get_settings_py()


class Client:
    """DataLab client for managing files, functions, pipelines, and tags.

    Args:
        base_url: The base URL of the DataLab server. If not provided, reads from
            settings (pyproject.toml or ~/.gdsfactory/gdsfactoryplus.toml).
        api_key: Optional API key for authentication. If not provided, reads from
            settings (only ~/.gdsfactory/gdsfactoryplus.toml, not local config).
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        """Initialize the DataLab client.

        Args:
            base_url: The base URL of the DataLab server. Falls back to settings.
            api_key: Optional API key. Falls back to settings.
        """
        # Get settings if not provided
        if base_url is None or api_key is None:
            settings_api_key, settings_base_url = get_settings()
            if base_url is None:
                base_url = settings_base_url
            if api_key is None and settings_api_key:
                api_key = settings_api_key

        self._base_url = base_url or "http://localhost:8080"
        self._client = _RustClient(base_url, api_key)

    @property
    def base_url(self) -> str:
        """Get the base URL of the DataLab server."""
        return self._base_url

    def url(self, *parts: str) -> str:
        """Get the full URL for a given path."""
        return urljoin(self._base_url, "/".join(parts))

    def add_file(
        self,
        data: str | Path | BinaryIO | pd.DataFrame,
        tags: Iterable[str] = (),
        *,
        filename: str | None = None,
    ) -> dict:
        """Upload a file to DataLab.

        Args:
            data: The data to upload. Can be:
                - str/Path: Path to a file to upload
                - BinaryIO: File-like object (e.g., io.BytesIO)
                - pandas.DataFrame: Will be converted to Parquet format
            tags: Optional list of tags to apply to the file. Tags can be simple names
                (e.g., "raw") or parameter tags with "key:value" format (e.g., "raw:3").
            filename: Optional filename to use on the server. Required when uploading
                from BinaryIO or DataFrame. Optional when uploading from a path
                (defaults to the actual filename).

        Returns:
            Dictionary containing the upload response with file metadata.

        Raises:
            RuntimeError: If the file upload fails.
            ValueError: If filename is not provided when uploading
                from BinaryIO or DataFrame.

        """
        tags_lst = None if not tags else [str(t) for t in tags]

        # Handle different input types
        if isinstance(data, (str, Path)):
            # Upload from file path
            path_obj = Path(data).resolve()
            if not path_obj.exists():
                msg = f"File not found: {path_obj}"
                raise FileNotFoundError(msg)

            if filename is not None:
                # Custom filename provided - read file and upload as bytes
                file_bytes = path_obj.read_bytes()
                mime_type = None  # Let server guess from filename
                return json.loads(
                    self._client.add_file_from_bytes(
                        file_bytes,
                        filename,
                        mime_type,
                        tags_lst,
                    )
                )
            # Use original filename
            path_str = str(path_obj)
            return json.loads(self._client.add_file(path_str, tags_lst))

        # Handle pandas DataFrame
        if isinstance(data, pd.DataFrame):
            if filename is None:
                msg = "filename parameter is required when uploading a DataFrame"
                raise ValueError(msg)
            # Convert DataFrame to Parquet bytes
            buffer = io.BytesIO()
            data.to_parquet(buffer, index=False)
            buffer.seek(0)
            file_bytes = buffer.read()
            mime_type = "application/octet-stream"

            # Ensure filename has .parquet extension
            if not filename.endswith(".parquet"):
                filename = f"{filename}.parquet"

            return json.loads(
                self._client.add_file_from_bytes(
                    file_bytes,
                    filename,
                    mime_type,
                    tags_lst,
                )
            )

        # Handle BinaryIO (file-like object)
        if hasattr(data, "read"):
            if filename is None:
                msg = "filename parameter is required when uploading a buffer"
                raise ValueError(msg)
            file_bytes = data.read()
            if isinstance(file_bytes, str):
                file_bytes = file_bytes.encode("utf-8")
            mime_type = None  # Let server guess from filename
            return json.loads(
                self._client.add_file_from_bytes(
                    file_bytes,
                    filename,
                    mime_type,
                    tags_lst,
                )
            )

        msg = f"Unsupported data type: {type(data)}"
        raise TypeError(msg)

    def list_functions(self) -> list[dict]:
        """List all functions in the organization.

        Returns:
            List of function dictionaries with id, name, parameters, etc.

        Raises:
            RuntimeError: If listing functions fails.
        """
        return json.loads(self._client.list_functions())

    def add_function(
        self,
        name: str,
        script: Path | str,
        *,
        update: bool = True,
    ) -> dict:
        """Add or update a Python function.

        Args:
            name: Name of the function.
            script: Either the Python script content (if it contains newlines)
                or a path to a Python script file. The function must have a valid
                signature with `main(path: Path, /, *, kwargs) -> Path`.
            update: If True, updates the function if it already exists. If False,
                raises an error on conflict. Defaults to True.

        Returns:
            Dictionary containing the function response with metadata.

        Raises:
            RuntimeError: If the function validation or upload fails.
        """
        script_or_path = str(script.resolve()) if isinstance(script, Path) else script
        if "\n" not in script_or_path:
            script_or_path = str(Path(script_or_path).resolve())
        return json.loads(
            self._client.add_function(str(name), script_or_path, bool(update))
        )

    def add_pipeline(
        self,
        name: str,
        schema: dict | str,
        *,
        update: bool = True,
    ) -> dict:
        """Add or update a pipeline.

        Args:
            name: Name of the pipeline.
            schema: Either a dict or JSON string containing the pipeline schema.
                The schema uses JsonNode/JsonEdge format:
                - nodes: List of nodes with name, type, and settings
                - edges: List of edges connecting nodes
            update: If True, updates the pipeline if it already exists. If False,
                raises an error on conflict. Defaults to True.

        Returns:
            Dictionary containing the pipeline response with metadata.

        Raises:
            RuntimeError: If the pipeline creation or update fails.

        Example:
            >>> schema = {
            ...     "nodes": [
            ...         {
            ...             "name": "to_parquet",
            ...             "type": "function",
            ...             "settings": {
            ...                 "function": "csv2parquet",
            ...                 "settings": {}
            ...             }
            ...         }
            ...     ],
            ...     "edges": []
            ... }
            >>> client.add_pipeline("csv_converter", schema)
        """
        # Parse schema if it's a string
        if isinstance(schema, str):
            schema = json.loads(schema)

        # Resolve function names to IDs for function nodes
        if "nodes" in schema:
            functions = self.list_functions()
            function_name_to_id = {f["name"]: f["id"] for f in functions}

            for node in schema["nodes"]:
                if node.get("type") == "function" and node.get("config"):
                    config = node["config"]
                    if "function" in config:
                        function_name = config["function"]
                        if function_name in function_name_to_id:
                            # Replace function name with ID
                            config["id"] = function_name_to_id[function_name]
                            del config["function"]
                        else:
                            msg = f"Function '{function_name}' not found"
                            raise ValueError(msg)

        # Convert to JSON string
        schema_str = json.dumps(schema)

        return json.loads(self._client.add_pipeline(str(name), schema_str, bool(update)))

    def enable_pipeline(self, pipeline_id: str) -> None:
        """Enable a pipeline.

        Args:
            pipeline_id: ID of the pipeline.

        Raises:
            RuntimeError: If the operation fails.

        Example:
            >>> client.enable_pipeline("pipeline-uuid")
        """
        self._client.enable_pipeline(str(pipeline_id))

    def disable_pipeline(self, pipeline_id: str) -> None:
        """Disable a pipeline.

        Args:
            pipeline_id: ID of the pipeline.

        Raises:
            RuntimeError: If the operation fails.

        Example:
            >>> client.disable_pipeline("pipeline-uuid")
        """
        self._client.disable_pipeline(str(pipeline_id))

    def _normalize_tag_arrays(self, schema: dict) -> dict:
        """Convert single-entry dicts in tag arrays to "key: value" strings.

        When YAML like "- wafer: ${step0,0}" is parsed, it becomes {"wafer": "${step0,0}"}.
        We need to convert these back to "wafer: ${step0,0}" strings for the backend.
        """
        for tags_key in ["input_tags", "output_tags"]:
            if tags_key in schema and isinstance(schema[tags_key], dict):
                for port, tags in schema[tags_key].items():
                    if isinstance(tags, list):
                        normalized = []
                        for tag in tags:
                            if isinstance(tag, dict) and len(tag) == 1:
                                # Single-entry dict: convert to "key: value" string
                                key, value = next(iter(tag.items()))
                                normalized.append(f"{key}: {value}")
                            else:
                                # Keep as-is (string or other type)
                                normalized.append(tag)
                        schema[tags_key][port] = normalized
        return schema

    def add_tag(
        self,
        name: str,
        color: str,
        *,
        update: bool = True,
    ) -> dict:
        """Add or update a tag.

        Args:
            name: Name of the tag.
            color: Hex color code for the tag (e.g., "#ef4444").
            update: If True, updates the tag if it already exists. If False,
                raises an error on conflict. Defaults to True.

        Returns:
            Dictionary containing the tag response with metadata.

        Raises:
            RuntimeError: If the tag creation or update fails.
        """
        return json.loads(self._client.add_tag(str(name), str(color), bool(update)))

    def query_files(
        self,
        *,
        name: str | None = None,
        tags: Iterable[str] = (),
    ) -> Entries:
        """Query files by name pattern and/or tags.

        Args:
            name: Optional filename pattern to filter by. Supports glob patterns:
                - Exact match: "lattice.gds" (case-insensitive)
                - Glob pattern: "*.csv", "data*.parquet", "lattice*"
            tags: Optional list of tags to filter by. Files must have ALL given tags.
                Supports wildcards (e.g., "wafer_id:*") to match any parameter value.

        Returns:
            Dictionary containing a list of matching files with their metadata.

        Raises:
            RuntimeError: If the query fails.

        Example:
            >>> # Find all CSV files by extension tag
            >>> client.query_files(tags=[".csv"])
            >>>
            >>> # Find files by exact name (case-insensitive)
            >>> client.query_files(name="lattice.gds")
            >>>
            >>> # Find files by glob pattern
            >>> client.query_files(name="*.csv")
            >>> client.query_files(name="data*.parquet")
            >>>
            >>> # Find files with specific parameter values
            >>> client.query_files(tags=["wafer_id:wafer1", ".parquet"])
            >>>
            >>> # Combine name pattern and tags
            >>> client.query_files(name="*.parquet", tags=["wafer_id:*"])
            >>>
            >>> # Get all files
            >>> client.query_files()
        """
        tags_list = None if not tags else [str(t) for t in tags]
        entries = Entries(json.loads(self._client.query_files(name, tags_list)))
        for entry in entries:
            if "tags" not in entry:
                entry["tags"] = {}
            else:
                # entry names are unique, so this is more convenient:
                entry["tags"] = {t["name"]: t for t in entry["tags"]}
        return entries

    def add_cascaded_pipeline(
        self,
        name: str,
        layers: list[list[dict] | dict],
    ) -> dict:
        """Create a cascaded pipeline with layered nodes.

        Each node in a layer connects to all nodes in the next layer.

        Args:
            name: Name of the pipeline.
            layers: List of layers. Each layer can be:
                - A single node dict: {"name": "...", "type": "...", "config": {...}}
                - A list of node dicts
                The first output (output 0) of each node in layer N connects to
                the first input (input 0) of each node in layer N+1.

        Returns:
            Dictionary containing the pipeline response with metadata.

        Raises:
            RuntimeError: If the pipeline creation or update fails.
            ValueError: If no layers are provided.

        Example:
            >>> layers = [
            ...     {"name": "on_file_upload", "type": "on_file_upload", "config": {}},
            ...     {"name": "load", "type": "load", "config": {}},
            ...     {"name": "csv2parquet", "type": "function", "config": {"function": "csv2parquet", "kwargs": {}}},
            ...     {"name": "parquet2json", "type": "function", "config": {"function": "parquet2json", "kwargs": {}}},
            ...     {"name": "save", "type": "save", "config": {}},
            ... ]
            >>> client.add_cascaded_pipeline("csv2json", layers)
        """
        if not layers:
            msg = "At least one layer must be provided"
            raise ValueError(msg)

        # Normalize layers - ensure each is a list
        normalized_layers: list[list[dict]] = []
        for layer in layers:
            if isinstance(layer, dict):
                normalized_layers.append([layer])
            elif isinstance(layer, list):
                normalized_layers.append(layer)
            else:
                msg = f"Layer must be a dict or list of dicts, got {type(layer)}"
                raise TypeError(msg)

        # Build nodes list - flatten all layers
        nodes = []
        for layer in normalized_layers:
            nodes.extend(layer)

        # Resolve function names to IDs for function nodes
        functions = self.list_functions()
        function_name_to_id = {f["name"]: f["id"] for f in functions}

        for node in nodes:
            if node.get("type") == "function" and node.get("config"):
                config = node["config"]
                if "function" in config:
                    function_name = config["function"]
                    if function_name in function_name_to_id:
                        # Replace function name with ID
                        config["id"] = function_name_to_id[function_name]
                        del config["function"]
                    else:
                        msg = f"Function '{function_name}' not found"
                        raise ValueError(msg)

        # Build edges - connect each node in layer N to all nodes in layer N+1
        edges = []
        for i in range(len(normalized_layers) - 1):
            current_layer = normalized_layers[i]
            next_layer = normalized_layers[i + 1]
            for source_node in current_layer:
                for target_node in next_layer:
                    edges.append(
                        {
                            "source": {"node": source_node["name"], "output": 0},
                            "target": {"node": target_node["name"], "input": 0},
                        }
                    )

        # Create schema
        schema = {
            "nodes": nodes,
            "edges": edges,
        }

        return self.add_pipeline(name, schema)

    def download_file(
        self,
        upload_id: str,
        output: str | Path | BinaryIO | None = None,
    ) -> io.BytesIO | None:
        """Download a file by upload ID.

        Args:
            upload_id: ID of the file to download.
            output: Where to write the file. Can be:
                - str/Path: File path to write to
                - File handle opened in binary mode (e.g., open('file', 'wb'))
                - io.BytesIO: BytesIO buffer to write to
                - None: Return new BytesIO buffer with file contents

        Returns:
            None if output is a path or file handle, io.BytesIO if output is None.

        Raises:
            RuntimeError: If the download fails.

        Example:
            >>> # Download to file path
            >>> client.download_file("upload_123", "downloaded_file.csv")
            >>>
            >>> # Download to file handle
            >>> with open("output.csv", "wb") as f:
            ...     client.download_file("upload_123", f)
            >>>
            >>> # Download to BytesIO
            >>> import io
            >>> buffer = io.BytesIO()
            >>> client.download_file("upload_123", buffer)
            >>> buffer.seek(0)
            >>>
            >>> # Get BytesIO directly
            >>> buffer = client.download_file("upload_123")
            >>> data = buffer.read()
        """
        file_bytes = bytes(self._client.download_file_bytes(str(upload_id)))

        if output is None:
            return io.BytesIO(file_bytes)
        if isinstance(output, (str, Path)):
            output_path = Path(output).resolve()
            with output_path.open("wb") as f:
                f.write(file_bytes)
            return None

        # File handle or BytesIO
        output.write(file_bytes)
        return None

    def trigger_pipeline(
        self,
        pipeline_name: str,
        upload_ids: str | Iterable[str],
    ) -> dict:
        """Trigger a pipeline manually with one or more files.

        Args:
            pipeline_name: Name of the pipeline to trigger.
            upload_ids: Single upload id or list of upload IDs to process.

        Returns:
            Dictionary containing the job metadata with job ID.

        Raises:
            RuntimeError: If the pipeline trigger fails or pipeline not found.

        Example:
            >>> # Trigger with single file
            >>> job = client.trigger_pipeline("csv2json", "upload_123")
            >>> print(job["id"])  # Job ID
            >>>
            >>> # Trigger with multiple files
            >>> job = client.trigger_pipeline("csv2json", ["upload_1", "upload_2"])
            >>> print(job["id"])  # Job ID
        """
        if isinstance(upload_ids, str):
            upload_ids = [upload_ids]
        return json.loads(self._client.trigger_pipeline(str(pipeline_name), upload_ids))

    def get_job(self, job_id: str) -> dict:
        """Get job details by ID.

        Args:
            job_id: The job ID to retrieve

        Returns:
            Job details including status, inputs, outputs, timestamps, etc.

        Example:
            >>> job = client.get_job("job_123")
            >>> print(job["status"])  # QUEUED, RUNNING, SUCCESS, or FAILED
            >>> print(job["pipeline_name"])  # Name of the pipeline
        """
        return json.loads(self._client.get_job(str(job_id)))

    def wait_for_job(
        self,
        job_id: str,
        poll_interval: float = 1.0,
    ) -> dict:
        """Wait for a job to complete (SUCCESS or FAILED status).

        Args:
            job_id: The job ID to wait for
            timeout: Maximum seconds to wait (default: 300)
            poll_interval: Seconds between polls (default: 1.0)

        Returns:
            Final job details with status SUCCESS or FAILED

        Raises:
            RuntimeError: If job is not found

        Example:
            >>> job = client.trigger_pipeline("csv2json", "upload_123")
            >>> final_job = client.wait_for_job(job["id"])
            >>> print(final_job["status"])  # SUCCESS or FAILED
            >>> if final_job["status"] == "SUCCESS":
            >>>     print(final_job["output_filenames"])
        """
        while True:
            job = self.get_job(job_id)
            status = job["status"]
            if status in ("SUCCESS", "FAILED"):
                return job
            time.sleep(poll_interval)

    def wait_for_jobs(
        self, job_ids: list[str], poll_interval: float = 1.0
    ) -> list[dict]:
        """Wait for multiple jobs to complete.

        Args:
            job_ids: List of job IDs to wait for
            poll_interval: Seconds between polling cycles (default: 1.0)

        Returns:
            List of final job details with status SUCCESS or FAILED

        Raises:
            RuntimeError: If any job is not found

        Example:
            >>> jobs = client.wait_for_jobs(["job_123", "job_456"])
            >>> for job in jobs:
            >>>     print(job["status"])  # SUCCESS or FAILED
        """
        completed = {}
        remaining = set(job_ids)

        with tqdm(total=len(job_ids)) as pbar:
            while remaining:
                # Check all remaining jobs in one cycle
                for job_id in list(remaining):
                    job = self.get_job(job_id)
                    status = job["status"]
                    if status in ("success", "failed"):
                        completed[job_id] = job
                        remaining.remove(job_id)
                        pbar.update(1)

                # Sleep once per cycle, not per job
                if remaining:
                    time.sleep(poll_interval)

        # Return in original order
        return [completed[job_id] for job_id in job_ids]
