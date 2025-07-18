import os
import subprocess
import threading
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename

import settings

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

SCENE_LIST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scene_list.json')

def load_scene_list():
    if os.path.exists(SCENE_LIST_FILE):
        with open(SCENE_LIST_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                return [Scene(**scene) for scene in data]
            except Exception:
                return []
    return []

def save_scene_list():
    with open(SCENE_LIST_FILE, 'w', encoding='utf-8') as f:
        json.dump([scene.__dict__ for scene in scene_list], f, indent=2)

scene_list = load_scene_list()
log_lines = []
render_thread = None
blender_executable_path = settings.load_blender_executable()

# rendering status tracking
is_rendering = False
current_scene_index = -1
stop_event = threading.Event()


class Scene:
    def __init__(self, file, output_folder, frame_start, frame_end, prefix,
                 resolution_x=None, resolution_y=None, engine=None, samples=None,
                 file_format=None, color_depth=None, fps=None):
        self.file = file
        self.output_folder = output_folder
        self.frame_start = frame_start
        self.frame_end = frame_end
        self.prefix = prefix
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.engine = engine
        self.samples = samples
        self.file_format = file_format
        self.color_depth = color_depth
        self.fps = fps


def log(message: str):
    print(message)
    log_lines.append(message)


def render_process(scene: Scene):
    try:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'render_blender.py')
        output_dir = scene.output_folder or os.path.dirname(scene.file)
        # Log file existence and paths
        log(f"[DEBUG] Blender executable: {blender_executable_path} (exists: {os.path.exists(blender_executable_path)})")
        log(f"[DEBUG] Script path: {script_path} (exists: {os.path.exists(script_path)})")
        log(f"[DEBUG] Blend file: {scene.file} (exists: {os.path.exists(scene.file)})")
        log(f"[DEBUG] Output dir: {output_dir} (exists: {os.path.exists(output_dir)})")
        render_command = [
            blender_executable_path,
            '--background',
            '--python', script_path,
            '--',
            '--blend-file', scene.file,
            '--output-dir', output_dir,
            '--prefix', scene.prefix,
            '--frame-start', str(scene.frame_start),
            '--frame-end', str(scene.frame_end),
        ]
        if scene.resolution_x is not None:
            render_command += ['--resolution-x', str(scene.resolution_x)]
        if scene.resolution_y is not None:
            render_command += ['--resolution-y', str(scene.resolution_y)]
        if scene.engine:
            render_command += ['--engine', scene.engine]
        if scene.samples is not None:
            render_command += ['--samples', str(scene.samples)]
        if scene.file_format:
            render_command += ['--file-format', scene.file_format]
        if scene.color_depth:
            render_command += ['--color-depth', scene.color_depth]
        if scene.fps is not None:
            render_command += ['--fps', str(scene.fps)]
        log(f"[DEBUG] Render command: {' '.join(render_command)})")
        with subprocess.Popen(render_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
            for output_line in proc.stdout:
                if stop_event.is_set():
                    proc.terminate()
                    break
                log(output_line.strip())
        log(f"Rendering completed for {scene.file}")
    except Exception as e:
        log(f"Error while rendering scene {scene.file}: {e}")


def run_rendering():
    global is_rendering, current_scene_index
    is_rendering = True
    current_scene_index = -1
    for idx, scene in enumerate(scene_list):
        if stop_event.is_set():
            break
        current_scene_index = idx
        log(f"--- Rendering scene {idx + 1}/{len(scene_list)}: {scene.file} ---")
        render_process(scene)
    current_scene_index = -1
    is_rendering = False
    stop_event.clear()
    log("All scenes rendered")


@app.route('/')
def index():
    return render_template('index.html', scenes=scene_list)


@app.route('/add', methods=['POST'])
def add_scene():
    uploaded_file = request.files.get('scene_file')
    if uploaded_file and uploaded_file.filename:
        filename = secure_filename(uploaded_file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(save_path)
        scene_file = save_path
    else:
        scene_file = request.form.get('scene_file', '')

    output_folder = request.form.get('output_folder', '')
    prefix = request.form.get('prefix', '')
    try:
        frame_start = int(request.form.get('frame_start', 0))
        frame_end = int(request.form.get('frame_end', 0))
    except ValueError:
        return redirect(url_for('index'))
    def opt_int(name):
        val = request.form.get(name)
        try:
            return int(val) if val else None
        except (TypeError, ValueError):
            return None
    resolution_x = opt_int('resolution_x')
    resolution_y = opt_int('resolution_y')
    samples = opt_int('samples')
    fps = opt_int('fps')
    engine = request.form.get('engine') or None
    file_format = request.form.get('file_format') or None
    color_depth = request.form.get('color_depth') or None
    if not scene_file:
        return redirect(url_for('index'))
    scene_list.append(Scene(
        scene_file, output_folder, frame_start, frame_end, prefix,
        resolution_x=resolution_x, resolution_y=resolution_y,
        engine=engine, samples=samples, file_format=file_format,
        color_depth=color_depth, fps=fps))
    save_scene_list()
    return redirect(url_for('index'))


@app.route('/clear', methods=['POST'])
def clear_scenes():
    scene_list.clear()
    save_scene_list()
    return redirect(url_for('index'))


@app.route('/remove/<int:idx>', methods=['POST'])
def remove_scene(idx: int):
    if 0 <= idx < len(scene_list):
        scene_list.pop(idx)
        save_scene_list()
    return redirect(url_for('index'))


@app.route('/render', methods=['POST'])
def render():
    global render_thread
    if render_thread is None or not render_thread.is_alive():
        render_thread = threading.Thread(target=run_rendering, daemon=True)
        render_thread.start()
    return redirect(url_for('logs'))


@app.route('/cancel', methods=['POST'])
def cancel_render():
    if render_thread and render_thread.is_alive():
        stop_event.set()
    return redirect(url_for('logs'))


@app.route('/status')
def status():
    total = len(scene_list)
    current_file = ''
    if is_rendering and 0 <= current_scene_index < total:
        current_file = scene_list[current_scene_index].file
    return jsonify({
        'rendering': is_rendering,
        'current_index': current_scene_index + 1 if is_rendering else 0,
        'total': total,
        'current_file': current_file,
    })


@app.route('/logs')
def logs():
    if request.args.get('plain'):
        return "\n".join(log_lines)
    return render_template('logs.html', log_text="\n".join(log_lines))


@app.route('/settings', methods=['GET', 'POST'])
def settings_view():
    global blender_executable_path
    if request.method == 'POST':
        # Only allow entering a path, do not allow upload
        blender_executable_path = request.form.get('blender_path', '')
        settings.save_blender_executable(blender_executable_path)
        return redirect(url_for('index'))
    return render_template('settings.html', blender_path=blender_executable_path)


if __name__ == '__main__':
    app.run()

