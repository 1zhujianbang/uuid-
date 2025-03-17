from gui import UUIDRedirectorGUI
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("650x550")
    app = UUIDRedirectorGUI(root)
    root.mainloop()