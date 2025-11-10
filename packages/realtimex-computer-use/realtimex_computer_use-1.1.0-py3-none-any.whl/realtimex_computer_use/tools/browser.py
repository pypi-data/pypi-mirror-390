"""Browser control tools for opening URLs and managing browser instances."""

import webbrowser
from typing import Dict, Optional, Literal
from pydantic import Field


def open_browser(
    url: str = Field(description="The URL to open in the browser"),
    browser: Optional[
        Literal["chrome", "firefox", "safari", "edge", "default"]
    ] = Field(
        default="default",
        description="Browser to use. Options: chrome, firefox, safari, edge, default. Defaults to system default browser.",
    ),
) -> Dict[str, str]:
    """Open a URL in the specified browser with automatic fallback to system default."""
    try:
        if browser == "default" or browser is None:
            webbrowser.open(url)
            return {"status": "success", "message": f"Opened {url} in default browser"}

        try:
            browser_controller = webbrowser.get(browser)
            browser_controller.open(url)
            return {"status": "success", "message": f"Opened {url} in {browser}"}
        except webbrowser.Error:
            webbrowser.open(url)
            return {
                "status": "success",
                "message": f"Browser '{browser}' not available. Opened {url} in default browser",
            }

    except Exception as e:
        return {"status": "error", "message": f"Failed to open browser: {str(e)}"}


def open_browser_new_tab(
    url: str = Field(description="The URL to open in a new tab"),
    browser: Optional[
        Literal["chrome", "firefox", "safari", "edge", "default"]
    ] = Field(
        default="default",
        description="Browser to use. Options: chrome, firefox, safari, edge, default. Defaults to system default browser.",
    ),
) -> Dict[str, str]:
    """Open a URL in a new browser tab, launching the browser if needed."""
    try:
        if browser == "default" or browser is None:
            webbrowser.open_new_tab(url)
            return {
                "status": "success",
                "message": f"Opened {url} in new tab (default browser)",
            }

        try:
            browser_controller = webbrowser.get(browser)
            browser_controller.open_new_tab(url)
            return {
                "status": "success",
                "message": f"Opened {url} in new {browser} tab",
            }
        except webbrowser.Error:
            webbrowser.open_new_tab(url)
            return {
                "status": "success",
                "message": f"Browser '{browser}' not available. Opened {url} in new tab (default browser)",
            }

    except Exception as e:
        return {"status": "error", "message": f"Failed to open new tab: {str(e)}"}


def open_browser_new_window(
    url: str = Field(description="The URL to open in a new window"),
    browser: Optional[
        Literal["chrome", "firefox", "safari", "edge", "default"]
    ] = Field(
        default="default",
        description="Browser to use. Options: chrome, firefox, safari, edge, default. Defaults to system default browser.",
    ),
) -> Dict[str, str]:
    """Open a URL in a new browser window instance."""
    try:
        if browser == "default" or browser is None:
            webbrowser.open_new(url)
            return {
                "status": "success",
                "message": f"Opened {url} in new window (default browser)",
            }

        try:
            browser_controller = webbrowser.get(browser)
            browser_controller.open_new(url)
            return {
                "status": "success",
                "message": f"Opened {url} in new {browser} window",
            }
        except webbrowser.Error:
            webbrowser.open_new(url)
            return {
                "status": "success",
                "message": f"Browser '{browser}' not available. Opened {url} in new window (default browser)",
            }

    except Exception as e:
        return {"status": "error", "message": f"Failed to open new window: {str(e)}"}
