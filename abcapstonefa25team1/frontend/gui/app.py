# Function to create a GUI application for file encoding/decoding prototype using Tkinter
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Encoder/Decoder — Prototype")
        self.geometry("980x560")
        self.minsize(860, 520)

        # Root Grid Configuration
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container = ttk.Frame(self, padding=16)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        # Main two-column area
        main = ttk.Frame(container)
        main.grid(row=1, column=0, sticky="nsew")
        for i in (0, 2):
            main.columnconfigure(i, weight=1, uniform="cols")
        main.columnconfigure(1, weight=0)
        main.rowconfigure(0, weight=1)

        # Input Pane
        leftPane = ttk.Frame(main)
        leftPane.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 12))
        leftPane.columnconfigure(0, weight=1)
        leftPane.rowconfigure(4, weight=1)

        # File Display Box
        ttk.Label(leftPane, text="Input").grid(row=3, column=0, sticky="w")
        self.inputText = tk.Text(leftPane, wrap="word", undo=True)
        self.inputText.grid(row=4, column=0, sticky="nsew")
        self._addScrollbar(self.inputText, leftPane, row=4)

        # (REMOVED) File Picker from leftPane so it can sit on the same row as action buttons

        # Middle Arrow
        midPane = ttk.Frame(main)
        midPane.grid(row=0, column=1, rowspan=2, sticky="ns")
        midPane.rowconfigure(0, weight=1)
        midPane.rowconfigure(2, weight=1)
        arrow = ttk.Label(midPane, text="→", font=("Segoe UI", 20))
        arrow.grid(row=1, column=0, pady=8)

        # Output Pane
        rightPane = ttk.Frame(main)
        rightPane.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(12, 0))
        rightPane.columnconfigure(0, weight=1)
        rightPane.rowconfigure(1, weight=1)

        ttk.Label(rightPane, text="Output").grid(row=0, column=0, sticky="w")
        self.outputText = tk.Text(rightPane, wrap="word", state="normal")
        self.outputText.grid(row=1, column=0, sticky="nsew")
        self._addScrollbar(self.outputText, rightPane, row=1)

        # Action Row: file picker + Encrypt/Decrypt on the SAME ROW
        actions = ttk.Frame(container)
        actions.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        # columns: 0 = label, 1 = entry (expands), 2 = browse, 3 = encrypt, 4 = decrypt
        actions.columnconfigure(0, weight=0)
        actions.columnconfigure(1, weight=1)  # make path entry stretch
        actions.columnconfigure(2, weight=0)
        actions.columnconfigure(3, weight=0)
        actions.columnconfigure(4, weight=0)

        ttk.Label(actions, text="File:").grid(row=0, column=0, sticky="w")

        self.filePathVar = tk.StringVar()
        self.filePathEntry = ttk.Entry(actions, textvariable=self.filePathVar, state="readonly")
        self.filePathEntry.grid(row=0, column=1, sticky="ew")

        ttk.Button(actions, text="Browse…", command=self.browseFile).grid(row=0, column=2, padx=(8, 0))
        ttk.Button(actions, text="Encrypt", command=self.handleEncrypt).grid(row=0, column=3, padx=(16, 8))
        ttk.Button(actions, text="Decrypt", command=self.handleDecrypt).grid(row=0, column=4)

        # Subtle note for prototype (put it on a second, thin row to avoid crowding)
        ttk.Label(actions, text="Prototype UI", foreground="#666").grid(row=1, column=0, columnspan=5, sticky="w", pady=(6, 0))

        self._applyStyle()

    # Misc helper methods
    def _addScrollbar(self, textWidget: tk.Text, parent: ttk.Frame, row: int):
        scroll = ttk.Scrollbar(parent, command=textWidget.yview)
        textWidget.configure(yscrollcommand=scroll.set)
        scroll.grid(row=row, column=1, sticky="ns")

    def _applyStyle(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TButton", padding=(10, 6))
        style.configure("TFrame", background="#f7f7fb")
        style.configure("TLabel", background="#f7f7fb")

    # File browsing and text handling (prototype behavior)
    def browseFile(self):
        path = filedialog.askopenfilename(title="Choose a text file")
        if not path:
            return
        self.filePathVar.set(path)
        try:
            text = Path(path).read_text(encoding="utf-8", errors="ignore")
            self.inputText.delete("1.0", "end")
            self.inputText.insert("1.0", text)
        except Exception as e:
            messagebox.showerror("Read error", f"Couldn't read the file:\n{e}")

    # Prototype behavior: simply copies input to output with a tag when encrypt button is pressed.
    def handleEncrypt(self):
        src = self.inputText.get("1.0", "end-1c")
        self._writeOutput(f"[Encrypted preview]\n\n{src}")

    # Prototype behavior: simply copies input to output with a tag when decrypt button is pressed.
    def handleDecrypt(self):
        src = self.inputText.get("1.0", "end-1c")
        self._writeOutput(f"[Decrypted preview]\n\n{src}")

    # Helper to write output text area
    def _writeOutput(self, text: str):
        self.outputText.configure(state="normal")
        self.outputText.delete("1.0", "end")
        self.outputText.insert("1.0", text)
        self.outputText.see("1.0")

def main():
    print("Running GUI Version of Application.")
    App().mainloop()
