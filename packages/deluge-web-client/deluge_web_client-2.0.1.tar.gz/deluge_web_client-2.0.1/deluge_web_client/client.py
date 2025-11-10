import base64
import re
from collections.abc import Iterable
from os import PathLike
from pathlib import Path
from typing import Any, Optional, Union
from urllib.parse import urlparse

import niquests

from deluge_web_client.exceptions import DelugeWebClientError
from deluge_web_client.schema import Response, TorrentOptions


class DelugeWebClient:
    HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

    __slots__ = (
        "session",
        "url",
        "password",
        "daemon_port",
        "_base_url",
        "_request_id",
    )

    def __init__(self, url: str, password: str, daemon_port: int = 58846) -> None:
        self.session = niquests.Session()
        self.url = self._build_url(url)
        self.password = password
        self.daemon_port = daemon_port

        self._base_url = self._get_base_url(self.url)
        self._request_id = 0

    def __enter__(self) -> "DelugeWebClient":
        """Login and connect to client while using with statement."""
        self.login()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """End of with statement, closes the session."""
        self.close_session()

    def login(self, timeout: int = 30) -> Response:
        """
        Log in to Web UI and connect to the first available host.

        Args:
            timeout (int): Timeout for the login and connection attempts.

        Returns:
            Response: A summary response indicating the success or failure of the login and connection attempts.
        """
        login_response = self._attempt_login(timeout)
        if not login_response.result:
            return self._create_failure_response("Login failed")

        # check if already connected
        if self._is_connected(timeout):
            return Response(result=True, error=None)

        # attempt to connect to a host
        return self._connect_to_first_host(timeout)

    def _attempt_login(self, timeout: int) -> Response:
        """Attempt to log in to the Web UI."""
        login_payload = {
            "method": "auth.login",
            "params": [self.password],
        }
        return self.execute_call(login_payload, timeout=timeout)

    def _is_connected(self, timeout: int) -> bool:
        """Check if already connected to the Web UI."""
        return True if self.check_connected(timeout).result else False

    def _connect_to_first_host(self, timeout: int) -> Response:
        """Attempt to connect to the first available host."""
        hosts = self.get_hosts()

        if isinstance(hosts.result, list) and hosts.result:
            host_info = hosts.result[0]
            if isinstance(host_info, list) and host_info:
                host_id = host_info[0]
                connect_response = self.connect_to_host(host_id)
                if connect_response.result:
                    return self.check_connected(timeout)

        return self._create_failure_response("Failed to connect to host")

    def _create_failure_response(self, error_message: str) -> Response:
        """Helper method to create a failure response."""
        return Response(result=False, error=error_message)

    def close_session(self) -> None:
        """
        Closes the `DelugeWebClient` session.
        This is handled automatically
        when `DelugeWebClient` is used in a context manager.
        """
        self.session.close()

    def _get_next_id(self) -> int:
        """Generate next request ID."""
        self._request_id += 1
        return self._request_id

    def disconnect(self, timeout: int = 30) -> Response:
        """
        Disconnects from the Web UI.

        Note: This disconnects from all of your logged in instances outside of this program as well
        that is tied to that user/password. Only use this IF needed not on each call.
        """
        payload = {
            "method": "web.disconnect",
            "params": [],
        }
        return self.execute_call(payload, timeout=timeout)

    def upload_torrent(
        self,
        torrent_path: Union[PathLike[str], str, Path],
        torrent_options: TorrentOptions,
        timeout: int = 30,
    ) -> Response:
        """
        Opens the torrent path building out the payload as needed to
        upload a single torrent to the client.

        Args:
            torrent_path (PathLike[str], str, Path): Path to torrent file (example.torrent).
            torrent_options (TorrentOptions): Torrent options.
            timeout (int): Time to timeout.

        Returns:
            Response: Response object.
        """
        torrent_path = Path(torrent_path)
        with open(torrent_path, "rb") as tf:
            params = [
                str(torrent_path),
                str(base64.b64encode(tf.read()), encoding="utf-8"),
                torrent_options.to_dict(),
            ]
            payload = {
                "method": "core.add_torrent_file",
                "params": params,
            }
            return self._upload_helper(payload, torrent_options.label, timeout)

    def upload_torrents(
        self,
        torrents: Iterable[Union[PathLike[str], str, Path]],
        torrent_options: TorrentOptions,
        timeout: int = 30,
    ) -> dict[str, Response]:
        """
        Uploads multiple torrents.

        Args:
            torrents (Iterable[Union[PathLike[str], str, Path]]): A list or other iterable of torrent file paths.
            torrent_options (TorrentOptions): Torrent options.
                You should avoid using `name` in `TorrentOptions` when uploading multiple torrents.
            timeout (int): Time to timeout.

        Returns:
            dict[str, Response]: A dictionary of torrent name and Response objects for each torrent.
        """
        results = {}
        for torrent_path in torrents:
            torrent_path = Path(torrent_path)
            try:
                response = self.upload_torrent(
                    torrent_path,
                    torrent_options=torrent_options,
                    timeout=timeout,
                )
                results[torrent_path.stem] = response
            except Exception as e:
                raise DelugeWebClientError(
                    f"Failed to upload {torrent_path.name}:\n{e}"
                )

        return results

    def add_torrent_magnet(
        self,
        uri: str,
        torrent_options: TorrentOptions,
        timeout: int = 30,
    ):
        """
        Adds a torrent from a magnet link.

        Args:
            uri (str): Magnet input.
            torrent_options (TorrentOptions): Torrent options.
            timeout (int): Time to timeout.

        Returns:
            Response: Response object.

        """
        payload = {
            "method": "core.add_torrent_magnet",
            "params": [str(uri), torrent_options.to_dict()],
        }
        return self._upload_helper(payload, torrent_options.label, timeout)

    def add_torrent_url(
        self,
        url: str,
        torrent_options: TorrentOptions,
        timeout: int = 30,
    ):
        """
        Adds a torrent from a URL.

        Args:
            url (str): URL input.
            torrent_options (TorrentOptions): Torrent options.
            timeout (int): Time to timeout.

        Returns:
            Response: Response object.
        """
        payload = {
            "method": "core.add_torrent_url",
            "params": [str(url), torrent_options.to_dict()],
        }
        return self._upload_helper(payload, torrent_options.label, timeout)

    def _upload_helper(
        self, payload: dict, label: Optional[str], timeout: int
    ) -> Response:
        """Helper method for uploading torrents (file, magnet, URL).

        Handles torrent addition with proper error parsing and special handling
        for torrents that already exist in the session (returns existing hash
        as a successful idempotent result).

        Args:
            payload: JSON-RPC payload to send
            label: Optional label to apply to the torrent
            timeout: Request timeout in seconds

        Returns:
            Response: Contains info_hash on success, None on error

        Raises:
            DelugeWebClientError: On upload failures (except duplicate torrents)
        """
        # assign a unique id per request
        payload["id"] = self._get_next_id()

        with self.session.post(
            self.url, headers=self.HEADERS, json=payload, timeout=timeout
        ) as response:
            # parse response JSON once
            try:
                data = response.json()
            except Exception:
                body_preview = response.text[:500] if response.text else "(empty)"
                raise DelugeWebClientError(
                    f"Invalid JSON response. Status: {response.status_code}, "
                    f"Reason: {response.reason}, Body: {body_preview}"
                )

            # success path: no error in response
            err = data.get("error")
            if response.ok and not err:
                info_hash = str(data["result"])
                if label:
                    self._apply_label(info_hash, label, timeout)
                return Response(result=info_hash, message="Torrent added successfully")

            # parse error to extract useful information
            parsed = self._parse_deluge_error(err)

            # torrent already exists in session, return existing hash as success
            parsed_class = parsed.get("class")
            if isinstance(parsed_class, str) and parsed_class.endswith(
                "AddTorrentError"
            ):
                info_hash = parsed.get("info_hash")
                if info_hash:
                    return Response(result=info_hash, message="Torrent already exists")

            # all other errors: raise with parsed information
            error_msg = parsed.get("message") or "Unknown error"
            raise DelugeWebClientError(
                f"Failed to add torrent. Status: {response.status_code}, "
                f"Reason: {response.reason}, Error: {error_msg}"
            )

    def _apply_label(
        self, info_hash: str, label: str, timeout: int
    ) -> tuple[Response, Response]:
        """
        Used internally to add and apply labels as needed for
        the `upload_torrent` method

        Args:
            info_hash (str): Info has of torrent.
            label (str): Label to apply it to (automatically set to lowercase internally).
            timeout (int): Time to timeout.

        Returns:
            tuple (bool, bool): add_label(), set_label().
        """
        add_label = self.add_label(label, timeout)
        set_label = self.set_label(info_hash, label, timeout)
        return add_label, set_label

    def get_free_space(
        self, path: Optional[Union[str, PathLike[str]]] = None, timeout: int = 30
    ) -> Response:
        """Gets free space."""
        payload = {
            "method": "core.get_free_space",
            "params": [str(path)] if path else [],
        }
        return self.execute_call(payload, timeout=timeout)

    def get_path_size(
        self, path: Optional[Union[str, PathLike[str]]] = None, timeout: int = 30
    ) -> Response:
        """
        Gets path size.

        Returns the size of the file or folder `path` and `-1` if the path is
        unaccessible (non-existent or insufficient privs)
        """
        payload = {
            "method": "core.get_path_size",
            "params": [str(path)] if path else [],
        }
        return self.execute_call(payload, timeout=timeout)

    def get_labels(self, timeout: int = 30) -> Response:
        """Gets defined labels."""
        payload = {
            "method": "label.get_labels",
            "params": [],
        }
        return self.execute_call(payload, timeout=timeout)

    def set_label(self, info_hash: str, label: str, timeout: int = 30) -> Response:
        """Sets the label for a specific torrent."""
        payload = {
            "method": "label.set_torrent",
            "params": [info_hash, label.lower()],
        }
        return self.execute_call(payload, timeout=timeout)

    def add_label(self, label: str, timeout: int = 30) -> Response:
        """Adds a label to the client, ignoring labels if they already exist."""
        payload = {
            "method": "label.add",
            "params": [label.lower()],
        }
        response = self.execute_call(payload, handle_error=False, timeout=timeout)
        if response.error is None:
            return response

        if isinstance(
            response.error, dict
        ) and "Label already exists" in response.error.get("message", ""):
            return response

        raise DelugeWebClientError(f"Error adding label:\n{response.error}")

    def get_libtorrent_version(self, timeout: int = 30) -> Response:
        """Gets libtorrent version."""
        payload = {
            "method": "core.get_libtorrent_version",
            "params": [],
        }
        return self.execute_call(payload, timeout=timeout)

    def get_listen_port(self, timeout: int = 30) -> Response:
        """Gets listen port."""
        payload = {
            "method": "core.get_listen_port",
            "params": [],
        }
        return self.execute_call(payload, timeout=timeout)

    def get_plugins(self, timeout: int = 30) -> Response:
        """Gets plugins."""
        payload = {
            "method": "web.get_plugins",
            "params": [],
        }
        return self.execute_call(payload, timeout=timeout)

    def get_torrent_files(self, torrent_id: str, timeout: int = 30) -> Response:
        """Gets the files for a torrent in tree format."""
        payload = {
            "method": "web.get_torrent_files",
            "params": [torrent_id],
        }
        return self.execute_call(payload, timeout=timeout)

    def get_torrent_status(
        self,
        torrent_id: str,
        keys: list[str] = [],
        diff: bool = False,
        timeout: int = 30,
    ) -> Response:
        """
        Gets the status for a torrent.

        Args:
            torrent_id (str): Torrent hash of for a single torrent.
            keys (list[str]): List of specific torrent's property keys to fetch.
            diff (bool): Whether to return the status difference.
            timeout (int): Time to timeout for the call.

        Returns:
            Response: The response from the API call.
        """
        payload = {
            "method": "core.get_torrent_status",
            "params": [torrent_id, keys, diff],
        }
        return self.execute_call(payload, timeout=timeout)

    def get_torrents_status(
        self,
        filter_dict: dict = {},
        keys: list[str] = [],
        diff: bool = False,
        timeout: int = 30,
    ) -> Response:
        """
        Gets the status for multiple torrents, returns all torrents,
        optionally filtered by filter_dict.

        Args:
            filter_dict (dict): Filtering criteria for torrents.
            keys (list[str]): List of specific torrents' property keys to fetch.
            diff (bool): Whether to return the status difference.
            timeout (int): Time to timeout for the call.

        Returns:
            Response: The response from the API call.

        Example `filter_dict`:
        >>> {"id": ["tid", "tid"]}
        ... or
        >>> state = str(TorrentState.SEEDING)
        >>> {"state": state, "id": ["tid", "tid"]}
        """
        payload = {
            "method": "core.get_torrents_status",
            "params": [filter_dict, keys, diff],
        }
        return self.execute_call(payload, timeout=timeout)

    def check_connected(self, timeout: int = 30) -> Response:
        """
        Use the `web.connected` method to get a boolean response if the Web UI is
        connected to a deluged host.
        """
        payload = {
            "method": "web.connected",
            "params": [],
        }
        return self.execute_call(payload, timeout=timeout)

    def get_hosts(self, timeout: int = 30) -> Response:
        """
        Returns hosts we're connected to currently.

        Example output:
            ```python
            Response(result=[['host_hash', '127.0.0.1', 58846, 'localclient'], ...], error=None)
            ```
        """
        payload = {
            "method": "web.get_hosts",
            "params": [],
        }
        return self.execute_call(payload, timeout=timeout)

    def get_host_status(self, host_id: str, timeout: int = 30) -> Response:
        """Get the deluged host status `<hostID>`."""
        payload = {
            "method": "web.get_host_status",
            "params": [host_id],
        }
        return self.execute_call(payload, timeout=timeout)

    def start_daemon(self, timeout: int = 30) -> Response:
        """
        Start local daemon.

        Response `result` and `error` will both be `None` if successfully started.
        """
        payload = {
            "method": "web.start_daemon",
            "params": [self.daemon_port],
        }
        return self.execute_call(payload, timeout=timeout)

    def stop_daemon(self, host_id: str, timeout: int = 30) -> Response:
        """
        Stop local daemon.

        Response `result` and `error` will both be `None` if successfully stopped.
        """
        payload = {
            "method": "web.stop_daemon",
            "params": [host_id],
        }
        return self.execute_call(payload, timeout=timeout)

    def update_ui(
        self, keys: list[str] = [], filter_dict: dict = {}, timeout: int = 30
    ) -> Response:
        """Gathers information to update the UI (this could be useful to gather info)."""
        payload = {
            "method": "web.update_ui",
            "params": [keys, filter_dict],
        }
        return self.execute_call(payload, timeout=timeout)

    def add_host(
        self,
        username: str,
        password: str,
        timeout: int = 30,
    ) -> Response:
        """
        Add a host to the host list.

        If successful payload will return a list with a bool and the host_id. Otherwise the
        payload will return an error message.

            Example output:
            ```python
            new_host = Response(result=[True, 'f3558dd405924807a0c5e5a057f7a496'], error=None)
            ```

        Example usage:
            ```python
            new_host = client.add_host("test", "test")
            if new_host.result:
                host_id = new_host.result[1]
            ```
        """
        payload = {
            "method": "web.add_host",
            "params": ["127.0.0.1", self.daemon_port, username, password],
        }
        return self.execute_call(payload, timeout=timeout)

    def remove_host(
        self,
        host_id: str,
        timeout: int = 30,
    ) -> Response:
        """
        Remove a host from the host list.

        If successful `result` will return `True`. Otherwise, will return `False`.
        """
        payload = {
            "method": "web.remove_host",
            "params": [host_id],
        }
        return self.execute_call(payload, timeout=timeout)

    def edit_host(
        self,
        host_id: str,
        username: str,
        password: str,
        timeout: int = 30,
    ) -> Response:
        """
        Edit a host in the hostlist.

        This is used to set or update the username/password that the Web UI
        will use when connecting to a deluged daemon.

        `result` will return `True` if successful.
        """
        payload = {
            "method": "web.edit_host",
            "params": [host_id, "127.0.0.1", self.daemon_port, username, password],
        }
        return self.execute_call(payload, timeout=timeout)

    def find_host_id_by_name(
        self,
        host_name: str,
        timeout: int = 30,
    ) -> Response:
        """
        Find a host ID by its name.

        Example output:
            ```python
            host_id = client.find_host_id_by_name("localclient")
            if host_id.result:
                print(f"Found host ID: {host_id.result}")
            ```
        """
        host_list = self.get_hosts(timeout)
        # if no hosts
        if not host_list.result:
            return Response(result=True, error=None)

        # let's search for the host
        if isinstance(host_list.result, list):
            for host in host_list.result:
                try:
                    get_host_hash = host[0]
                    get_host_name = host[3]
                    if get_host_name == host_name:
                        return Response(result=get_host_hash, error=None)
                except IndexError:
                    continue

        # not found
        return Response(result=None, error=None)

    def connect_to_host(self, host_id: str, timeout: int = 30) -> Response:
        """To connect to deluged with `<hostID>`."""
        payload = {
            "method": "web.connect",
            "params": [host_id],
        }
        return self.execute_call(payload, timeout=timeout)

    def test_listen_port(self, timeout: int = 30) -> bool:
        """
        Checks if the active port is open.

        Returns:
            bool: If active port is opened or closed.
        """
        payload = {
            "method": "core.test_listen_port",
            "params": [],
        }
        check_port = self.execute_call(payload, timeout=timeout)
        if check_port.result is not None:
            return True
        return False

    def pause_torrent(self, torrent_id: str, timeout: int = 30) -> Response:
        """Pause a specific torrent."""
        payload = {
            "method": "core.pause_torrent",
            "params": [torrent_id],
        }
        return self.execute_call(payload, timeout=timeout)

    def pause_torrents(self, torrent_ids: list, timeout: int = 30) -> Response:
        """Pause a list of torrents."""
        payload = {
            "method": "core.pause_torrents",
            "params": [torrent_ids],
        }
        return self.execute_call(payload, timeout=timeout)

    def remove_torrent(
        self, torrent_id: str, remove_data: bool = False, timeout: int = 30
    ) -> Response:
        """Removes a specific torrent."""
        payload = {
            "method": "core.remove_torrent",
            "params": [torrent_id, remove_data],
        }
        return self.execute_call(payload, timeout=timeout)

    def remove_torrents(
        self, torrent_ids: list, remove_data: bool = False, timeout: int = 30
    ) -> Response:
        """Removes a list of torrents."""
        payload = {
            "method": "core.remove_torrents",
            "params": [torrent_ids, remove_data],
        }
        return self.execute_call(payload, timeout=timeout)

    def resume_torrent(self, torrent_id: str, timeout: int = 30) -> Response:
        """Resumes a specific torrent."""
        payload = {
            "method": "core.resume_torrent",
            "params": [torrent_id],
        }
        return self.execute_call(payload, timeout=timeout)

    def resume_torrents(self, torrent_ids: list, timeout: int = 30) -> Response:
        """Resumes a list of torrents."""
        payload = {
            "method": "core.resume_torrents",
            "params": [torrent_ids],
        }
        return self.execute_call(payload, timeout=timeout)

    def set_torrent_trackers(
        self, torrent_id: str, trackers: list[dict[str, Any]], timeout: int = 30
    ) -> Response:
        """Sets a torrents tracker list. Trackers will be ``[{'url', 'tier'}]``."""
        payload = {
            "method": "core.set_torrent_trackers",
            "params": [torrent_id, trackers],
        }
        return self.execute_call(payload, timeout=timeout)

    def execute_call(
        self, payload: dict, handle_error: bool = True, timeout: int = 30
    ) -> Response:
        """
        Helper method to execute most calls to the Web UI as needed.

        Args:
            payload (dict): Payload object to be called.
            handle_error (bool, optional): Handle errors here or allow the caller to handle
                the error. Defaults to True.
            timeout (int): Time to timeout.

        Returns:
            Response: Response object for each call.
        """
        # assign a unique id per request
        payload["id"] = self._get_next_id()

        with self.session.post(
            self.url, headers=self.HEADERS, json=payload, timeout=timeout
        ) as response:
            # parse response JSON once
            try:
                response_json = response.json()
            except Exception:
                body_preview = response.text[:500] if response.text else "(empty)"
                raise DelugeWebClientError(
                    f"Invalid JSON response. Status: {response.status_code}, "
                    f"Reason: {response.reason}, Body: {body_preview}"
                )

            if response.ok:
                # normalize the error field using our parser
                error_raw = response_json.get("error")
                parsed_error = (
                    self._parse_deluge_error(error_raw) if error_raw else None
                )

                data = Response(
                    result=response_json.get("result"),
                    error=self._normalize_exception(error_raw),
                )

                if handle_error and data.error:
                    # include parsed error info in the exception message
                    error_msg = (
                        parsed_error.get("message") if parsed_error else str(data.error)
                    )
                    raise DelugeWebClientError(
                        f"RPC Error - Method: {payload.get('method', 'unknown')}, "
                        f"Error: {error_msg}"
                    )
                return data
            else:
                raise DelugeWebClientError(
                    f"HTTP Error - Status: {response.status_code}, "
                    f"Reason: {response.reason}, Method: {payload.get('method', 'unknown')}"
                )

    @staticmethod
    def _normalize_exception(exc_str: Any) -> Union[str, Any]:
        """
        Removes the un-needed ending square bracket and stripping extra white
        space if input is a string.
        """
        if isinstance(exc_str, str):
            return exc_str.rstrip("]").strip()
        else:
            return exc_str

    @staticmethod
    def _build_url(url: str) -> str:
        """Automatically fixes URLs as needed to access the JSON API endpoint."""
        if not url.endswith("/"):
            url += "/"

        if "json" not in url:
            url += "json/"

        return url.rstrip("/")

    @staticmethod
    def _get_base_url(url: str) -> str:
        """Returns the base URL."""
        parsed_url = urlparse(url)
        return f"{parsed_url.scheme}://{parsed_url.netloc}"

    @staticmethod
    def _parse_deluge_error(err: Any) -> dict[str, Optional[str]]:
        """Parse Deluge error (dict or string) and extract useful information.

        Deluge's JSON-RPC API returns errors in multiple formats:
        - Structured dict with 'message' and 'code' keys
        - Stringified Twisted Failure objects containing exception class and message
        - Plain strings

        This helper normalizes all formats and extracts:
        - Exception class name (e.g., 'deluge.error.AddTorrentError')
        - Human-readable message
        - Info hash (40 hex chars) if present in the message
        - Raw error for debugging

        Args:
            err: The error value from JSON-RPC response (dict, string, or None)

        Returns:
            dict: Parsed error with keys 'class', 'message', 'info_hash', 'raw'
        """
        parsed: dict[str, Optional[str]] = {
            "class": None,
            "message": None,
            "info_hash": None,
            "raw": None,
        }

        if not err:
            return parsed

        # handle structured dict errors (e.g., JSONException, auth errors)
        if isinstance(err, dict):
            parsed["raw"] = str(err)
            msg = err.get("message") or err.get("msg") or str(err)
            parsed["message"] = msg
            # check if there's a 'class' key in the dict
            parsed["class"] = err.get("class")

            # if no explicit class, try to extract from the message string
            # (Twisted Failures are often in dict with stringified message)
            if not parsed["class"] and msg:
                match = re.search(r"<class '([^']+)'>:\s*(.+)", msg, re.DOTALL)
                if match:
                    parsed["class"] = match.group(1).strip()
        else:
            # handle stringified Failure or plain strings
            err_str = str(err)
            parsed["raw"] = err_str

            # try to extract exception class and message from Twisted Failure format:
            # "Failure: [Failure instance: ... <class 'deluge.error.SomeError'>: message ...]"
            match = re.search(r"<class '([^']+)'>:\s*(.+)", err_str, re.DOTALL)
            if match:
                parsed["class"] = match.group(1).strip()
                parsed["message"] = match.group(2).strip()
            else:
                # no class found, use entire string as message
                parsed["message"] = err_str.strip()

        # extract info hash (40 hex characters) if present in the message
        if parsed.get("message"):
            hash_match = re.search(r"\b([0-9a-fA-F]{40})\b", parsed["message"])
            if hash_match:
                parsed["info_hash"] = hash_match.group(1)

        return parsed
