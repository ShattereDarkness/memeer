import tkinter
import tkinter.filedialog
from tkinter import ttk
from tkinter import BOTH, END, LEFT

from PIL import ImageTk, Image
from tkinter import messagebox 
from tkinter.messagebox import showinfo

root = tkinter.Tk()
root.geometry("600x400")
root.iconphoto(False, tkinter.PhotoImage(file='icon.png'))
root.title("Meme'er")

for c in range(0,100):
	ttk.Label(root, text='.').grid(column=c, row=0)
for r in range(0,50):
	ttk.Label(root, text='.').grid(column=0, row=r)

ttk.Label(root, text='first').grid(column=10, row=10, columnspan=5, rowspan=4)

entry_text_entry = ttk.Entry(root, width=10)
entry_text_entry.grid(column=51, row=10, columnspan=60, rowspan=4)



root.mainloop()