# RenderManager

A simple tool for managing Blender render jobs. The application now exposes a small web interface instead of a desktop window.

Prerequisites:
- Blender (to provide the `bpy` module)
- Python with the `Flask` package installed

No installation necessary, simply run `python main.py` and open your browser to `http://localhost:5000`.
The web interface provides file pickers for selecting `.blend` files and the Blender executable, and includes a simple stylesheet for improved visuals.

Developed by larsvonmars.

Build instruction:
- Open terminal in folder
- use `pyinstaller --onefile --windowed main.py`
