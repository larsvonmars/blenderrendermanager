import os
import subprocess
import threading
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import settings

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

scene_list = []
log_lines = []
render_thread = None
blender_executable_path = settings.load_blender_executable()


class Scene:
    def __init__(self, file, output_folder, frame_start, frame_end, prefix):
        self.file = file
        self.output_folder = output_folder
        self.frame_start = frame_start
        self.frame_end = frame_end
        self.prefix = prefix


def log(message: str):
    print(message)
    log_lines.append(message)


def render_process(scene: Scene):
    try:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'render_blender.py')
        output_dir = scene.output_folder or os.path.dirname(scene.file)
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
        with subprocess.Popen(render_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
            for output_line in proc.stdout:
                log(output_line.strip())
        log(f"Rendering completed for {scene.file}")
    except Exception as e:
        log(f"Error while rendering scene {scene.file}: {e}")


def run_rendering():
    for scene in scene_list:
        render_process(scene)
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
    if not scene_file:
        return redirect(url_for('index'))
    scene_list.append(Scene(scene_file, output_folder, frame_start, frame_end, prefix))
    return redirect(url_for('index'))


@app.route('/clear', methods=['POST'])
def clear_scenes():
    scene_list.clear()
    return redirect(url_for('index'))


@app.route('/render', methods=['POST'])
def render():
    global render_thread
    if render_thread is None or not render_thread.is_alive():
        render_thread = threading.Thread(target=run_rendering)
        render_thread.start()
    return redirect(url_for('logs'))


@app.route('/logs')
def logs():
    if request.args.get('plain'):
        return "\n".join(log_lines)
    return render_template('logs.html', log_text="\n".join(log_lines))


@app.route('/settings', methods=['GET', 'POST'])
def settings_view():
    global blender_executable_path
    if request.method == 'POST':
        uploaded_exec = request.files.get('blender_path')
        if uploaded_exec and uploaded_exec.filename:
            filename = secure_filename(uploaded_exec.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_exec.save(save_path)
            blender_executable_path = save_path
        else:
            blender_executable_path = request.form.get('blender_path', '')
        settings.save_blender_executable(blender_executable_path)
        return redirect(url_for('index'))
    return render_template('settings.html', blender_path=blender_executable_path)


if __name__ == '__main__':
    app.run()

