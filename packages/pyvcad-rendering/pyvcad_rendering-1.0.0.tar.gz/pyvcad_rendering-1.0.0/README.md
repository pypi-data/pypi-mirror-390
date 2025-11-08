# pyvcad-rendering

Prototype Python bindings that bring OpenVCAD (`pyvcad`) geometry to a Qt/VTK
viewport. The library is currently **pre-alpha** and ships with placeholder
implementations that outline how the viewer will be structured.

## Installation

```bash
pip install pyvcad-rendering
```

> **Note**
> The dependency graph pulls in `pyvcad`, `vtk`, and `PySide6`. These packages
> can be heavy and may require system-level prerequisites. Please review the
> upstream projects for platform specific notes.

## Quickstart

```python
from pyvcad_rendering import Render

# Obtain or construct a pyvcad model somewhere in your application
vcad_shape = build_my_vcad_shape()

renderer = Render()
context = renderer(vcad_shape)

# The current scaffold raises NotImplementedError because the VTK scene hookup
# is pending. Once implemented, a Qt window will appear and stay responsive for
# as long as the application event loop runs.
context.app.exec()
```

## Project Layout

```
rendering_v2/
├── pyproject.toml
├── README.md
└── src/
    └── pyvcad_rendering/
        ├── __init__.py
        └── render.py
```

Upcoming work will flesh out dedicated modules for scene translation, Qt/VTK
widgets, and convenience components for embedding the viewer inside existing
OpenVCAD tools.
