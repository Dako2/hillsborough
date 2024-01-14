import tkinter as tk

def process_input():
    input_string = entry.get()
    # Call your function here to process the input and generate three output strings
    output_strings = [f"{input_string} Output {i+1}" for i in range(3)]
    output_label.config(text="\n".join(output_strings))

root = tk.Tk()
root.title("Chatea GUI")

# Create input entry
entry = tk.Entry(root)
entry.pack()

# Create button
button = tk.Button(root, text="Process", command=process_input)
button.pack()

# Create output label
output_label = tk.Label(root, text="")
output_label.pack()

string1  = "Hello1"
string2  = "Hello2"
string3  = "Hello3"

frame = tk.Frame(root)
frame.pack()

label1 = tk.Label(frame, text=string1)
label1.pack(side=tk.LEFT)

label2 = tk.Label(frame, text=string2)
label2.pack(side=tk.LEFT)

label3 = tk.Label(frame, text=string3)
label3.pack(side=tk.LEFT)

root.mainloop()