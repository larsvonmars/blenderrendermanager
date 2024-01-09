import subprocess
import tkinter as tk
from tkinter import filedialog
import configparser
import os
from tkinter import messagebox
import configparser
import settings


blender_executable_path = ""

class Scene:
    def __init__(self, file, output_folder, frame_start, frame_end):
        self.file = file
        self.output_folder = output_folder
        self.frame_start = frame_start
        self.frame_end = frame_end

""" def save_settings():
    global blender_executable_path

    config = configparser.ConfigParser()
    config['Blender'] = {'ExecutablePath': blender_entry.get()}
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)

    blender_executable_path = blender_entry.get()

    with open('settings.ini', 'w') as configfile:
        config.write(configfile)

    # Load Blender executable path from settings.ini
    if 'Blender' in config and 'ExecutablePath' in config['Blender']:
        blender_executable = config['Blender']['ExecutablePath']
        blender_entry.delete(0, tk.END)
        blender_entry.insert(0, blender_executable)
 """

render_settings = {}

def render():
    # Check if the scene list is empty
    if not scene_list:
        messagebox.showerror("NoElementError", "No scenes have been added. Please add at least one scene to render.")
        return
    
    config = configparser.ConfigParser()
    config.read('settings.ini')
    blender_executable = blender_executable_path
    if blender_executable == "":
        messagebox.showerror("ExeError", "No blender executable has been selected. Please select a blender executable.")
        return

    #status_label.config(text="Rendering in progress...")
    window.update()

    outputlog = []
    def update_status_label():
        # Read a line from the subprocess output
        output_line = render_process.stdout.readline()

        if output_line:
            # Update the label with the new line
            status_label.config(text=output_line.strip())
            # Schedule to call this function again
            window.after(100, update_status_label)
        else:
            # Check if the subprocess has finished
            if render_process.poll() is not None:
                status_label.config(text="Rendering completed!")

    for scene in scene_list:
        scene_file = scene.file
        output_folder = scene.output_folder
        frame_start = scene.frame_start
        frame_end = scene.frame_end

        # Convert the output folder path to an absolute path
        if not output_folder:
            blend_dir = os.path.dirname(scene_file)
            output_folder = os.path.join(blend_dir, 'output')

        output_folder = os.path.abspath(output_folder)

        render_command = [
            blender_executable,
            '-b', scene_file,
            '-o', os.path.join(output_folder, "frame_####"),
            '-s', str(frame_start),
            '-e', str(frame_end),
            '-a',
            '-F', 'PNG',
            '-x', '1',
        ]

        try:
            render_process = subprocess.Popen(render_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            update_status_label()

        except subprocess.CalledProcessError as e:
            messagebox.showerror("RenderError", "An error occurred during rendering. Please check the console output for more information.")
            console_output_text = f"Error during rendering: {e.stderr}"
            status_label.config(text="Aborted due to error.")
            return
        except FileNotFoundError as e:
            messagebox.showerror("ExeError", "The selected blender executable does not exist. Please select a valid blender executable.")
            status_label.config(text="Aborted due to error.")
            return
        except Exception as e:
            messagebox.showerror("InternalError", "An internal error occurred during rendering:" + "\n" + str(e))
            console_output_text = f"Error during rendering: {e}"
            status_label.config(text="Aborted due to error.")
            return

    """ for i in output_entry:
        blenderoutput = blenderoutput + "\n" + i
    console_output_text = blenderoutput """
    # Update the console output widget
    console_output.delete("1.0", tk.END)
    console_output.insert(tk.END, console_output_text)

    status_label.config(text="Rendering completed!")
    messagebox.showinfo("RenderComplete", "Rendering completed!")
    
    # Check if the shutdown option is selected
    if shutdown_var.get() == 1:
        shutdown_command = "shutdown /s /t 0"
        subprocess.run(shutdown_command, shell=True)

config = configparser.ConfigParser()
config.read('settings.ini')

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
    frame_start = int(frame_start_entry.get())
    frame_end = int(frame_end_entry.get())

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
