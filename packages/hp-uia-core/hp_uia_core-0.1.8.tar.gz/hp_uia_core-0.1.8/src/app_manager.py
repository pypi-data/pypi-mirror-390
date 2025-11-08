import psutil
import subprocess
import time
import logging
import json
import os
from dataclasses import dataclass, asdict
from typing import List, Optional
from pathlib import Path
from pywinauto import Application, Desktop
from pywinauto.base_wrapper import BaseWrapper
from pywinauto.controls.uiawrapper import UIAWrapper


class AppManagerError(RuntimeError):
    ...


class AumidNotFoundError(AppManagerError):
    ...


class WindowNotFoundError(AppManagerError):
    ...


class ElementNotFoundError(AppManagerError):
    ...


@dataclass
class ElementInfo:
    handle:   int
    control_type: str
    name:     str
    automation_id: str
    rectangle: str        # "left, top, right, bottom"
    depth:    int         # distance from the root window


class AppManager:
    def __init__(self, *, backend: str = "uia", ele_wait_time: int = 1) -> None:
        self.backend = backend
        self.ele_wait_time = ele_wait_time
        self.elements: Optional[list[tuple[ElementInfo, BaseWrapper]]] = None
        self._app: Optional[Application] = None
        self._window: Optional[BaseWrapper] = None
        self._log: logging.Logger = logging.getLogger(__name__)

    # ---------- life‑cycle ----------
    def launch(
        self,
        *,
        exe_path: str | None = None,
        app_name: str | None = None
    ) -> subprocess.Popen:
        """
        Launch an application, either by executable path or by UWP app name.

        Exactly one of `exe_path` or `app_name` must be provided.

        Parameters
        ----------
        exe_path : str | None
            Full path to a .exe file (for classic Win32 apps).
        app_name : str | None
            Display name of a UWP app (used to resolve AUMID).
        delay : int, default=1
            Seconds to wait after launching before returning.

        Returns
        -------
        subprocess.Popen
            The process object for the launched application.

        Raises
        ------
        ValueError
            If neither or both of exe_path and app_name are provided.
        AumidNotFoundError
            If a UWP app name cannot be resolved to an AUMID.
        """
        if bool(exe_path) == bool(app_name):
            raise ValueError("Exactly one of exe_path or app_name must be specified.")

        if exe_path:
            if not os.path.exists(exe_path):
                raise FileNotFoundError(f"Executable not found: {exe_path}")
            self._log.info("Launching executable: %s", exe_path)
            proc = subprocess.Popen([exe_path])
        else:
            if not app_name:
                raise ValueError("app_name must be provided for UWP app launch.")
            aumid = self._get_aumid(app_name)
            if not aumid:
                raise AumidNotFoundError(f"No AUMID found for app name '{app_name}'")
            self._log.info("Launching UWP app: %s (AUMID=%s)", app_name, aumid)
            proc = subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{aumid}"])

        return proc


    def connect(self, *, window_title: str | None = None,
                process_name: str | None = None,
                timeout: int = 3) -> BaseWrapper:
        if window_title:
            self._app = Application(self.backend).connect(title_re=rf".*{window_title}.*", timeout=timeout)
            self._log.info("Connected to window %s", window_title)
        elif process_name:
            # Connect to the first window of the process when it's ready
            retry = 0
            while retry < timeout and not self._app:
                time.sleep(1)
                for proc in psutil.process_iter(attrs=['pid', 'name']):
                    if proc.info['name'] == process_name:
                        pid = proc.info['pid']
                        windows = Desktop(backend="uia").windows()
                        for win in windows:
                            if win.process_id() == pid:
                                self._app = Application(self.backend).connect(handle=win.handle, timeout=timeout)
                                self._log.info("Connected to process %s (PID=%s)", process_name, pid)
                                break
                retry += 1
        else:
            raise ValueError("Must pass window_title or process_name")

        if not self._app:
            raise RuntimeError("App is not connected")

        self._window = self._app.top_window().wrapper_object()
        
        if not self._window:
            raise WindowNotFoundError("No window found for the application")
        
        self._window.set_focus()
        return self._window
    
    def ensure_connected(
        self,
        *,
        launch_exe: str | None = None,
        launch_app: str | None = None,
        connect_window: str | None = None,
        connect_process: str | None = None,
        connect_timeout: int = 3,
        relaunch_on_fail: bool = True,
        relaunch_connect_timeout: int = 20,
        relaunch_delay: int = 1,
    ):
        """
        Launch (if needed) and connect to an application window.

        Parameters
        ----------
        launch_exe : str | None
            Full path to a .exe (Win32 desktop app). Exactly one of `launch_exe` or `launch_app`
            must be provided if a relaunch is required.
        launch_app : str | None
            UWP display name (used to resolve AUMID). Exactly one of `launch_exe` or `launch_app`
            must be provided if a relaunch is required.
        connect_window : str | None
            Partial or full window title used for connection (regex match in `connect()`).
        connect_process : str | None
            Process name (e.g., 'LM Studio.exe') used for connection.
        connect_timeout : int, default=3
            Timeout for the initial connection attempt (before launching).
        relaunch_on_fail : bool, default=True
            Whether to launch and retry when the first connection attempt fails.
        relaunch_connect_timeout : int, default=20
            Timeout for the connection attempt after launching.
        relaunch_delay : int, default=1
            Seconds to wait after launching before attempting to connect.

        Returns
        -------
        BaseWrapper
            The connected top-level window wrapper object.

        Raises
        ------
        ValueError
            If neither `connect_window` nor `connect_process` is provided; or if both/neither of
            `launch_exe` and `launch_app` are provided when a relaunch is required.
        RuntimeError
            If connection ultimately fails after retries.
        """
        if not connect_window and not connect_process:
            raise ValueError("Must provide at least one of connect_window or connect_process")

        # 1) Try connecting to an existing running instance first (reuses your connect())
        try:
            if connect_window:
                return self.connect(window_title=connect_window, timeout=connect_timeout)  # uses existing connect()
            else:
                return self.connect(process_name=connect_process, timeout=connect_timeout)  # uses existing connect()
        except Exception as e:
            self._log.warning("Initial connect failed (%s).", e)

        # 2) Optionally launch and retry
        if relaunch_on_fail:
            # Only validate launch mode when we actually need to launch
            if bool(launch_exe) == bool(launch_app):
                raise ValueError("Exactly one of launch_exe or launch_app must be specified when relaunching.")

            self._log.info("Launching application and retrying connection...")
            if launch_exe:
                self.launch(exe_path=launch_exe)
            else:
                self.launch(app_name=launch_app)
            time.sleep(relaunch_delay)  # Wait for app to initialize
            
            if connect_window:
                return self.connect(window_title=connect_window, timeout=relaunch_connect_timeout)
            else:
                return self.connect(process_name=connect_process, timeout=relaunch_connect_timeout)

        # 3) No relaunch allowed -> re-raise the original error context
        raise


    def close(self, *, graceful: bool = True) -> None:
        if self._window:
            self._log.info("Closing %s", self._window.window_text())
            if self._app:
                if graceful:
                    try:
                        self._app.top_window().close()
                    except Exception as e:
                        self._log.warning("Graceful close failed: %s, fallback to kill()", e)
                        self._app.kill()
                else:
                    self._app.kill()
            self._window = self._app = None

    def _find_element(self, locator: dict) -> Optional[BaseWrapper]:
        deadline = time.monotonic() + max(0, getattr(self, "ele_wait_time", 1))
        # 初次构建元素缓存
        if self.elements is None:
            self.refresh_elements()

        def match():
            for ei, ctrl in self.elements or []:
                if all(getattr(ei, key, None) == value for key, value in locator.items()):
                    return ctrl
            return None

        # 轮询直到超时
        while True:
            ctrl = match()
            if ctrl:
                return ctrl
            if time.monotonic() >= deadline:
                return None
            # 轻量等待+刷新
            time.sleep(0.2)
            self.refresh_elements()

    def refresh_elements(self, **kwargs):
        self.elements = self.extract_elements(**kwargs)

    def element(self, locator: dict) -> BaseWrapper:
        ctrl = self._find_element(locator)
        if ctrl is None:
            raise ElementNotFoundError(f"Element not found: {locator!r}")
        return ctrl

    def _get_aumid(self, name: str) -> str:
        ps_cmd = ["powershell", "-NoProfile", "-Command",
                  f"Get-StartApps | Where {{$_.Name -like '*{name}*'}} | "
                  "Select -ExpandProperty AppID"]
        try:
            result = subprocess.run(ps_cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get AUMID: {e}") from e
        if not (aumid := result.stdout.strip()):
            raise AumidNotFoundError(f"No AUMID found for {name!r}")
        return aumid

    def extract_elements(
        self,
        max_depth: int = 0,
        include_invisible: bool = False,
        dump_file: Optional[str | Path] = None,
        *,
        isolate: bool = True,       # Pre-warm and re-acquire root before traversal
        enrich_rect: bool = False,  # Optional second pass to fill rectangle() safely
    ) -> List[tuple[ElementInfo, BaseWrapper]]:
        """
        Robust UI tree traversal.

        - Pre-warms RawView providers and re-acquires the root window so the
        first traversal already sees the full Document subtree (fixes
        'first run fewer elements' issue).
        - Uses ControlView first, then RawView as fallback for children().
        - Separates each try/except block to ensure a failed node record
        never blocks its subtree traversal.
        - Automatically whitelists depth==1 Document nodes (client area)
        even if is_visible() fails.
        """

        if not self._window:
            raise RuntimeError("No window connected. Call `connect()` first.")



        log = logging.getLogger(__name__)

        # ---------- Internal helpers ----------
        def _raw_children(ctrl) -> list[BaseWrapper]:
            """Return RawView children; empty list on failure."""
            try:
                eis = ctrl.element_info.children()
                return [UIAWrapper(ei) for ei in eis]
            except Exception as exc:
                log.debug("Raw children() failed: %s", exc)
                return []

        def _safe_children(ctrl) -> list[BaseWrapper]:
            """Try ControlView first, then fall back to RawView."""
            try:
                return ctrl.children()
            except Exception as exc:
                log.debug("ControlView children() failed: %s", exc)
                return _raw_children(ctrl)

        def _prewarm_root():
            """Trigger RawView provider construction with a light scan."""
            try:
                for child in _raw_children(self._window):
                    _ = child.element_info.control_type  # Access to initialize provider
            except Exception as exc:
                log.debug("Prewarm failed: %s", exc)

        def _reacquire_root():
            """Recreate the root wrapper to avoid stale references."""
            try:
                h = int(self._window.handle)    # type: ignore
                self._window = self._app.window(handle=h).wrapper_object()  # type: ignore
            except Exception as exc:
                log.debug("Reacquire root failed: %s", exc)

        # ---------- Isolation / warm-up ----------
        if isolate:
            _prewarm_root()
            try:
                self._window.set_focus()
            except Exception:
                pass
            time.sleep(0.1)  # Let UIA stabilize (important for Electron apps)
            _reacquire_root()

        visited: list[tuple[ElementInfo, BaseWrapper]] = []

        # ---------- Traversal ----------
        def _walk(ctrl, depth: int = 0):
            if max_depth and depth > max_depth:
                return

            # A) Decide whether to record this node
            record = True
            if not include_invisible:
                try:
                    ct = ctrl.element_info.control_type
                except Exception:
                    ct = None
                if not (depth == 1 and ct == "Document"):
                    try:
                        record = bool(ctrl.is_visible())
                    except Exception as exc:
                        log.debug("is_visible() failed @%s: %s", depth, exc)
                        record = False

            # B) Record current node (lightweight: skip rectangle for now)
            if record:
                try:
                    ei = ElementInfo(
                        handle=ctrl.handle,
                        control_type=ctrl.element_info.control_type,
                        name=ctrl.element_info.name,
                        automation_id=ctrl.element_info.automation_id or "",
                        rectangle="",  # Filled later if enrich_rect=True
                        depth=depth,
                    )
                    visited.append((ei, ctrl))
                except Exception as exc:
                    log.debug("Record node failed @%s: %s", depth, exc)

            # C) Recurse into children (always, even if current node failed)
            for child in _safe_children(ctrl):
                try:
                    _walk(child, depth + 1)
                except Exception as exc:
                    log.debug("Walk child failed @%s: %s", depth + 1, exc)

        _walk(self._window)

        # ---------- Optional second pass: fill rectangles ----------
        if enrich_rect:
            for ei, ctrl in visited:
                if not ei.rectangle:
                    try:
                        ei.rectangle = str(ctrl.rectangle())
                    except Exception as exc:
                        log.debug("rectangle() failed h=%s: %s", ei.handle, exc)

        # ---------- Output ----------
        if dump_file:
            dump = [asdict(ei) for ei, _ in visited]
            Path(dump_file).write_text(
                json.dumps(dump, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            log.info("Wrote element dump to %s (count=%d)", dump_file, len(dump))

        return visited