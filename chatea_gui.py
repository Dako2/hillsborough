import tkinter as tk

def display_strings(string1, string2, string3):
    root = tk.Tk()
    root.title("String Display")

    frame = tk.Frame(root)
    frame.pack()

    label1 = tk.Label(frame, text=string1)
    label1.pack(side=tk.LEFT)

    label2 = tk.Label(frame, text=string2)
    label2.pack(side=tk.LEFT)

    label3 = tk.Label(frame, text=string3)
    label3.pack(side=tk.LEFT)

    root.mainloop()

display_strings("Hellow", "helloe2", "head")