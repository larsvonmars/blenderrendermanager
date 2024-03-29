import tkinter as tk
from tkinter import filedialog
import configparser

def run():
    settings_window = tk.Tk()
    settings_entry = tk.Entry(settings_window, width=50)
    blender_executable_path = ""
    def save_settings():
        global blender_executable_path

        config = configparser.ConfigParser()
        config['Blender'] = {'ExecutablePath': settings_entry.get()}
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)

        blender_executable_path = settings_entry.get()

        with open('settings.ini', 'w') as configfile:
            config.write(configfile)

    def browse_blender_executable():
        file_path = filedialog.askopenfilename(filetypes=[("Blender Executable", "blender.exe")])
        settings_entry.delete(0, tk.END)
        settings_entry.insert(0, file_path)

    settings_window.title("Settings")
    settings_window.resizable(False, False)

    #settings_window.iconbitmap("assets/icon.ico") TODO: Add icon

    # Blender executable path input
    blender_label = tk.Label(settings_window, text="Blender Executable Path:")
    blender_label.pack()

    settings_entry = tk.Entry(settings_window, width=50)
    settings_entry.pack()

    browse_blender_button = tk.Button(settings_window, text="Browse", command=browse_blender_executable)
    browse_blender_button.pack()


    # Save settings button
    save_settings_button = tk.Button(settings_window, text="Save Settings", command=save_settings)
    save_settings_button.pack()

    # Load the Blender executable path from settings.ini if it exists
    config = configparser.ConfigParser()
    config.read('settings.ini')
    if 'Blender' in config and 'ExecutablePath' in config['Blender']:
        settings_entry.insert(0, config['Blender']['ExecutablePath'])
    settings_window.mainloop()