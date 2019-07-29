from tkinter import *
from tkinter.messagebox import showinfo

def reply():
    showinfo(title='popup', message='Button pressed!')

def strToSortlist(event):
    s = e.get()
    s = s.split()
    s.sort()
    l['text'] = ' '.join(s)

window = Tk()
button = Button(window, text='press', command=reply)
e = Entry(window, width=20)
b = Button(window, text="Преобразовать")
l = Label(window, bg='black', fg='white', width=20)

b.bind('<Button-1>', strToSortlist)

button.pack()
e.pack()
b.pack()
l.pack()
window.mainloop()

