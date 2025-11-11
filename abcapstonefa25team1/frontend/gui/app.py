# abcapstonefa25team1/frontend/gui/app.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import base64
import binascii
import threading
import io
import sys

# Allow running this file directly (without -m)
repoRoot = Path(__file__).resolve().parents[3]
if str(repoRoot) not in sys.path:
    sys.path.insert(0, str(repoRoot))

# Backend imports (backend uses snake_case)
from abcapstonefa25team1.backend.rsa.RSA_encrypt import RSA
from abcapstonefa25team1.backend.utils.read_write import (
    read_file, write_file, write_encrypted_binary, read_encrypted_binary
)

# CamelCase wrappers so all new code stays camelCase
def readFile(path: str) -> str:
    return read_file(path)

def writeFile(path: str, text: str) -> None:
    return write_file(path, text)

def writeEncryptedBinary(path: Path, blocks, n: int) -> None:
    return write_encrypted_binary(path, blocks, n)

def readEncryptedBinary(path: str, n: int):
    return read_encrypted_binary(path, n)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Encoder/Decoder — Prototype")
        self.geometry("980x600")
        self.minsize(860, 520)

        # Runtime crypto state
        self.rsa = RSA()
        self.publicKey = None    # (e, n)
        self.privateKey = None   # (d, n)

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

        ttk.Label(leftPane, text="Input").grid(row=3, column=0, sticky="w")
        self.inputText = tk.Text(leftPane, wrap="word", undo=True)
        self.inputText.grid(row=4, column=0, sticky="nsew")
        self.addScrollbar(self.inputText, leftPane, row=4)

        # Watch input changes to update button states
        self.inputText.bind("<<Modified>>", self.onInputModified)

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
        self.addScrollbar(self.outputText, rightPane, row=1)

        # Action Row
        actions = ttk.Frame(container)
        actions.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        actions.columnconfigure(0, weight=0)
        actions.columnconfigure(1, weight=1)
        for i in (2, 3, 4, 5):
            actions.columnconfigure(i, weight=0)

        ttk.Label(actions, text="File:").grid(row=0, column=0, sticky="w")

        self.filePathVar = tk.StringVar()
        self.filePathEntry = ttk.Entry(actions, textvariable=self.filePathVar, state="readonly")
        self.filePathEntry.grid(row=0, column=1, sticky="ew")

        ttk.Button(actions, text="Browse…", command=self.browseFile).grid(row=0, column=2, padx=(8, 0))
        self.generateKeysBtn = ttk.Button(actions, text="Generate Keys", command=self.handleGenerateKeys)
        self.generateKeysBtn.grid(row=0, column=3, padx=(16, 0))
        self.encryptBtn = ttk.Button(actions, text="Encrypt", command=self.handleEncrypt)
        self.encryptBtn.grid(row=0, column=4, padx=(16, 8))
        self.decryptBtn = ttk.Button(actions, text="Decrypt", command=self.handleDecrypt)
        self.decryptBtn.grid(row=0, column=5)

        # Status
        self.keyBanner = ttk.Label(actions, text="No keys loaded", foreground="#666")
        self.keyBanner.grid(row=1, column=0, columnspan=6, sticky="w", pady=(6, 0))

        # React to path changes (to enable/disable buttons)
        self.filePathVar.trace_add("write", lambda *args: self.updateActionStates())
        self.applyStyle()
        self.updateActionStates()

    # UI helpers
    def addScrollbar(self, textWidget: tk.Text, parent: ttk.Frame, row: int):
        scroll = ttk.Scrollbar(parent, command=textWidget.yview)
        textWidget.configure(yscrollcommand=scroll.set)
        scroll.grid(row=row, column=1, sticky="ns")

    def applyStyle(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TButton", padding=(10, 6))
        style.configure("TFrame", background="#f7f7fb")
        style.configure("TLabel", background="#f7f7fb")

    def writeOutput(self, text: str):
        self.outputText.configure(state="normal")
        self.outputText.delete("1.0", "end")
        self.outputText.insert("1.0", text)
        self.outputText.see("1.0")

    def getInputText(self) -> str:
        return self.inputText.get("1.0", "end-1c")

    def onInputModified(self, _event=None):
        # Reset the modified flag and update button states
        self.inputText.edit_modified(False)
        self.updateActionStates()

    def isEncSelected(self) -> bool:
        path = (self.filePathVar.get() or "").lower()
        return path.endswith(".enc")

    def inputLooksLikeBase64(self) -> bool:
        text = self.getInputText().strip()
        if not text:
            return False
        # Remove whitespace for validation
        compact = "".join(text.split())
        # Base64 should be multiple of 4 chars
        if len(compact) % 4 != 0:
            return False
        try:
            base64.b64decode(compact.encode("ascii"), validate=True)
            return True
        except (binascii.Error, UnicodeEncodeError):
            return False

    def updateActionStates(self):
        # Encrypt disabled if a .enc file is selected; otherwise enabled
        if self.isEncSelected():
            self.encryptBtn.state(["disabled"])
        else:
            self.encryptBtn.state(["!disabled"])

        # Decrypt enabled only if:
        #   - a .enc file is selected, OR
        #   - Input contains something that looks like base64
        if self.isEncSelected() or self.inputLooksLikeBase64():
            self.decryptBtn.state(["!disabled"])
        else:
            self.decryptBtn.state(["disabled"])

    # Actions 
    def browseFile(self):
        path = filedialog.askopenfilename(title="Choose a file")
        if not path:
            return
        self.filePathVar.set(path)
        try:
            # .enc files are binary ciphertext; don't read as text
            if path.lower().endswith(".enc"):
                key = self.privateKey or self.publicKey
                if not key:
                    messagebox.showinfo(
                        "Encrypted file selected",
                        "This is an encrypted (.enc) file.\n"
                        "Generate or load keys first, then click Decrypt."
                    )
                    self.updateActionStates()
                    return

                _, n = key
                blocks = readEncryptedBinary(path, n)

                # Base64 preview of raw cipher bytes → show in Input
                blockSize = (n.bit_length() + 7) // 8
                buf = io.BytesIO()
                for c in blocks:
                    buf.write(int(c).to_bytes(blockSize, "big"))
                b64 = base64.b64encode(buf.getvalue()).decode("ascii")

                self.inputText.delete("1.0", "end")
                self.inputText.insert("1.0", b64)
                self.writeOutput(
                    "Selected encrypted file (.enc).\n"
                    "A base64 preview of the raw cipher bytes is shown in Input.\n"
                    "Click Decrypt to recover plaintext."
                )
                self.updateActionStates()
                return

            # Otherwise treat it as a normal text file
            text = readFile(path)
            if text is None:
                raise IOError("Read returned None")
            self.inputText.delete("1.0", "end")
            self.inputText.insert("1.0", text)

        except UnicodeDecodeError:
            messagebox.showerror(
                "Read error",
                "This file is not UTF-8 text. If it's an encrypted file, "
                "please select the .enc and click Decrypt."
            )
        except Exception as e:
            messagebox.showerror("Read error", f"Couldn't read the file:\n{e}")
        finally:
            self.updateActionStates()

    def handleGenerateKeys(self):
        try:
            pub, priv, (p, q) = self.rsa.generate_keys()
            self.publicKey, self.privateKey = pub, priv
            e, n = pub
            d, _ = priv
            self.keyBanner.configure(
                text=f"Public: e={e}, n={n}  |  Private: d={d}  (p={p}, q={q})"
            )
            self.writeOutput("Keys generated.\nYou can now Encrypt/Decrypt.")
        except Exception as e:
            messagebox.showerror("Key generation error", str(e))
        finally:
            self.updateActionStates()

    def handleEncrypt(self):
        # Guard: never encrypt a .enc file
        if self.isEncSelected():
            messagebox.showinfo(
                "Already Encrypted",
                "The selected file has a .enc extension and appears to be encrypted.\n"
                "Please choose a plaintext file to encrypt."
            )
            return
        if not self.publicKey:
            messagebox.showwarning("No key", "Generate keys first.")
            return

        def work():
            try:
                src = self.getInputText()
                blocks = self.rsa.encrypt(src, self.publicKey)  # list[int]

                # Save to .enc next to selected file (if any)
                selected = self.filePathVar.get()
                if selected:
                    outFile = Path(selected).with_suffix(".enc")
                    _, n = self.publicKey
                    writeEncryptedBinary(outFile, blocks, n)

                # Base64 preview for Output
                e, n = self.publicKey
                blockSize = (n.bit_length() + 7) // 8
                buf = io.BytesIO()
                for c in blocks:
                    buf.write(int(c).to_bytes(blockSize, "big"))
                b64 = base64.b64encode(buf.getvalue()).decode("ascii")

                self.writeOutput("[Encrypted base64 preview]\n\n" + b64)
            except Exception as e:
                self.writeOutput(f"[Encrypt error]\n{e}")
            finally:
                self.updateActionStates()

        threading.Thread(target=work, daemon=True).start()

    def handleDecrypt(self):
        if not self.privateKey:
            messagebox.showwarning("No key", "Generate keys first (or load d,n).")
            return

        def work():
            try:
                d, n = self.privateKey
                textArea = self.getInputText().strip()
                blocks = None

                selected = self.filePathVar.get()
                if selected and selected.endswith(".enc"):
                    blocks = readEncryptedBinary(selected, n)
                else:
                    if not textArea:
                        raise ValueError("No ciphertext provided.")
                    raw = base64.b64decode("".join(textArea.split()).encode("ascii"))
                    blockSize = (n.bit_length() + 7) // 8
                    if len(raw) % blockSize != 0:
                        raise ValueError("Cipher length is not a multiple of block size.")
                    blocks = [
                        int.from_bytes(raw[i:i + blockSize], "big")
                        for i in range(0, len(raw), blockSize)
                    ]

                pt = self.rsa.decrypt(blocks, self.privateKey)  # str
                self.writeOutput(pt)
            except Exception as e:
                self.writeOutput(f"[Decrypt error]\n{e}")
            finally:
                self.updateActionStates()

        threading.Thread(target=work, daemon=True).start()


def main():
    print("Running GUI Version of Application.")
    App().mainloop()


if __name__ == "__main__":
    main()
