import socket
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Server Configuration
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

class FileTransferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📤 File Transfer Client")
        self.root.geometry("450x300")
        self.root.configure(bg="#f4f4f4")

        self.filename = None
        self.transfer_complete = False
        self.transfer_error = None

        tk.Label(root, text="Choose a file to send",
                 bg="#f4f4f4", font=("Arial", 14))\
          .pack(pady=20)

        tk.Button(root, text="📁 Browse File",
                  command=self.select_file,
                  bg="#4CAF50", fg="white",
                  font=("Arial", 12), width=20)\
          .pack(pady=10)

        self.file_info = tk.Label(root, text="",
                                  bg="#f4f4f4", font=("Arial", 10))
        self.file_info.pack(pady=5)

        self.progress = ttk.Progressbar(
            root, orient=tk.HORIZONTAL,
            length=300, mode='determinate'
        )
        self.progress.pack(pady=20)

        tk.Button(root, text="🚀 Send File",
                  command=self.send_file_thread,
                  bg="#2196F3", fg="white",
                  font=("Arial", 12), width=20)\
          .pack(pady=10)

        # Correctly schedule the callback for transfer status checks
        self.root.after(100, self.check_transfer_status)

    def select_file(self):
        path = filedialog.askopenfilename(parent=self.root)
        if path:
            self.filename = path
            size = os.path.getsize(path)
            self.file_info.config(
                text=f"Selected: {os.path.basename(path)} ({size} bytes)"
            )

    def send_file_thread(self):
        threading.Thread(target=self._send_file, daemon=True).start()

    def _send_file(self):
        if not self.filename:
            self.transfer_error = "No file selected."
            return

        filesize = os.path.getsize(self.filename)
        try:
            s = socket.socket()
            s.connect((SERVER_HOST, SERVER_PORT))
            s.send(f"{self.filename}{SEPARATOR}{filesize}".encode())

            sent = 0
            with open(self.filename, "rb") as f:
                while True:
                    chunk = f.read(BUFFER_SIZE)
                    if not chunk:
                        break
                    s.sendall(chunk)
                    sent += len(chunk)
                    pct = sent / filesize * 100
                    self.progress['value'] = pct
                    self.root.update_idletasks()

            s.close()
            self.transfer_complete = True
        except Exception as e:
            self.transfer_error = str(e)

    def check_transfer_status(self):
        # Check if transfer is complete and show the appropriate message
        if self.transfer_complete:
            self.transfer_complete = False
            messagebox.showinfo(
                "Success",
                "File sent successfully!",
                parent=self.root
            )
            self.progress['value'] = 0

        if self.transfer_error:
            err = self.transfer_error
            self.transfer_error = None
            messagebox.showerror(
                "Error",
                f"Failed to send file:\n{err}",
                parent=self.root
            )
            self.progress['value'] = 0

        # Continue polling the transfer status
        self.root.after(100, self.check_transfer_status)


if __name__ == "__main__":
    root = tk.Tk()
    app = FileTransferApp(root)
    root.mainloop()
