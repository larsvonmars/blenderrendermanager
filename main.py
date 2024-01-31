import subprocess
import tkinter as tk
from tkinter import filedialog
import configparser
import os
from tkinter import messagebox
import configparser
import settings
import threading
import queue

blender_executable_path = ""
render_settings = {}
render_queue = queue.Queue()

class Scene:
    def __init__(self, file, output_folder, frame_start, frame_end):
        self.file = file
        self.output_folder = output_folder
        self.frame_start = frame_start
        self.frame_end = frame_end

def render_process(scene):
    try:
        render_command = [
            blender_executable_path,
            '-b', scene.file,
            '-o', os.path.join(scene.output_folder, "frame_####"),
            '-s', str(scene.frame_start),
            '-e', str(scene.frame_end),
            '-a',
            '-F', 'PNG',
            '-x', '1',
        ]
        render_process = subprocess.run(render_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        render_queue.put(render_process.stdout)
        for output_line in iter(render_process.stdout.readline, ''):
            render_queue.put(output_line.strip())
        render_queue.put("Rendering completed for scene.")
    except Exception as e:
        render_queue.put(f"Error during rendering: {e}")

def update_gui():
    while not render_queue.empty():
        message = render_queue.get_nowait()
        status_label.config(text=message)
        console_output.insert(tk.END, message + "\n")
    window.after(100, update_gui)  # Schedule the next update
    
def render():
    if not scene_list:
        messagebox.showerror("NoElementError", "No scenes have been added. Please add at least one scene to render.")
        return

    for scene in scene_list:
        render_thread = threading.Thread(target=render_process, args=(scene,))
        render_thread.start()
    
    update_gui()  # Start updating the GUI

config = configparser.ConfigParser()
config.read('settings.ini')

if 'Blender' in config and 'ExecutablePath' in config['Blender']:
    blender_executable_path = config['Blender']['ExecutablePath']

def open_settings():
    settings.run()
    
def browse_scene_file(scene_entry):
    file_path = filedialog.askopenfilename(filetypes=[("Blender Files", "*.blend")])
    scene_entry.delete(0, tk.END)
    scene_entry.insert(0, file_path)

def browse_output_folder(output_entry):
    folder_path = filedialog.askdirectory()
    output_entry.delete(0, tk.END)
    output_entry.insert(0, folder_path)

def add_scene():
    scene_file = scene_entry.get()
    output_folder = output_entry.get()
    
    try:
        frame_start = int(frame_start_entry.get())
        frame_end = int(frame_end_entry.get())
    except ValueError:
        messagebox.showerror("InputError", "Frame start and end must be integers.")
        return

    if frame_start > frame_end:
        messagebox.showerror("InputError", "Frame start cannot be greater than frame end.")
        return

    if not scene_file.strip():
        messagebox.showerror("SceneFileInvalidError", "Please select a scene file to add.")
        return
    
    if not scene_file.endswith('.blend'):
        messagebox.showerror("SceneFileInvalidError", "The selected file is not a .blend file. Please select a valid Blender scene file.")
        return
    
    scene = Scene(scene_file, output_folder, frame_start, frame_end)
    scene_list.append(scene)

    # Update the listbox to display the added scene
    scene_info = f"File: {scene_file}, Output: {output_folder or 'Blend File Directory'}, Frames: {frame_start}-{frame_end}"
    scene_listbox.insert(tk.END, scene_info)

    # Update the width of the listbox based on the longest line of text
    max_line_width = max(len(line) for line in scene_listbox.get(0, tk.END))
    scene_listbox.config(width=max_line_width)

    # Clear the input fields
    scene_entry.delete(0, tk.END)
    output_entry.delete(0, tk.END)
    frame_start_entry.delete(0, tk.END)
    frame_end_entry.delete(0, tk.END)

def clear_scenes():
    scene_list.clear()
    scene_listbox.delete(0, tk.END)

# Create the GUI window
window = tk.Tk()
window.title("Blender Render")
#blender_entry = tk.Entry(window, width=50)
#blender_entry.pack()

# Add menu bar
menubar = tk.Menu(window)
file = tk.Menu(menubar, tearoff=0)
file.add_command(label="Settings", command=open_settings)
menubar.add_cascade(label="File", menu=file)
window.config(menu=menubar)

# Scene file selection
scene_label = tk.Label(window, text="Scene File:")
scene_label.pack()

scene_entry = tk.Entry(window, width=50)
scene_entry.pack()

browse_scene_button = tk.Button(window, text="Browse", command=lambda: browse_scene_file(scene_entry))
browse_scene_button.pack()

# Output folder selection
output_label = tk.Label(window, text="Output Folder:")
output_label.pack()

output_entry = tk.Entry(window, width=50)
output_entry.pack()

browse_output_button = tk.Button(window, text="Browse", command=lambda: browse_output_folder(output_entry))
browse_output_button.pack()

# Frame range inputs
frame_start_label = tk.Label(window, text="Frame Start:")
frame_start_label.pack()

frame_start_entry = tk.Entry(window, width=50)
frame_start_entry.pack()

frame_end_label = tk.Label(window, text="Frame End:")
frame_end_label.pack()

frame_end_entry = tk.Entry(window, width=50)
frame_end_entry.pack()

# Add scene button
add_scene_button = tk.Button(window, text="Add Scene", command=add_scene)
add_scene_button.pack()

# Scene list
scene_list = []
scene_listbox = tk.Listbox(window, width=1)  # Start with a minimum width
scene_listbox.pack(fill=tk.BOTH)

# Render button
render_button = tk.Button(window, text="Render", command=render)
render_button.pack()

# Clear scenes button
clear_scenes_button = tk.Button(window, text="Clear Scenes", command=clear_scenes)
clear_scenes_button.pack()

# Shutdown checkbox
shutdown_var = tk.IntVar()
shutdown_checkbox = tk.Checkbutton(window, text="Shutdown after rendering", variable=shutdown_var)
shutdown_checkbox.pack()

# Status label
status_label = tk.Label(window, text="")
status_label.pack()

console_output = tk.Text(window, height=10, width=80)
console_output.pack()

# Start the GUI event loop
window.mainloop()
