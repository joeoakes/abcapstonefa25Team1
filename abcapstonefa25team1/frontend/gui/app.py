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

# Allow running this file directly (without -m)
repoRoot = Path(__file__).resolve().parents[3]
if str(repoRoot) not in sys.path:
    sys.path.insert(0, str(repoRoot))

# Backend imports (backend uses snake_case)
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
        self.geometry("980x620")
        self.minsize(880, 540)

        # === Accessibility: font scaling state (with hard bounds) ===
        self.MIN_FONT_SIZE = 9
        self.MAX_FONT_SIZE = 22
        self.fontSizeVar = tk.IntVar(value=11)

        # Named fonts so ttk + Text widgets scale together
        self.uiFont     = tkfont.nametofont("TkDefaultFont")
        self.textFont   = tkfont.nametofont("TkTextFont")
        self.fixedFont  = tkfont.nametofont("TkFixedFont")
        for f in (self.uiFont, self.textFont, self.fixedFont):
            f.configure(size=self.fontSizeVar.get())

        # React to size changes
        self.fontSizeVar.trace_add("write", lambda *_: self.applyFontScale())
        # Keyboard shortcuts for scaling (no buttons)
        self.bindAllShortcuts()

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

        # Action Row (no A-/A+ buttons)
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

        ttk.Button(actions, text="Browse…", command=self.browseFile).grid(row=0, column=2, padx=(8, 0))
        self.generateKeysBtn = ttk.Button(actions, text="Generate Keys", command=self.handleGenerateKeys)
        self.generateKeysBtn.grid(row=0, column=3, padx=(16, 0))
        self.encryptBtn = ttk.Button(actions, text="Encrypt", command=self.handleEncrypt)
        self.encryptBtn.grid(row=0, column=4, padx=(16, 8))
        self.decryptBtn = ttk.Button(actions, text="Decrypt", command=self.handleDecrypt)
        self.decryptBtn.grid(row=0, column=5)

        # Classical ↔ Quantum toggle (Checkbutton: checked=Classical, unchecked=Quantum)
        self.methodToggle = ttk.Checkbutton(
            actions,
            text="Classical",
            variable=self.useClassical,
            command=self.onMethodToggled
        )
        self.methodToggle.grid(row=0, column=6, padx=(16, 0))

        # Status
        self.keyBanner = ttk.Label(actions, text="No keys loaded", foreground="#666")
        self.keyBanner.grid(row=1, column=0, columnspan=7, sticky="w", pady=(6, 0))

        # If Shor's modules missing, dim/disable the toggle
        if not (self.classicalShors or self.quantumShors):
            self.methodToggle.state(["disabled"])
            self.methodToggle.configure(text="Classical (Shor's unavailable)")

        # React to path changes (to enable/disable buttons)
        self.filePathVar.trace_add("write", lambda *args: self.updateActionStates())
        self.applyStyle()
        self.updateActionStates()
        self.onMethodToggled()

    # ===== Accessibility: font scaling (with bounds + reliable key handling) =====
    def setFontSize(self, newSize: int):
        """Clamp to [MIN_FONT_SIZE, MAX_FONT_SIZE] and apply if changed."""
        clamped = max(self.MIN_FONT_SIZE, min(self.MAX_FONT_SIZE, int(newSize)))
        if clamped != self.fontSizeVar.get():
            self.fontSizeVar.set(clamped)  # triggers applyFontScale via trace
        else:
            # Hit a bound; give quick user feedback
            bound = "min" if newSize < self.fontSizeVar.get() else "max"
            self.showTempStatus(f"Font size {bound} reached ({clamped})")

    def applyFontScale(self):
        """Apply current font size to default Tk/ttk and text fonts."""
        size = int(self.fontSizeVar.get())
        for f in (self.uiFont, self.textFont, self.fixedFont):
            try:
                f.configure(size=size)
            except tk.TclError:
                pass
        # Render immediately so one keypress always shows a change
        self.update_idletasks()

    def increaseFont(self):
        self.setFontSize(self.fontSizeVar.get() + 1)

    def decreaseFont(self):
        self.setFontSize(self.fontSizeVar.get() - 1)

    def onIncreaseFont(self, event=None):
        self.increaseFont()
        return "break"  # prevent focused widgets from swallowing the event

    def onDecreaseFont(self, event=None):
        self.decreaseFont()
        return "break"

    def bindAllShortcuts(self):
        """Bind multiple sequences so Ctrl/⌘ + +/- works across layouts."""
        # Increase
        for seq in ("<Control-equal>", "<Control-plus>", "<Control-Shift-equal>", "<Control-Shift-plus>", "<Control-KP_Add>"):
            self.bind_all(seq, self.onIncreaseFont, add="+")
        # Decrease
        for seq in ("<Control-minus>", "<Control-KP_Subtract>"):
            self.bind_all(seq, self.onDecreaseFont, add="+")
        # macOS Command variants
        if sys.platform == "darwin":
            for seq in ("<Command-equal>", "<Command-plus>", "<Command-Shift-equal>"):
                self.bind_all(seq, self.onIncreaseFont, add="+")
            self.bind_all("<Command-minus>", self.onDecreaseFont, add="+")

    def showTempStatus(self, msg: str, ms: int = 900):
        """Flash a short status message (used for min/max reached)."""
        if not hasattr(self, "_statusRestore"):
            self._statusRestore = None
        # Save current text and set new
        current = self.keyBanner.cget("text")
        self.keyBanner.configure(text=msg)
        # Restore after delay
        if self._statusRestore:
            self.after_cancel(self._statusRestore)
        self._statusRestore = self.after(ms, lambda: self.keyBanner.configure(text=current))
    # ===== End Accessibility =====

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
        if self.useClassical.get():
            if self.classicalShors is None:
                if self.quantumShors:
                    self.useClassical.set(False)
                    self.methodToggle.configure(text="Quantum")
                else:
                    self.methodToggle.state(["disabled"])
                    self.methodToggle.configure(text="Classical (Shor's unavailable)")
            else:
                self.methodToggle.configure(text="Classical")
        else:
            if self.quantumShors is None:
                if self.classicalShors:
                    self.useClassical.set(True)
                    self.methodToggle.configure(text="Classical")
                else:
                    self.methodToggle.state(["disabled"])
                    self.methodToggle.configure(text="Classical (Shor's unavailable)")
            else:
                self.methodToggle.configure(text="Quantum")

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
                    "Click Decrypt to recover plaintext."
                )
                self.updateActionStates()
                return

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
            except Exception as e:
                self.writeOutput(f"[Encrypt error]\n{e}")
            finally:
                self.updateActionStates()

        threading.Thread(target=work, daemon=True).start()

    def handleDecrypt(self):
        if not (self.privateKey or self.publicKey):
            messagebox.showwarning("No key", "Generate keys first (or load e,n / d,n).")
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
