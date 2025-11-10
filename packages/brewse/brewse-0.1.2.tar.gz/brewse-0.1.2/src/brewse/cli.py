#!/usr/bin/env python3

import subprocess
import curses
from dataclasses import dataclass
from typing import List, Dict, Optional
import urllib.request
import json
from pathlib import Path
from datetime import datetime, timedelta
import threading
import time
import argparse
import shutil
# termios and tty previously used for manual exit handling; no longer needed


@dataclass
class BrewPackage:
    name: str
    category: str  # 'Formulae' or 'Casks'
    installed: bool = False


@dataclass
class PackageInfo:
    name: str
    version: Optional[str] = None
    description: Optional[str] = None
    homepage: Optional[str] = None
    installed: bool = False
    analytics: Dict[str, int] = None
    artifacts: List[str] = None


class BrewInteractive:
    def __init__(self, force_refresh: bool = False):
        self.packages: List[BrewPackage] = []
        self.selected_index = 0
        self.scroll_offset = 0  # Add scroll offset tracking
        self.view_mode = "search"
        self.current_package_info: Optional[PackageInfo] = None
        self.search_term = ""
        self.api_base_url = "https://formulae.brew.sh/api"
        # Add cache directory
        self.cache_dir = Path.home() / ".cache" / "brewse"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.is_data_loaded = False
        self.is_loading = False
        self.request_search_input = False  # Signal to re-open search prompt
        # Progress tracking
        self.download_progress = {"current": 0, "total": 0, "file": ""}
        self.progress_lock = threading.Lock()
        self.force_refresh = force_refresh
        # Keep parsed data in memory to avoid re-parsing on each search
        self.formulae_data = None
        self.casks_data = None
        # Cache installed packages lists
        self._installed_formulae = None
        self._installed_casks = None

    def _get_cache_path(self, url: str) -> Path:
        """Generate a cache file path from URL."""
        # Create a filename from the URL (replace special chars with _)
        filename = (
            url.replace("https://", "").replace("/", "_").replace(".", "_") + ".json"
        )
        return self.cache_dir / filename

    def _get_file_size(self, url: str) -> int:
        """Get file size using HEAD request."""
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=10) as response:
                content_length = response.headers.get("Content-Length")
                return int(content_length) if content_length else 0
        except Exception:
            return 0

    def _fetch_json(self, url: str, track_progress: bool = False) -> dict:
        """Helper method to fetch and parse JSON from URL with caching."""
        cache_path = self._get_cache_path(url)

        # Check if cache exists and is fresh (less than 24 hours old)
        # Skip cache if force_refresh is enabled
        if not self.force_refresh and cache_path.exists():
            with open(cache_path) as f:
                cached_data = json.load(f)
                cached_time = datetime.fromtimestamp(cached_data["timestamp"])
                if datetime.now() - cached_time < timedelta(hours=24):
                    return cached_data["data"]

        # Only show loading message when actually fetching from network
        if hasattr(self, "stdscr") and self.search_term:
            height, width = self.stdscr.getmaxyx()
            loading_msg = "Loading data..."
            self.stdscr.clear()
            self.stdscr.addstr(
                height // 2, (width - len(loading_msg)) // 2, loading_msg
            )
            self.stdscr.refresh()

        # Fetch fresh data with progress tracking
        try:
            with urllib.request.urlopen(url, timeout=120) as response:
                if track_progress:
                    # Get file size from response headers
                    content_length = response.headers.get("Content-Length")
                    file_size = int(content_length) if content_length else 0

                    # Extract filename from URL
                    filename = url.split("/")[-1]

                    # Download in chunks and track progress
                    data_bytes = b""
                    chunk_size = 8192
                    downloaded = 0

                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        data_bytes += chunk
                        downloaded += len(chunk)

                        # Update progress
                        if file_size > 0:
                            with self.progress_lock:
                                self.download_progress["current"] += len(chunk)
                                self.download_progress["file"] = filename

                    data = json.loads(data_bytes)
                else:
                    data = json.loads(response.read())
        except urllib.error.URLError as e:
            raise Exception(
                f"Network error: {e.reason}. Check your internet connection."
            )
        except TimeoutError:
            raise Exception("Request timed out. Server may be slow or unreachable.")

        # Cache the data
        cache_data = {"timestamp": datetime.now().timestamp(), "data": data}
        with open(cache_path, "w") as f:
            json.dump(cache_data, f)

        return data

    def _background_load_data(self):
        """Load initial API data in background."""
        try:
            self.is_loading = True

            # Get file sizes first
            formula_url = f"{self.api_base_url}/formula.json"
            cask_url = f"{self.api_base_url}/cask.json"

            # Check if we need to download (not in cache or stale)
            formula_cached = self._is_cache_fresh(formula_url)
            cask_cached = self._is_cache_fresh(cask_url)

            if not formula_cached or not cask_cached:
                # Calculate total size for progress tracking
                total_size = 0
                if not formula_cached:
                    total_size += self._get_file_size(formula_url)
                if not cask_cached:
                    total_size += self._get_file_size(cask_url)

                with self.progress_lock:
                    self.download_progress["total"] = total_size
                    self.download_progress["current"] = 0

            # Fetch both datasets with progress tracking and keep in memory
            self.formulae_data = self._fetch_json(
                formula_url, track_progress=not formula_cached
            )
            self.casks_data = self._fetch_json(cask_url, track_progress=not cask_cached)
            self.is_data_loaded = True
        finally:
            self.is_loading = False

    def _is_cache_fresh(self, url: str) -> bool:
        """Check if cache exists and is fresh."""
        if self.force_refresh:
            return False

        cache_path = self._get_cache_path(url)
        if cache_path.exists():
            try:
                with open(cache_path) as f:
                    cached_data = json.load(f)
                    cached_time = datetime.fromtimestamp(cached_data["timestamp"])
                    return datetime.now() - cached_time < timedelta(hours=24)
            except Exception:
                return False
        return False

    def _get_installed_packages(self):
        """Get all installed packages once and cache them."""
        if self._installed_formulae is None:
            try:
                result = subprocess.run(
                    ["brew", "list", "--formula"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    self._installed_formulae = set(result.stdout.strip().split("\n"))
                else:
                    self._installed_formulae = set()
            except Exception:
                self._installed_formulae = set()

        if self._installed_casks is None:
            try:
                result = subprocess.run(
                    ["brew", "list", "--cask"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    self._installed_casks = set(result.stdout.strip().split("\n"))
                else:
                    self._installed_casks = set()
            except Exception:
                self._installed_casks = set()

    def run_brew_search(self, term: str) -> None:
        """Search packages using the Homebrew API."""
        # Reset position when performing new search
        self.selected_index = 0
        self.scroll_offset = 0
        self.search_term = term
        # Wait for data to be loaded if necessary
        while not self.is_data_loaded:
            if not self.is_loading:
                # If not currently loading, start the load
                self.is_loading = True
                self.formulae_data = self._fetch_json(
                    f"{self.api_base_url}/formula.json"
                )
                self.casks_data = self._fetch_json(f"{self.api_base_url}/cask.json")
                self.is_data_loaded = True
            else:
                # Show loading message while waiting
                height, width = self.stdscr.getmaxyx()
                loading_msg = "Downloading all package data... (this may take a while)"
                self.stdscr.clear()
                self.stdscr.addstr(
                    height // 2, (width - len(loading_msg)) // 2, loading_msg
                )
                self.stdscr.refresh()
                time.sleep(0.1)  # Small delay to prevent CPU spinning

        try:
            # Get all installed packages once
            self._get_installed_packages()

            # Use in-memory data (already parsed)
            self.packages = []
            term_lower = term.lower()

            # Search formulae
            for formula in self.formulae_data:
                if term_lower in formula["name"].lower():
                    name = formula["name"]
                    self.packages.append(
                        BrewPackage(
                            name=name,
                            category="Formulae",
                            installed=name in self._installed_formulae,
                        )
                    )

            # Search casks
            for cask in self.casks_data:
                if term_lower in cask["token"].lower():
                    name = cask["token"]
                    self.packages.append(
                        BrewPackage(
                            name=name,
                            category="Casks",
                            installed=name in self._installed_casks,
                        )
                    )

        except Exception as e:
            print(f"Error fetching search results: {str(e)}")

    def get_package_info(self, package: BrewPackage) -> PackageInfo:
        """Fetch package information using the Homebrew API."""
        try:
            # Determine if it's a formula or cask
            endpoint = "formula" if package.category == "Formulae" else "cask"
            url = f"{self.api_base_url}/{endpoint}/{package.name}.json"

            data = self._fetch_json(url)

            info = PackageInfo(name=package.name)

            if endpoint == "formula":
                info.version = data.get("versions", {}).get("stable")
                info.description = data.get("desc")
                info.homepage = data.get("homepage")
                info.installed = self._is_installed(data)

                # Helper function to safely parse analytics numbers
                def parse_analytics_value(value) -> int:
                    if isinstance(value, int):
                        return value
                    if isinstance(value, str):
                        return int(value.replace(",", ""))
                    return 0

                # Get analytics data
                analytics = data.get("analytics", {}).get("install", {})
                info.analytics = {
                    "30 days": parse_analytics_value(
                        analytics.get("30d", {}).get(package.name, 0)
                    ),
                    "90 days": parse_analytics_value(
                        analytics.get("90d", {}).get(package.name, 0)
                    ),
                    "365 days": parse_analytics_value(
                        analytics.get("365d", {}).get(package.name, 0)
                    ),
                }
            else:  # cask
                info.version = data.get("version")
                info.description = data.get("desc")
                info.homepage = data.get("homepage")
                info.installed = self._is_installed(data)

                # Helper function to safely parse analytics numbers
                def parse_analytics_value(value) -> int:
                    if isinstance(value, int):
                        return value
                    if isinstance(value, str):
                        return int(value.replace(",", ""))
                    return 0

                # Get analytics data
                analytics = data.get("analytics", {}).get("install", {})
                info.analytics = {
                    "30 days": parse_analytics_value(
                        analytics.get("30d", {}).get(package.name, 0)
                    ),
                    "90 days": parse_analytics_value(
                        analytics.get("90d", {}).get(package.name, 0)
                    ),
                    "365 days": parse_analytics_value(
                        analytics.get("365d", {}).get(package.name, 0)
                    ),
                }

            return info

        except Exception as e:
            return PackageInfo(
                name=package.name, description=f"Error fetching info: {str(e)}"
            )

    def _is_installed(self, package_data: dict) -> bool:
        """Return True if the package appears installed via Homebrew."""
        try:
            # Determine package type using Homebrew API schema:
            # - Casks use 'token'
            # - Formulae use 'name' (or 'full_name')
            if "token" in package_data:  # cask
                package_name = package_data.get("token")
                cmd = ["brew", "list", "--cask", package_name]
            else:  # formula
                package_name = package_data.get("name") or package_data.get("full_name")
                if not package_name:
                    return False
                cmd = ["brew", "list", "--formula", package_name]

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def draw_screen(self, stdscr) -> None:
        """Draw the current screen based on view mode."""
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if self.view_mode == "search":
            self.draw_search_results(stdscr, height, width)
        elif self.view_mode == "info":  # info mode
            self.draw_package_info(stdscr, height, width)
        elif self.view_mode == "help":
            self.draw_help(stdscr, height, width)

        stdscr.refresh()

    def draw_header(self, stdscr, title: str, width: int) -> int:
        """Draw a consistent header and return the line number after the header."""
        # Draw title bar
        header_bar = "=" * width
        title_pos = (width - len(title)) // 2  # Center the title

        stdscr.addstr(0, 0, header_bar, curses.A_BOLD)
        stdscr.addstr(1, title_pos, title, curses.A_BOLD)
        stdscr.addstr(2, 0, header_bar, curses.A_BOLD)

        return 4  # Return the line number after the header

    def draw_search_results(self, stdscr, height: int, width: int) -> None:
        """Draw the search results screen."""
        current_line = self.draw_header(stdscr, "Brewse: Homebrew Search", width)

        # Draw search term and result count
        search_info = f"Search Results for '{self.search_term}'"
        count_info = f"({len(self.packages)} found)"

        stdscr.addstr(current_line, 2, search_info)
        # Add count in gray (using dim attribute)
        stdscr.addstr(current_line, 2 + len(search_info) + 1, count_info, curses.A_DIM)
        current_line += 2

        # Calculate available lines for results
        available_lines = height - current_line - 1  # -1 for footer

        # Sort all packages together alphabetically
        self.packages.sort(key=lambda p: p.name.lower())

        # Adjust scroll_offset to keep selected item visible
        visible_area = available_lines - 2  # Account for search term line
        if self.selected_index - self.scroll_offset >= visible_area:
            self.scroll_offset = self.selected_index - visible_area + 1
        elif self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index

        # Ensure scroll offset stays within valid range
        max_scroll = max(0, len(self.packages) - visible_area + 1)
        self.scroll_offset = min(max(0, self.scroll_offset), max_scroll)

        # Draw packages
        current_package_idx = 0
        visible_line = 0

        for package in self.packages:
            if visible_line >= self.scroll_offset:
                if current_line >= height - 1:
                    break
                prefix = "✔ " if package.installed else "  "
                # Make the category suffix gray
                category_suffix = (
                    "(formula)" if package.category == "Formulae" else "(cask)"
                )

                if current_package_idx == self.selected_index:
                    # Selected line
                    stdscr.addstr(
                        current_line, 4, prefix + package.name, curses.A_REVERSE
                    )
                    stdscr.addstr(
                        current_line,
                        4 + len(prefix + package.name) + 1,
                        category_suffix,
                        curses.A_REVERSE | curses.A_DIM,
                    )
                else:
                    # Normal line
                    stdscr.addstr(current_line, 4, prefix + package.name)
                    stdscr.addstr(
                        current_line,
                        4 + len(prefix + package.name) + 1,
                        category_suffix,
                        curses.A_DIM,
                    )

                current_line += 1
            current_package_idx += 1
            visible_line += 1

        # Update footer
        footer = "↑/↓: Navigate | Enter: Show Info | q: Quit | i: Install | n: New Search | h: Help"
        try:
            stdscr.addstr(height - 1, 0, footer[: width - 1], curses.A_BOLD)
        except curses.error:
            pass

    def draw_package_info(self, stdscr, height: int, width: int) -> None:
        """Draw the package info screen."""
        if not self.current_package_info:
            return

        current_line = self.draw_header(stdscr, "Package Information", width)

        # Draw package name
        stdscr.addstr(current_line, 2, f"Package: {self.current_package_info.name}")
        current_line += 2

        # Draw info
        info = self.current_package_info

        def add_line(label: str, value: str) -> None:
            nonlocal current_line
            if current_line >= height - 2:
                return
            try:
                stdscr.addstr(current_line, 2, f"{label}: ", curses.A_BOLD)
                stdscr.addstr(f"{value}"[: width - len(label) - 5])
                current_line += 1
            except curses.error:
                pass

        # Add installed status at the top of the info
        add_line("Status", "✔ Installed" if info.installed else "Not installed")

        if info.version:
            add_line("Version", info.version)
        if info.homepage:
            add_line("Homepage", info.homepage)
        if info.description:
            add_line("Description", info.description)
        if info.analytics:
            current_line += 1
            add_line("Analytics", "")
            for period, count in info.analytics.items():
                add_line(f"  {period}", f"{count} installs")

        # Update the footer text to include uninstall option and help
        footer = "←: Back | i: Install | u: Uninstall | h: Help | q: Quit"
        try:
            stdscr.addstr(height - 1, 0, footer[: width - 1], curses.A_BOLD)
        except curses.error:
            pass

    def draw_help(self, stdscr, height: int, width: int) -> None:
        """Draw the help screen with keybindings and tips."""
        current_line = self.draw_header(stdscr, "Help", width)

        lines = [
            "Keybindings:",
            "",
            "General:",
            "  q         Quit",
            "  h or ?    Help",
            "  / or n    New search",
            "  ← or ⌫    Back",
            "",
            "Search view:",
            "  ↑/↓       Navigate",
            "  PgUp/PgDn Page up/down",
            "  Enter     Show package info",
            "  i         Install selected",
            "",
            "Info view:",
            "  ←         Back to results",
            "  i         Install",
            "  u         Uninstall",
            "",
            f"Cache: {self.cache_dir}",
        ]

        for line in lines:
            if current_line >= height - 2:
                break
            try:
                stdscr.addstr(current_line, 2, line[: max(0, width - 4)])
            except curses.error:
                pass
            current_line += 1

        footer = "ESC/←/⌫: Back | q: Quit"
        try:
            stdscr.addstr(height - 1, 0, footer[: width - 1], curses.A_BOLD)
        except curses.error:
            pass

    def install_package(self) -> None:
        """Install the currently selected package."""
        if self.view_mode == "search":
            package = self.packages[self.selected_index]
        else:
            package = next(
                p for p in self.packages if p.name == self.current_package_info.name
            )

        # Temporarily leave curses input echo for command execution output capture
        try:
            result = subprocess.run(
                ["brew", "install", package.name], capture_output=True, text=True
            )
            success = result.returncode == 0
            message = (
                f"Installed {package.name}"
                if success
                else f"Install failed: {result.stderr.strip()}"
            )
        except Exception as e:
            success = False
            message = f"Install error: {e}"

        # Refresh installed status
        try:
            if success:
                # Invalidate cached install lists to refresh on next search
                if package.category == "Formulae":
                    self._installed_formulae = None
                else:
                    self._installed_casks = None

            if self.view_mode == "search":
                package.installed = True if success else package.installed
            else:
                if self.current_package_info:
                    self.current_package_info.installed = (
                        True if success else self.current_package_info.installed
                    )
        except Exception:
            pass

        # Show transient message at footer area
        try:
            height, width = self.stdscr.getmaxyx()
            self.stdscr.addstr(
                height - 2, 0, (message[: width - 1]).ljust(width - 1), curses.A_BOLD
            )
            self.stdscr.refresh()
        except Exception:
            pass

    def uninstall_package(self) -> None:
        """Uninstall the currently selected package."""
        if self.view_mode == "search":
            package = self.packages[self.selected_index]
        else:
            package = next(
                p for p in self.packages if p.name == self.current_package_info.name
            )

        try:
            result = subprocess.run(
                ["brew", "uninstall", package.name], capture_output=True, text=True
            )
            success = result.returncode == 0
            message = (
                f"Uninstalled {package.name}"
                if success
                else f"Uninstall failed: {result.stderr.strip()}"
            )
        except Exception as e:
            success = False
            message = f"Uninstall error: {e}"

        # Refresh installed status
        try:
            if success:
                # Invalidate cached install lists to refresh on next search
                if package.category == "Formulae":
                    self._installed_formulae = None
                else:
                    self._installed_casks = None

            if self.view_mode == "search":
                package.installed = False if success else package.installed
            else:
                if self.current_package_info:
                    self.current_package_info.installed = (
                        False if success else self.current_package_info.installed
                    )
        except Exception:
            pass

        # Show transient message
        try:
            height, width = self.stdscr.getmaxyx()
            self.stdscr.addstr(
                height - 2, 0, (message[: width - 1]).ljust(width - 1), curses.A_BOLD
            )
            self.stdscr.refresh()
        except Exception:
            pass

    def handle_input(self, stdscr) -> bool:
        """Handle user input. Returns False if should exit."""
        height, width = stdscr.getmaxyx()
        key = stdscr.getch()

        if key == ord("q"):
            return False
        elif key in (ord("\b"), curses.KEY_BACKSPACE, 127, 8):
            if self.view_mode == "info":
                self.view_mode = "search"
                self.current_package_info = None
            elif self.view_mode == "search":
                self.scroll_offset = 0
                self.selected_index = 0
                self.view_mode = "search"
                self.current_package_info = None
                self.request_search_input = True
            return True
        elif key == ord("i"):
            self.install_package()  # This will now handle everything including exit
        elif key == ord("u"):
            self.uninstall_package()  # This will now handle everything including exit
        elif key == ord("/"):  # Quick search
            self.scroll_offset = 0
            self.selected_index = 0
            self.request_search_input = True
            return True
        elif key == ord("h"):  # Show help
            self.view_mode = "help"
            return True
        elif key == ord(" "):  # Page down
            self.selected_index = min(
                len(self.packages) - 1, self.selected_index + (height - 5)
            )
        elif self.view_mode == "search" and key == ord("n"):
            self.scroll_offset = 0  # Reset scroll offset
            self.selected_index = 0
            self.request_search_input = True
            return True
        elif self.view_mode == "search":
            if key == curses.KEY_UP and self.selected_index > 0:
                self.selected_index -= 1
            elif (
                key == curses.KEY_DOWN and self.selected_index < len(self.packages) - 1
            ):
                self.selected_index += 1
            elif key == curses.KEY_PPAGE:  # Page Up
                self.selected_index = max(0, self.selected_index - (height - 5))
            elif key == curses.KEY_NPAGE:  # Page Down
                self.selected_index = min(
                    len(self.packages) - 1, self.selected_index + (height - 5)
                )
            elif key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
                self.current_package_info = self.get_package_info(
                    self.packages[self.selected_index]
                )
                self.view_mode = "info"
        elif self.view_mode == "info":
            if key == curses.KEY_LEFT:  # Add left arrow for consistency
                self.view_mode = "search"
                self.current_package_info = None
        elif self.view_mode == "help":
            if key in (curses.KEY_LEFT, 27) or key in (
                ord("\b"),
                curses.KEY_BACKSPACE,
                127,
                8,
            ):
                # ESC (27), Left, or Backspace exits help
                self.view_mode = "search"

        return True

    def main(self, stdscr, search_term: Optional[str]) -> None:
        """Main application loop."""
        self.stdscr = stdscr
        self.search_term = search_term
        # Reset position when starting new search
        self.selected_index = 0
        self.scroll_offset = 0

        # Setup curses
        curses.curs_set(0)
        stdscr.keypad(1)

        # Initialize colors here, after curses is started
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()

        # Start background loading if not already loaded
        if not self.is_data_loaded and not self.is_loading:
            thread = threading.Thread(target=self._background_load_data)
            thread.daemon = True
            thread.start()

        if search_term is None:
            search_input = self._search_input_flow(stdscr)
            if search_input:
                self.run_brew_search(search_input)
        else:
            self.run_brew_search(search_term)

        # Continue with the rest of the UI loop
        while True:
            # If a new search was requested from input handling, open the prompt
            if self.request_search_input:
                self.request_search_input = False
                search_input = self._search_input_flow(stdscr)
                if search_input:
                    self.run_brew_search(search_input)
            self.draw_screen(stdscr)
            if not self.handle_input(stdscr):
                break

    def _search_input_flow(self, stdscr) -> Optional[str]:
        """Render search prompt and collect input; return the term or None."""
        height, width = stdscr.getmaxyx()
        title = "Brewse: Homebrew Search"
        input_width = 30  # Define fixed input width

        # Set timeout for non-blocking input to allow progress updates
        stdscr.timeout(100)  # 100ms timeout
        curses.curs_set(1)  # Show cursor

        while True:
            stdscr.clear()

            # Draw fancy border
            self.draw_header(stdscr, title, width)

            # Center the content vertically
            content_start = (height - 6) // 2

            # Draw prompt with a box around it
            prompt = "Search anywhere in name:"
            prompt_x = (width - len(prompt)) // 2  # Center the prompt
            input_x = (width - input_width) // 2  # Center the input field

            # Initialize input variables
            search_input = ""
            search_submitted = False
            user_modified_after_submit = False

            # Define instructions
            instructions = ["Press Enter to search", "Press Ctrl+C to quit"]

            # Draw prompt above the input field
            stdscr.addstr(content_start, prompt_x, prompt)

            while True:
                stdscr.clear()

                # Redraw header
                self.draw_header(stdscr, title, width)
                stdscr.addstr(content_start, prompt_x, prompt)

                # Determine if we should gray out the input (search submitted but not modified)
                input_style = curses.A_UNDERLINE
                text_style = curses.A_NORMAL
                if search_submitted and not user_modified_after_submit:
                    text_style = curses.A_DIM

                # Redraw the input field with a line of spacing
                stdscr.addstr(
                    content_start + 2,
                    input_x,
                    " " * input_width,
                    input_style,
                )

                # Center the text within the input field
                if search_input:
                    text_start = input_x + (input_width - len(search_input)) // 2
                    stdscr.addstr(
                        content_start + 2, text_start, search_input, text_style
                    )
                    cursor_x = text_start + len(search_input)
                else:
                    cursor_x = input_x + (input_width // 2)

                # Draw instructions centered (unless search is submitted)
                if not search_submitted:
                    for i, instruction in enumerate(instructions):
                        instr_x = (width - len(instruction)) // 2
                        stdscr.addstr(content_start + 4 + i, instr_x, instruction)
                else:
                    # Show "search queued" message
                    if user_modified_after_submit:
                        queued_msg = "Press Enter again to update search"
                        queued_x = (width - len(queued_msg)) // 2
                        stdscr.addstr(
                            content_start + 4, queued_x, queued_msg, curses.A_DIM
                        )
                    else:
                        queued_msg = (
                            f"Search queued: '{search_input}' - waiting for data..."
                        )
                        queued_x = (width - len(queued_msg)) // 2
                        stdscr.addstr(
                            content_start + 4, queued_x, queued_msg, curses.A_DIM
                        )

                # Show loading progress if downloading
                if self.is_loading and not self.is_data_loaded:
                    with self.progress_lock:
                        current = self.download_progress["current"]
                        total = self.download_progress["total"]

                    # Use bold style if search is submitted, dim if just loading
                    progress_style = curses.A_BOLD if search_submitted else curses.A_DIM

                    if total > 0:
                        # Show progress bar
                        percent = (current / total) * 100
                        current_mb = current / (1024 * 1024)
                        total_mb = total / (1024 * 1024)

                        progress_text = f"Downloading package data: {current_mb:.1f} / {total_mb:.1f} MB ({percent:.0f}%)"
                        progress_x = (width - len(progress_text)) // 2

                        # Position below instructions with extra spacing
                        progress_y = content_start + 7
                        if progress_y < height - 2:
                            try:
                                stdscr.addstr(
                                    progress_y,
                                    progress_x,
                                    progress_text,
                                    progress_style,
                                )

                                # Draw progress bar
                                bar_width = min(50, width - 10)
                                bar_x = (width - bar_width) // 2
                                filled = int(bar_width * (current / total))
                                bar = "█" * filled + "░" * (bar_width - filled)
                                stdscr.addstr(
                                    progress_y + 1, bar_x, bar, progress_style
                                )
                            except curses.error:
                                pass
                    else:
                        # Just show loading message
                        loading_text = "Preparing download..."
                        loading_x = (width - len(loading_text)) // 2
                        progress_y = content_start + 7
                        if progress_y < height - 2:
                            try:
                                stdscr.addstr(
                                    progress_y, loading_x, loading_text, progress_style
                                )
                            except curses.error:
                                pass
                elif self.is_data_loaded:
                    # If search was submitted and data is now loaded, execute the search
                    if search_submitted and not user_modified_after_submit:
                        stdscr.timeout(-1)  # Reset to blocking
                        curses.curs_set(0)
                        return search_input

                    # Show ready message
                    ready_text = "✓ Ready to search"
                    ready_x = (width - len(ready_text)) // 2
                    progress_y = content_start + 7
                    if progress_y < height - 2:
                        try:
                            stdscr.addstr(progress_y, ready_x, ready_text, curses.A_DIM)
                        except curses.error:
                            pass

                # Move cursor to correct position
                stdscr.move(content_start + 2, cursor_x)
                stdscr.refresh()

                # Get input (non-blocking with timeout)
                try:
                    ch = stdscr.getch()
                except KeyboardInterrupt:
                    stdscr.timeout(-1)  # Reset to blocking
                    curses.curs_set(0)
                    return None

                # If no input (timeout), continue loop to update progress
                if ch == -1:
                    continue

                # Handle Ctrl+C to quit
                if ch == 3:  # Ctrl+C
                    stdscr.timeout(-1)  # Reset to blocking
                    curses.curs_set(0)
                    return None

                if ch in (curses.KEY_ENTER, 10, 13):  # Enter key
                    if search_input:
                        # Check if data is already loaded
                        if self.is_data_loaded:
                            stdscr.timeout(-1)  # Reset to blocking
                            curses.noecho()
                            curses.curs_set(0)
                            return search_input
                        else:
                            # Mark as submitted but allow editing
                            search_submitted = True
                            user_modified_after_submit = False
                elif ch in (curses.KEY_BACKSPACE, 127, 8):  # Backspace
                    if search_input:
                        search_input = search_input[:-1]
                        if search_submitted:
                            user_modified_after_submit = True
                elif ch == curses.KEY_RESIZE:
                    height, width = stdscr.getmaxyx()
                    stdscr.clear()
                elif 32 <= ch <= 126:  # Printable characters
                    if len(search_input) < input_width - 2:  # Leave some padding
                        search_input += chr(ch)
                        if search_submitted:
                            user_modified_after_submit = True


def main():
    """Entry point for the CLI."""
    # Import version, with fallback for direct script execution
    try:
        from brewse import __version__
    except ImportError:
        __version__ = "0.1.2"  # Fallback for development

    parser = argparse.ArgumentParser(
        description="An interactive TUI browser for Homebrew packages", prog="brewse"
    )
    parser.add_argument(
        "search_term", nargs="?", help="Optional search term to use immediately"
    )
    parser.add_argument("--version", action="version", version=f"brewse {__version__}")
    parser.add_argument(
        "--refresh", action="store_true", help="Force refresh of cached package data"
    )
    parser.add_argument(
        "--clear-cache", action="store_true", help="Clear all cached data and exit"
    )

    args = parser.parse_args()

    # Handle --clear-cache
    if args.clear_cache:
        cache_dir = Path.home() / ".cache" / "brewse"
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            print(f"✓ Cache cleared: {cache_dir}")
        else:
            print(f"Cache directory does not exist: {cache_dir}")
        return

    # Create app with force_refresh flag
    app = BrewInteractive(force_refresh=args.refresh)

    # Run with or without search term
    if args.search_term:
        curses.wrapper(lambda stdscr: app.main(stdscr, args.search_term))
    else:
        curses.wrapper(lambda stdscr: app.main(stdscr, None))


if __name__ == "__main__":
    main()
