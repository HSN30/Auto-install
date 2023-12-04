import os
import subprocess
from tkinter import filedialog, Tk, Button, Label, Frame, Checkbutton, IntVar, Canvas, Scrollbar, messagebox

def install(file_path, silent, command):
    try:
        subprocess.run(f"{command}", shell=True)
        print(f"{file_path} installed successfully.")
    except Exception as e:
        print(f"Failed to install {file_path}. Error: {str(e)}")

def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        if any(file_path == existing_path for existing_path, _, _ in file_paths):
            messagebox.showwarning("Warning", "File already exists in the list")
        else:
            file_paths.append((file_path, IntVar(value=1), IntVar(value=1)))  # Added enable/disable status
            update_label()
            save_file_paths()

def start_installation():
    for file_path, silent, enabled in file_paths:  # Added enable/disable status
        if enabled.get() and file_path.endswith('.exe'):
            install(file_path, silent.get(), f"{file_path} /S" if silent.get() else f"{file_path}")
        elif enabled.get() and file_path.endswith('.inf'):
            install(file_path, silent.get(), f"rundll32.exe setupapi,InstallHinfSection DefaultInstall {'132' if silent.get() else '0'} {file_path}")
        elif enabled.get() and file_path.endswith('.bat'):
            os.startfile(file_path)

def update_state(enabled, label):
    if enabled.get():
        label.config(state='normal')
    else:
        label.config(state='disabled')

def update_label():
    [widget.destroy() for widget in frame.winfo_children()]
    for file_path, silent, enabled in file_paths:  # Added enable/disable status
        file_frame = Frame(frame)
        file_frame.pack(fill="x")
        truncated_path = file_path if len(file_path) <= 50 else file_path[:47] + "..."
        label = Label(file_frame, text=truncated_path)
        label.pack(side="left")
        update_state(enabled, label)  # Update the state of the label
        Checkbutton(file_frame, text='Silent', variable=silent).pack(side="left")
        checkbutton = Checkbutton(file_frame, text='Enable', variable=enabled)
        checkbutton.pack(side="left")  # Added enable/disable tickbox
        checkbutton.config(command=lambda enabled=enabled, label=label: update_state(enabled, label))  # Update the state of the label when the checkbox is clicked
        Button(file_frame, text='Remove', command=lambda file_path=file_path: remove_file(file_path)).pack(side="right")

def remove_file(file_path):
    file_paths.remove(next(x for x in file_paths if x[0] == file_path))
    update_label()
    save_file_paths()

def save_file_paths():
    with open('file_paths.txt', 'w') as f:
        [f.write(f"{file_path},{silent.get()},{enabled.get()}\n") for file_path, silent, enabled in file_paths]  # Added enable/disable status

def load_file_paths():
    if os.path.exists('file_paths.txt'):
        with open('file_paths.txt', 'r') as f:
            file_paths.extend([(file_path, IntVar(value=int(silent)), IntVar(value=int(enabled))) for line in f for file_path, silent, enabled in [line.strip().split(',')]])  # Added enable/disable status

root = Tk()
root.title("Auto Install")

file_paths = []

# Create a canvas with a scrollbar
canvas = Canvas(root)
canvas.pack(side="right", fill="both", expand=True)  # Pack to the right

scrollbar = Scrollbar(root, command=canvas.yview)
scrollbar.pack(side="right", fill="y")  # Pack to the right

canvas.configure(yscrollcommand=scrollbar.set)

# Create a frame inside the canvas to hold the file paths
frame = Frame(canvas)
canvas.create_window((0,0), window=frame, anchor="nw")

def on_configure(event):
    # Update the scroll region after the canvas and the frame have changed size
    canvas.configure(scrollregion=canvas.bbox('all'))

canvas.bind('<Configure>', on_configure)

# Bind the mouse scroll event to the canvas
def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)

# Create a frame for the buttons
button_frame = Frame(root)
button_frame.pack(side="top", fill="x")

# Add the buttons to the frame
Button(button_frame, text='Add File', command=select_file).grid(row=0, column=0, pady=5)
Button(button_frame, text='Start Installation', command=start_installation).grid(row=1, column=0, pady=5)

load_file_paths()
update_label()

root.geometry('650x600')
root.mainloop()