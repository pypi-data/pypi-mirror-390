# Windows UI Automation Framework
_Automate Windows apps easily using pywinauto — Launch, Connect, and Control with one class._

---

## 🚀 Overview

This Python framework provides a **clean, unified interface for automating Windows applications**.  
It is built on top of `pywinauto` and `psutil` to help you **launch**, **connect**, and **interact with UI elements** programmatically — ideal for UI validation, smoke testing, or system automation.

**Key Capabilities**
- Launch and connect to Windows apps (EXE or UWP)
- Locate and interact with UI controls (`click`, `type_keys`, etc.)
- Extract UI tree structure to JSON for inspection
- Handle element reloads automatically with configurable wait times
- Optionally capture system metrics (CPU, memory, battery)
- Support HP laptop power switching *(available on request — HP confidential)*

---

## 🧩 Installation

```bash
pip install hp-uia-core
```

**Requirements**
- Windows 11 or later  
- Python 3.10+ (tested with 3.13)  
- Dependencies: `pywinauto`, `psutil`, `wmi` *(optional)*  

---

## ⚡ Quickstart

Here’s how to launch and connect to an application using the latest `ensure_connected()` method.

```python
from app_manager import AppManager
import time

app = AppManager()

# Example 1: Use window title and app name for UWP apps and installed programs
app_window = app.ensure_connected(connect_window="Camera", launch_app="Camera")

# Example 2: Connect to a running app or launch by exe path if not running
# app_window = app.ensure_connected(
#     connect_process="LM Studio.exe",
#     launch_exe=r"C:\Users\ivers\AppData\Local\Programs\LM Studio\LM Studio.exe"
# )

# Optional: Extract UI elements to JSON for inspection
app.extract_elements(dump_file="camera_elements.json")

# UI Locators
SETTINGS_BTN = {"automation_id": "settingsButton"}

# Interact with elements
app.element(SETTINGS_BTN).click_input()
time.sleep(1)
app.close(graceful=True)
```

✅ `ensure_connected()` automatically:
1. Tries to connect to an existing app window (by window title or process name).
2. If not found, launches the app (by app name or exe path).
3. Retries connection until success or timeout.

✅ There are 2 ways to find the locator of the desired UI elements:
1. Use [Accessibility Insights Tool](https://accessibilityinsights.io/docs/windows/overview/).
2. Use built-in `extract_elements()` to dump the full UI tree to JSON for easy locator discovery.
---

## 📘 Core Components

### 1. `AppManager` (in `app_manager.py`)
The central class that manages application lifecycle and UI element operations.

**Highlights**
- `ensure_connected()` – One-call launch & connect helper  
- `launch()` – Start an app via `.exe` path or UWP name  
- `connect()` – Attach to a running app via window title or process name  
- `extract_elements()` – Dump all UI elements as structured JSON  
- `element()` – Retrieve specific UI elements via locator dictionary  

**Custom Exceptions**
- `AppManagerError`
- `AumidNotFoundError`
- `WindowNotFoundError`
- `ElementNotFoundError`

**Element Wait Time**
```python
app = AppManager(ele_wait_time=8)  # wait up to 8 seconds for elements to appear
```
- Increase for slow apps
- Keep small for responsive ones
- You can manually call `app.refresh_elements()` anytime

---

### 2. System Metrics (`utils.py`)
```python
from utils import capture_system_metrics

capture_system_metrics('Test Started')
# ... run automation ...
capture_system_metrics('Test Completed')
```
Writes timestamped CPU/memory/battery stats to `system_metrics.csv`.

---

### 3. HP Power Switching (`hp_power_switch.py`)
> ⚠️ This module is **not included** in the public release because it contains HP confidential content.  
> For HP internal users, contact the author to request access to the HP-specific scripts.

**Functions (internal version)**
- `switch_power_mode(target)` – switch between `'AC'` and `'DC'`
- `get_power_status()` – retrieve current power source

**Requirements**
- HP laptop with BIOS power switching
- Admin privileges  
- `wmi`, `pywin32`

---

## 🧠 Example: Automating Camera

```python
from app_manager import AppManager

app = AppManager()
app_window = app.ensure_connected(launch_app="Camera", connect_window="Camera")

app.element({"automation_id": "settingsButton"}).click_input()
app.close(graceful=True)
```

---

## 💡 Common Patterns

### Typing into Fields
```python
SEARCH_BOX = {"control_type": "Edit", "name": "Search"}
app.element(SEARCH_BOX).type_keys("Hello World", with_spaces=True)
app.element(SEARCH_BOX).type_keys("{ENTER}")
```

### Clicking Menu Items
```python
FILE_MENU = {"control_type": "MenuItem", "name": "File"}
SAVE_OPTION = {"control_type": "MenuItem", "name": "Save"}

app.element(FILE_MENU).click_input()
app.element(SAVE_OPTION).click_input()
```

### Waiting for Elements
```python
app = AppManager(ele_wait_time=10)
time.sleep(2)
```

### Error Handling
```python
from app_manager import ElementNotFoundError

try:
    app.element({"name": "Submit"}).click_input()
except ElementNotFoundError:
    app.element({"automation_id": "submitBtn"}).click_input()
```

---

## 🧩 Advanced Usage

### Extract Elements Tree
```python
app.extract_elements(max_depth=5, include_invisible=True, dump_file="ui_elements.json")
```

### Use Locator Modules
```python
# locators_myapp.py
OK_BTN = {"control_type": "Button", "name": "OK"}
USERNAME = {"automation_id": "UsernameInput"}

# script
import locators_myapp as ui
app.element(ui.USERNAME).type_keys("user@example.com", with_spaces=True)
app.element(ui.OK_BTN).click_input()
```

---

## 🔍 Troubleshooting

**Element Not Found**
- Re-extract elements to confirm locator
- Check if control is visible and loaded
- Use `include_invisible=True` for hidden items
- Increase `ele_wait_time`

**App Won’t Launch**
- For UWP apps: ensure the name matches Start Menu entry  
- For `.exe`: use full path  
- Check if already running

**Metrics Not Captured**
- Verify permissions for output folder  
- Ensure `psutil` is installed

**HP Power Switching Not Available**
- Internal-only module (contact author for details)

---

## ⚙️ Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

---

## 🧭 Project Structure

```
ui_automation/
├── app_manager.py
├── utils.py
├── hp_power_switch.py        # HP internal module (confidential)
├── requirements.txt
├── samples/
│   ├── auto_camera.py
│   ├── auto_lm_studio.py
│   └── locators_*.py
└── README.md
```

---

## 🤝 Contributing

When extending this framework:
1. Follow the established patterns (`AppManager`, locators modules, sample scripts)
2. Add docstrings to new methods
3. Test on Windows 11
4. Update README if adding new features

---

## 🧾 License

This project is provided for **educational and testing purposes**.  
For commercial or HP internal use, please contact the author.

---

## 💬 Author Contact

For inquiries or to request HP internal scripts (power switching, enterprise utilities),  
please contact the author directly.

---

Happy automating! 🚀
