
<img width="1920" alt="Nercone Modern" src="https://github.com/user-attachments/assets/c92b0407-916f-46ec-9116-c3388b38c88c" />

# nercone-modern
Modern CLI Library

## Installation

### uv
**Install to venv and Add to project dependencies:**
```
uv add nercone-modern
```

**Install to venv:**
```
uv pip install nercone-modern
```

### pip
```
pip3 install nercone-modern
```

## Usage

### Import

```python
from nercone_modern.color import ModernColor
from nercone_modern.text import ModernText
from nercone_modern.logging import ModernLogging
from nercone_modern.progressbar import ModernProgressBar
```

### Color
```python
from nercone_modern.color import ModernColor as Color
print(f"Build {Color.GREEN}Success{Color.RESET}")
```

**Supported colors:**
- `CYAN`
- `MAGENTA`
- `YELLOW`
- `GREEN`
- `RED`
- `BLUE`
- `WHITE`
- `BLACK`
- `GRAY`
- `RESET`

### Text
```python
from nercone_modern.text import ModernText as Text
from nercone_modern.color import ModernColor as Color
print("Build" + Text("Success", color="green"))
print("Build" + Text("Failed", color=Color.RED))
```

### Logging
```python
from nercone_modern.logging import ModernLogging
logger = ModernLogging("Main", display_level="DEBUG")
logger.log("This is a test message", level="INFO")
answer = logger.prompt("What's your name?", level="INFO")
logger.log(f"Answer: {answer}", level="DEBUG")
```

**Supported levels:**
- `DEBUG`
- `INFO`
- `WARN`
- `ERROR`
- `CRITICAL`

### Progress Bar
```python
from nercone_modern.progressbar import ModernProgressBar
progress_bar = ModernProgressBar(total=100, process_name="Task 1", spinner_mode=True)

progress_bar.start()
time.sleep(5)

progress_bar.spinner(False)

progress_bar.setMessage("Step 1")

for i in range(50):
  time.sleep(0.05)
  progress_bar.update(amount=1)

progress_bar.setMessage("Step 2")

for i in range(25):
  time.sleep(0.03)
  progress_bar.update(amount=1)

progress_bar.setMessage("Step 3")

for i in range(5):
  time.sleep(1)
  progress_bar.update(amount=5)

progress_bar.finish()
```
