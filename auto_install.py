import os
import subprocess
import threading
from tkinter import filedialog, Tk, Button, Label, Frame, Checkbutton, IntVar, Canvas, Scrollbar

class AutoInstaller:
    def __init__(self):
        self.file_paths = []
        self.root = Tk()
        self.root.title("Auto Install")
        self.setup_ui()

    def setup_ui(self):
        canvas = Canvas(self.root)
        canvas.pack(side="right", fill="both", expand=True)
        scrollbar = Scrollbar(self.root, command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        self.frame = Frame(canvas)
        canvas.create_window((0,0), window=self.frame, anchor="nw")
        canvas.bind('<Configure>', lambda event: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        button_frame = Frame(self.root)
        button_frame.pack(side="top", fill="x")
        Button(button_frame, text='Add File', command=self.select_file).grid(row=0, column=0, pady=5)
        Button(button_frame, text='Start Installation', command=self.start_installation).grid(row=1, column=0, pady=5)
        self.load_file_paths()
        self.update_label()
        self.root.geometry('650x600')
        self.root.mainloop()

    def install(self, file_path, silent, command):
        try:
            subprocess.run(f"{command}", creationflags=subprocess.CREATE_NEW_CONSOLE, shell=True)
            print(f"{file_path} installed successfully.")
            return True
        except Exception as e:
            print(f"Failed to install {file_path}. Error: {str(e)}")
            return False

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path and not any(file_path == existing_path for existing_path, _, _ in self.file_paths):
            self.file_paths.append((file_path, IntVar(value=1), IntVar(value=1)))
            self.update_label()
            self.save_file_paths()

    def start_installation(self):
        threads = []
        for file_path, silent, enabled in self.file_paths:
            if enabled.get():
                command = self.get_command(file_path, silent.get())
                if command:
                    t = threading.Thread(target=self.install, args=(file_path, silent.get(), command))
                    t.start()
                    threads.append(t)
        for t in threads:
            t.join()

    def get_command(self, file_path, silent):
        if file_path.endswith('.exe'):
            return f"{file_path} /S" if silent else f"{file_path}"
        elif file_path.endswith('.inf'):
            return f"rundll32.exe setupapi,InstallHinfSection DefaultInstall {'132' if silent else '0'} {file_path}"
        elif file_path.endswith('.bat'):
            return f"cmd /c start {file_path}"
        else:
            return None

    def update_state(self, enabled, label):
        label.config(state='normal' if enabled.get() else 'disabled')

    def update_label(self):
        [widget.destroy() for widget in self.frame.winfo_children()]
        for file_path, silent, enabled in self.file_paths:
            self.create_file_frame(file_path, silent, enabled)

    def create_file_frame(self, file_path, silent, enabled):
        file_frame = Frame(self.frame)
        file_frame.pack(fill="x")
        truncated_path = file_path if len(file_path) <= 50 else file_path[:47] + "..."
        label = Label(file_frame, text=truncated_path)
        label.pack(side="left")
        self.update_state(enabled, label)
        Checkbutton(file_frame, text='Silent', variable=silent).pack(side="left")
        checkbutton = Checkbutton(file_frame, text='Enable', variable=enabled)
        checkbutton.pack(side="left")
        checkbutton.config(command=lambda enabled=enabled, label=label: self.update_state(enabled, label))
        Button(file_frame, text='Remove', command=lambda file_path=file_path: self.remove_file(file_path)).pack(side="right")

    def remove_file(self, file_path):
        self.file_paths.remove(next(x for x in self.file_paths if x[0] == file_path))
        self.update_label()
        self.save_file_paths()

    def save_file_paths(self):
        with open('file_paths.txt', 'w') as f:
            [f.write(f"{file_path},{silent.get()},{enabled.get()}\n") for file_path, silent, enabled in self.file_paths]

    def load_file_paths(self):
        if os.path.exists('file_paths.txt'):
            with open('file_paths.txt', 'r') as f:
                self.file_paths.extend([(file_path, IntVar(value=int(silent)), IntVar(value=int(enabled))) for line in f for file_path, silent, enabled in [line.strip().split(',')]])

if __name__ == "__main__":
    AutoInstaller()
