# abcapstonefa25team1/frontend/gui/app.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import font as tkfont
from pathlib import Path
import base64
import binascii
import threading
import io
import sys
from typing import Optional, Tuple, Iterable

# Optional TTS for status announcements (screen-reader-like feedback)
try:
    import pyttsx3  # pip install pyttsx3 (optional)
    _HAS_TTS = True
except Exception:
    pyttsx3 = None
    _HAS_TTS = False

repoRoot = Path(__file__).resolve().parents[3]
if str(repoRoot) not in sys.path:
    sys.path.insert(0, str(repoRoot))


from abcapstonefa25team1.backend.rsa.RSA_encrypt import RSA
from abcapstonefa25team1.backend.utils.read_write import (
    read_file, write_file, write_encrypted_binary, read_encrypted_binary
)

# --- Optional: Classical/Quantum Shor’s (safe import; toggle auto-disables if unavailable)
try:
    from abcapstonefa25team1.backend.quantum import classical_shors, quantum_shors
    _HAS_SHORS = True
except Exception:
    classical_shors = quantum_shors = None
    _HAS_SHORS = False

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
        self.geometry("980x640")
        self.minsize(880, 560)

        # === Accessibility: font scaling (bounded), named fonts, shortcuts ===
        self.MIN_FONT_SIZE = 9
        self.MAX_FONT_SIZE = 22
        self.fontSizeVar = tk.IntVar(value=11)

        self.uiFont     = tkfont.nametofont("TkDefaultFont")
        self.textFont   = tkfont.nametofont("TkTextFont")
        self.fixedFont  = tkfont.nametofont("TkFixedFont")
        for f in (self.uiFont, self.textFont, self.fixedFont):
            f.configure(size=self.fontSizeVar.get())

        self.fontSizeVar.trace_add("write", lambda *_: self.applyFontScale())
        # Keyboard shortcuts (font + primary actions)
        self.bindAllShortcuts()

        # Optional speech engine for status announcements
        self.tts = pyttsx3.init() if _HAS_TTS else None
        if self.tts:
            try:
                self.tts.setProperty("rate", min(200, int(self.tts.getProperty("rate"))))
                self.tts.setProperty("volume", 1.0)
            except Exception:
                pass

        # Runtime crypto state
        self.rsa = RSA()
        self.publicKey = None    # (e, n)
        self.privateKey = None   # (d, n)

        # Classical/Quantum state (UI toggle + instances)
        self.useClassical = tk.BooleanVar(value=True)  # True => Classical, False => Quantum
        self.classicalShors = None
        self.quantumShors = None
        if _HAS_SHORS:
            try:
                self.classicalShors = classical_shors.Classical_Shors()
            except Exception:
                self.classicalShors = None
            try:
                self.quantumShors = quantum_shors.Quantum_Shors()
            except Exception:
                self.quantumShors = None
        else:
            self.useClassical.set(True)

        # Root Grid Configuration
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container = ttk.Frame(self, padding=16)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        # Main area
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
        # Make Text focus visually obvious
        self.inputText.configure(highlightthickness=2, highlightcolor="#0B5FFF", highlightbackground="#C8D8FF")
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
        self.outputText.configure(highlightthickness=2, highlightcolor="#0B5FFF", highlightbackground="#C8D8FF")

        # Action Row
        # Action Row
        actions = ttk.Frame(container)
        actions.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        actions.columnconfigure(0, weight=0)
        actions.columnconfigure(1, weight=1)
        for i in (2, 3, 4, 5, 6):
            actions.columnconfigure(i, weight=0)

        ttk.Label(actions, text="File:").grid(row=0, column=0, sticky="w")

        self.filePathVar = tk.StringVar()
        self.filePathEntry = ttk.Entry(actions, textvariable=self.filePathVar, state="readonly")
        self.filePathEntry.grid(row=0, column=1, sticky="ew")

        self.browseBtn = ttk.Button(actions, text="Browse… (Ctrl+O)", command=self.browseFile)
        self.browseBtn.grid(row=0, column=2, padx=(8, 0))

        self.generateKeysBtn = ttk.Button(actions, text="Generate Keys (Ctrl+G)", command=self.handleGenerateKeys)
        self.generateKeysBtn.grid(row=0, column=3, padx=(16, 0))

        self.encryptBtn = ttk.Button(actions, text="Encrypt (Ctrl+E)", command=self.handleEncrypt)
        self.encryptBtn.grid(row=0, column=4, padx=(16, 8))

        self.decryptBtn = ttk.Button(actions, text="Decrypt (Ctrl+D)", command=self.handleDecrypt)
        self.decryptBtn.grid(row=0, column=5)

        # Factoring method toggle with clearer label
        self.methodToggle = ttk.Checkbutton(
            actions,
            text="Factoring method: Classical",
            variable=self.useClassical,
            command=self.onMethodToggled
        )
        self.methodToggle.grid(row=0, column=6, padx=(16, 0))

        # Status line (used for announcements; also shown in TTS if available)
        self.keyBanner = ttk.Label(actions, text="No keys loaded", foreground="#222")
        self.keyBanner.grid(row=1, column=0, columnspan=7, sticky="w", pady=(6, 0))

        # If Shor's modules missing, dim/disable the toggle
        if not (self.classicalShors or self.quantumShors):
            self.methodToggle.state(["disabled"])
            self.methodToggle.configure(text="Factoring method: Classical (Shor's unavailable)")

        self.applyStyle()       # includes high-contrast focus ring for ttk widgets
        self.filePathVar.trace_add("write", lambda *args: self.updateActionStates())
        self.updateActionStates()
        self.onMethodToggled()
        self.announceStatus("Ready. Press Ctrl+O to choose a file.")

    # ===== Accessibility: font scaling, action shortcuts, visible focus =====
    def setFontSize(self, newSize: int):
        clamped = max(self.MIN_FONT_SIZE, min(self.MAX_FONT_SIZE, int(newSize)))
        if clamped != self.fontSizeVar.get():
            self.fontSizeVar.set(clamped)  # triggers applyFontScale via trace
        else:
            bound = "minimum" if newSize < self.fontSizeVar.get() else "maximum"
            self.showTempStatus(f"Font size {bound} reached ({clamped})")
            self.announceStatus(f"Font size {bound} reached")

    def applyFontScale(self):
        size = int(self.fontSizeVar.get())
        for f in (self.uiFont, self.textFont, self.fixedFont):
            try:
                f.configure(size=size)
            except tk.TclError:
                pass
        self.update_idletasks()

    def increaseFont(self):
        self.setFontSize(self.fontSizeVar.get() + 1)

    def decreaseFont(self):
        self.setFontSize(self.fontSizeVar.get() - 1)

    def onIncreaseFont(self, event=None):
        self.increaseFont()
        return "break"

    def onDecreaseFont(self, event=None):
        self.decreaseFont()
        return "break"

    def bindAllShortcuts(self):
        # Font scale: multiple sequences for reliability; return "break" to avoid Text eating it
        for seq in ("<Control-equal>", "<Control-plus>", "<Control-Shift-equal>", "<Control-Shift-plus>", "<Control-KP_Add>"):
            self.bind_all(seq, self.onIncreaseFont, add="+")
        for seq in ("<Control-minus>", "<Control-KP_Subtract>"):
            self.bind_all(seq, self.onDecreaseFont, add="+")
        if sys.platform == "darwin":
            for seq in ("<Command-equal>", "<Command-plus>", "<Command-Shift-equal>"):
                self.bind_all(seq, self.onIncreaseFont, add="+")
            self.bind_all("<Command-minus>", self.onDecreaseFont, add="+")

        # Primary actions: Ctrl+O, Ctrl+G, Ctrl+E, Ctrl+D (+ Command on macOS)
        self.bind_all("<Control-o>", lambda e: (self.browseFile(), "break"), add="+")
        self.bind_all("<Control-g>", lambda e: (self.handleGenerateKeys(), "break"), add="+")
        self.bind_all("<Control-e>", lambda e: (self.handleEncrypt(), "break"), add="+")
        self.bind_all("<Control-d>", lambda e: (self.handleDecrypt(), "break"), add="+")
        if sys.platform == "darwin":
            self.bind_all("<Command-o>", lambda e: (self.browseFile(), "break"), add="+")
            self.bind_all("<Command-g>", lambda e: (self.handleGenerateKeys(), "break"), add="+")
            self.bind_all("<Command-e>", lambda e: (self.handleEncrypt(), "break"), add="+")
            self.bind_all("<Command-d>", lambda e: (self.handleDecrypt(), "break"), add="+")

    def showTempStatus(self, msg: str, ms: int = 900):
        if not hasattr(self, "_statusRestore"):
            self._statusRestore = None
        current = self.keyBanner.cget("text")
        self.keyBanner.configure(text=msg)
        if self._statusRestore:
            self.after_cancel(self._statusRestore)
        self._statusRestore = self.after(ms, lambda: self.keyBanner.configure(text=current))

    def announceStatus(self, msg: str):
        """Visual + optional speech announcement."""
        try:
            self.keyBanner.configure(text=msg)
        except Exception:
            pass
        if self.tts:
            try:
                self.tts.stop()
                self.tts.say(msg)
                self.tts.runAndWait()
            except Exception:
                pass
    # ===== End Accessibility =====

    # UI helpers
    def addScrollbar(self, textWidget: tk.Text, parent: ttk.Frame, row: int):
        scroll = ttk.Scrollbar(parent, command=textWidget.yview)
        textWidget.configure(yscrollcommand=scroll.set)
        scroll.grid(row=row, column=1, sticky="ns")

    def applyStyle(self):
        # Theme + padding
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TButton", padding=(10, 6))
        style.configure("TFrame", background="#f7f7fb")
        style.configure("TLabel", background="#f7f7fb")
        style.configure("TCheckbutton", background="#f7f7fb")

        # High-contrast focus ring for interactive controls
        focusBorder = "#0B5FFF"  
        focusBg     = "#E6F0FF"   
        # Buttons
        style.map("TButton",
            highlightcolor=[("focus", focusBorder)],
            bordercolor=[("focus", focusBorder)],
            background=[("focus", focusBg)]
        )
        # Entry
        style.map("TEntry",
            fieldbackground=[("focus", "#FFFFFF"), ("!focus", "#FFFFFF")],
            bordercolor=[("focus", focusBorder)]
        )
        # Checkbutton
        style.map("TCheckbutton",
            foreground=[("focus", "#000")],
            background=[("focus", focusBg)]
        )

        # Give the read-only path entry a visible border on focus
        try:
            self.filePathEntry.configure(takefocus=True)
        except Exception:
            pass

    def writeOutput(self, text: str):
        self.outputText.configure(state="normal")
        self.outputText.delete("1.0", "end")
        self.outputText.insert("1.0", text)
        self.outputText.see("1.0")

    def getInputText(self) -> str:
        return self.inputText.get("1.0", "end-1c")

    def onInputModified(self, _event=None):
        self.inputText.edit_modified(False)
        self.updateActionStates()

    def isEncSelected(self) -> bool:
        path = (self.filePathVar.get() or "").lower()
        return path.endswith(".enc")

    def inputLooksLikeBase64(self) -> bool:
        text = self.getInputText().strip()
        if not text:
            return False
        compact = "".join(text.split())
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

        # Decrypt enabled if .enc selected OR input looks like base64
        if self.isEncSelected() or self.inputLooksLikeBase64():
            self.decryptBtn.state(["!disabled"])
        else:
            self.decryptBtn.state(["disabled"])

    # Shor's UI
    def onMethodToggled(self):
        # Update label text for clarity
        if self.useClassical.get():
            label = "Factoring method: Classical"
            if self.classicalShors is None:
                if self.quantumShors:
                    self.useClassical.set(False)
                    label = "Factoring method: Quantum"
                else:
                    self.methodToggle.state(["disabled"])
                    label = "Factoring method: Classical (Shor's unavailable)"
        else:
            label = "Factoring method: Quantum"
            if self.quantumShors is None:
                if self.classicalShors:
                    self.useClassical.set(True)
                    label = "Factoring method: Classical"
                else:
                    self.methodToggle.state(["disabled"])
                    label = "Factoring method: Classical (Shor's unavailable)"
        self.methodToggle.configure(text=label)

    # Shor's integration helpers
    @staticmethod
    def _egcd(a: int, b: int) -> Tuple[int, int, int]:
        if a == 0:
            return (b, 0, 1)
        g, y, x = App._egcd(b % a, a)
        return (g, x - (b // a) * y, y)

    @staticmethod
    def _modInv(a: int, m: int) -> int:
        g, x, _ = App._egcd(a, m)
        if g != 1:
            raise ValueError("modular inverse does not exist")
        return x % m

    @staticmethod
    def _normalizeFactors(result) -> Optional[Tuple[int, int]]:
        if result is None:
            return None
        if isinstance(result, (int,)):
            return None
        if isinstance(result, (tuple, list, set)):
            flat: Iterable[int] = []
            flat = [int(x) for x in result if isinstance(x, (int,)) or (isinstance(x, str) and x.isdigit())]
            flat = [x for x in flat if x > 1]
            if len(flat) >= 2:
                return (flat[0], flat[1])
            return None
        return None

    def factorN(self, n: int) -> Optional[Tuple[int, int]]:
        if self.useClassical.get() and self.classicalShors:
            try:
                for meth in ("shors_classical", "run", "factor"):
                    if hasattr(self.classicalShors, meth):
                        res = getattr(self.classicalShors, meth)(n)
                        pair = self._normalizeFactors(res)
                        if pair and pair[0] * pair[1] == n:
                            return pair
            except Exception:
                pass

        if not self.useClassical.get() and self.quantumShors:
            try:
                if hasattr(self.quantumShors, "run_shors_algorithm"):
                    try:
                        res = self.quantumShors.run_shors_algorithm(n, 15)
                    except TypeError:
                        res = self.quantumShors.run_shors_algorithm(n)
                else:
                    res = None
                    for meth in ("run", "factor", "shors_quantum"):
                        if hasattr(self.quantumShors, meth):
                            res = getattr(self.quantumShors, meth)(n)
                            break
                pair = self._normalizeFactors(res)
                if pair and pair[0] * pair[1] == n:
                    return pair
            except Exception:
                pass
        return None

    def computePrivateKeyFromPublicViaShors(self, publicKey: Tuple[int, int]) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        e, n = publicKey
        pq = self.factorN(n)
        if not pq:
            return None
        p, q = pq
        phi = (p - 1) * (q - 1)
        d = self._modInv(e, phi)
        return ( (d, n), (p, q) )

    # Actions
    def browseFile(self):
        path = filedialog.askopenfilename(title="Choose a file")
        if not path:
            return
        self.filePathVar.set(path)
        try:
            if path.lower().endswith(".enc"):
                key = self.privateKey or self.publicKey
                if not key:
                    self.announceStatus("Encrypted file selected. Generate or load keys, then press Decrypt.")
                    messagebox.showinfo(
                        "Encrypted file selected",
                        "This is an encrypted (.enc) file.\n"
                        "Generate or load keys first, then click Decrypt."
                    )
                    self.updateActionStates()
                    return

                _, n = key
                blocks = readEncryptedBinary(path, n)
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
                    "Press Decrypt to recover plaintext."
                )
                self.announceStatus("Encrypted file loaded. Ready to decrypt.")
                self.updateActionStates()
                return

            text = readFile(path)
            if text is None:
                raise IOError("Read returned None")
            self.inputText.delete("1.0", "end")
            self.inputText.insert("1.0", text)
            self.announceStatus("Plaintext file loaded.")

        except UnicodeDecodeError:
            messagebox.showerror(
                "Read error",
                "This file is not UTF-8 text. If it's an encrypted file, "
                "please select the .enc and click Decrypt."
            )
            self.announceStatus("Read error.")
        except Exception as e:
            messagebox.showerror("Read error", f"Couldn't read the file:\n{e}")
            self.announceStatus("Read error.")
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
            self.announceStatus("Keys generated.")
        except Exception as e:
            messagebox.showerror("Key generation error", str(e))
            self.announceStatus("Key generation failed.")
        finally:
            self.updateActionStates()

    def handleEncrypt(self):
        if self.isEncSelected():
            messagebox.showinfo(
                "Already Encrypted",
                "The selected file has a .enc extension and appears to be encrypted.\n"
                "Please choose a plaintext file to encrypt."
            )
            self.announceStatus("Encrypt blocked. File already encrypted.")
            return
        if not self.publicKey:
            messagebox.showwarning("No key", "Generate keys first.")
            self.announceStatus("No keys. Generate keys first.")
            return

        def work():
            try:
                src = self.getInputText()
                blocks = self.rsa.encrypt(src, self.publicKey)
                selected = self.filePathVar.get()
                if selected:
                    outFile = Path(selected).with_suffix(".enc")
                    _, n = self.publicKey
                    writeEncryptedBinary(outFile, blocks, n)

                e, n = self.publicKey
                blockSize = (n.bit_length() + 7) // 8
                buf = io.BytesIO()
                for c in blocks:
                    buf.write(int(c).to_bytes(blockSize, "big"))
                b64 = base64.b64encode(buf.getvalue()).decode("ascii")
                self.writeOutput("[Encrypted base64 preview]\n\n" + b64)
                self.announceStatus("Encryption complete.")
            except Exception as e:
                self.writeOutput(f"[Encrypt error]\n{e}")
                self.announceStatus("Encryption failed.")
            finally:
                self.updateActionStates()

        threading.Thread(target=work, daemon=True).start()

    def handleDecrypt(self):
        if not (self.privateKey or self.publicKey):
            messagebox.showwarning("No key", "Generate keys first (or load e,n / d,n).")
            self.announceStatus("No keys. Generate keys first.")
            return

        def work():
            try:
                if not self.privateKey and self.publicKey:
                    if not (self.classicalShors or self.quantumShors):
                        raise RuntimeError(
                            "Shor's modules are unavailable. Cannot factor n automatically.\n"
                            "Please generate keys (which includes d) or install the Shor's modules."
                        )
                    mode = "Classical" if self.useClassical.get() else "Quantum"
                    self.writeOutput(f"[{mode} Shor's] Attempting to factor n to derive private key...\n")
                    self.announceStatus(f"{mode} factoring started.")
                    res = self.computePrivateKeyFromPublicViaShors(self.publicKey)
                    if not res:
                        raise RuntimeError(f"{mode} Shor's failed to factor n.")
                    (d, n), (p, q) = res
                    self.privateKey = (d, n)
                    e, _ = self.publicKey
                    self.keyBanner.configure(
                        text=f"Public: e={e}, n={n}  |  Private (derived): d={d}  (p={p}, q={q})"
                    )
                    self.writeOutput(f"[{mode} Shor's] Factoring successful.\nDerived d. Proceeding to decrypt...\n")
                    self.announceStatus("Private key derived. Decrypting.")

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

                pt = self.rsa.decrypt(blocks, self.privateKey)
                self.writeOutput(pt)
                self.announceStatus("Decryption complete.")
            except Exception as e:
                self.writeOutput(f"[Decrypt error]\n{e}")
                self.announceStatus("Decryption failed.")
            finally:
                self.updateActionStates()

        threading.Thread(target=work, daemon=True).start()


def main():
    print("Running GUI Version of Application.")
    App().mainloop()


if __name__ == "__main__":
    main()
