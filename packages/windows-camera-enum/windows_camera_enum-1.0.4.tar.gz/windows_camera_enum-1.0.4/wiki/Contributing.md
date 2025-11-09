# Contributing Guide

Thank you for your interest in contributing to **windows-camera-enum**!

## Ways to Contribute

### 🐛 Report Bugs

Found a bug? [Create an issue](https://github.com/thecheapgeek/python-lite-camera/issues/new) with:

- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Your environment:
  ```
  - OS: Windows 10/11
  - Python version
  - Package version
  - Camera model
  ```
- Minimal code example
- Full error traceback

### 💡 Suggest Features

Have an idea? [Open an issue](https://github.com/thecheapgeek/python-lite-camera/issues/new) describing:

- The problem you're trying to solve
- Proposed solution
- Alternative approaches considered
- Example use cases

### 📸 Test Cameras

Help build the [Camera Compatibility](Camera-Compatibility) list!

1. Run the test script from the compatibility page
2. [Create an issue](https://github.com/thecheapgeek/python-lite-camera/issues/new) with results
3. Include camera make/model and any issues

### 📝 Improve Documentation

Documentation contributions are very welcome!

**Wiki Pages:**
- Fix typos or clarify instructions
- Add examples
- Improve troubleshooting steps
- Add compatibility data

**In-Repo Docs:**
- Submit pull requests for `README.md`, `CHANGELOG.md`, etc.

### 💻 Code Contributions

See the [development setup](#development-setup) below.

---

## Development Setup

### Prerequisites

- **Windows 10/11**
- **Python 3.8+**
- **Visual Studio Build Tools** or Visual Studio with C++ workload
- **Git**

### Clone Repository

```bash
git clone https://github.com/thecheapgeek/python-lite-camera.git
cd python-lite-camera
```

### Install Development Dependencies

```bash
pip install -e . --verbose
```

This installs in "editable" mode, so code changes take effect immediately after rebuild.

### Quick Rebuild Script

After making C++ changes:

```bash
python scripts/rebuild.py --dev
```

This automates:
1. Uninstall package
2. Clean build artifacts
3. Rebuild C++ extension
4. Reinstall in development mode

### Project Structure

```
windows-camera-enum/
├── src/
│   └── camera_enum/
│       ├── __init__.py          # Python API wrapper
│       ├── camera_enum.cpp      # C++ DirectShow implementation
│       └── py.typed             # Type hint marker
├── examples/                    # Usage examples
├── scripts/                     # Development utilities
├── docs/                        # In-repo documentation
│   ├── ARCHITECTURE.md          # Technical details
│   └── IMPROVEMENTS.md          # Planned features
├── CMakeLists.txt               # Build configuration
└── pyproject.toml               # Package metadata
```

---

## Making Changes

### Python Code Changes

Edit `src/camera_enum/__init__.py`:

```bash
# Edit the file
nano src/camera_enum/__init__.py

# No rebuild needed for Python-only changes!
python -c "import camera_enum; camera_enum.list_cameras()"
```

### C++ Code Changes

Edit `src/camera_enum/camera_enum.cpp`:

```bash
# Edit the file
nano src/camera_enum/camera_enum.cpp

# Rebuild required
python scripts/rebuild.py --dev --verbose

# Test
python -c "import camera_enum; camera_enum.list_cameras()"
```

### Testing Changes

```bash
# Test with basic example
python examples/basic_usage.py

# Or write a test script
python -c "
import camera_enum
cameras = camera_enum.list_cameras()
print(f'Found {len(cameras)} camera(s)')
"
```

---

## Code Style Guidelines

### Python Code

Follow **PEP 8**:

```python
# Good
def list_cameras() -> List[Dict[str, Any]]:
    """Enumerate all available cameras."""
    pass

# Bad
def ListCameras():
    pass
```

**Use:**
- Type hints on all public functions
- Descriptive variable names
- Docstrings with examples
- 4 spaces for indentation

### C++ Code

```cpp
// Good
HRESULT hr = CoInitializeEx(NULL, COINIT_MULTITHREADED);
if (FAILED(hr)) {
    throw std::runtime_error("COM initialization failed");
}

// Use descriptive names
IEnumMoniker* pEnum = nullptr;

// Clean up COM objects
if (pEnum) {
    pEnum->Release();
}
```

**Use:**
- Descriptive variable names
- Proper COM cleanup (Release())
- Error checking for all COM calls
- Exceptions for fatal errors

---

## Submitting Pull Requests

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Your Changes

- Write code
- Test thoroughly
- Follow style guidelines

### 3. Update Documentation

If you changed:
- **API:** Update `README.md` and wiki
- **Build process:** Update `docs/ARCHITECTURE.md`
- **Features:** Update `CHANGELOG.md`

### 4. Commit Changes

Use conventional commit format:

```bash
git commit -m "feat: Add new camera control enumeration"
git commit -m "fix: Handle COM initialization edge case"
git commit -m "docs: Improve installation instructions"
```

**Commit types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear description of changes
- Link to related issue (if any)
- Screenshots/examples (if applicable)

---

## Development Tips

### Quick Testing

```python
# Create a test file for rapid iteration
# test.py
import camera_enum

cameras = camera_enum.list_cameras()
print(f"Found: {len(cameras)}")

for camera in cameras:
    print(camera['name'])
```

```bash
# Run frequently while developing
python test.py
```

### Debugging C++ Code

Add debug prints:

```cpp
#include <iostream>

// In your C++ code
std::cout << "Debug: pEnum = " << pEnum << std::endl;
```

Rebuild and check output:

```bash
python scripts/rebuild.py --dev --verbose
```

### Check Build Logs

Verbose mode shows full compilation output:

```bash
python scripts/rebuild.py --dev --verbose
```

---

## Common Development Tasks

### Add a New Exception Class

1. **In `__init__.py`:**
   ```python
   class NewCameraException(CameraException):
       """Description of when this is raised."""
       pass
   ```

2. **In C++ code:**
   ```cpp
   throw std::runtime_error("Specific error message");
   ```

3. **In `__init__.py` wrapper:**
   ```python
   try:
       result = _camera_enum.list_cameras()
   except RuntimeError as e:
       if "specific error message" in str(e):
           raise NewCameraException(str(e))
       raise
   ```

### Add New Camera Information

Example: Adding FPS information

1. **Modify C++** to extract frame rate
2. **Update Python dict** structure in C++
3. **Update type hints** in `__init__.py`
4. **Update documentation**
5. **Test thoroughly**

---

## Getting Help

- **Questions?** [Open a discussion](https://github.com/thecheapgeek/python-lite-camera/discussions)
- **Stuck?** Comment on your pull request
- **Architecture questions?** Read [ARCHITECTURE.md](https://github.com/thecheapgeek/python-lite-camera/blob/main/docs/ARCHITECTURE.md)

---

## Code of Conduct

- Be respectful and constructive
- Help others learn
- Provide detailed feedback on PRs
- Focus on the code, not the person

---

## Recognition

Contributors will be:
- Listed in release notes
- Mentioned in `CHANGELOG.md`
- Credited in git history

Thank you for contributing! 🎉

---

## Related Pages

- **[Architecture](https://github.com/thecheapgeek/python-lite-camera/blob/main/docs/ARCHITECTURE.md)** - Technical deep dive
- **[Improvements](https://github.com/thecheapgeek/python-lite-camera/blob/main/docs/IMPROVEMENTS.md)** - Planned features
- **[Camera Compatibility](Camera-Compatibility)** - Test results
