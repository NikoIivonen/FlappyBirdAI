from tkinter import *
from tkinter import messagebox

def edit_params(def_max_gens, def_size, def_lifetime, def_top):

    window = Tk()
    window.title("Edit parameters")

    w = 400
    h = 300

    ww = window.winfo_screenwidth()
    wh = window.winfo_screenheight()

    x = ww/2 - w/2
    y = wh/2 - h/2

    window.geometry('%dx%d+%d+%d' % (w, h, x, y))
    window.config(background="white")

    new_params = [def_max_gens, def_size, def_lifetime, def_top]

    def apply():
        nonlocal new_params
        try:
            gens = int(text_max_gens.get())
            size = int(text_size.get())
            lifetime = int(text_lifetime.get())
            top = int(text_top.get())

            new_params = [gens, size, lifetime, top]

            window.destroy()
        except:
            messagebox.showerror(title="Error", message="Invalid parameters")


    button_apply = Button(window, text="Apply", command=apply)
    button_apply.place(x=170, y=200)

    """"""""""""""""""
    text_max_gens = Entry(window)
    text_max_gens.insert(0, str(def_max_gens))
    text_max_gens.place(x=50, y=100)

    lb_gens = Label(window, text="Max generations")
    lb_gens.place(x=50, y=75)
    """"""""""""""""""
    text_size = Entry(window)
    text_size.insert(0, str(def_size))
    text_size.place(x=50, y=150)

    lb_size = Label(window, text="Population size")
    lb_size.place(x=50, y=125)
    """"""""""""""""""
    text_lifetime = Entry(window)
    text_lifetime.insert(0, str(def_lifetime))
    text_lifetime.place(x=200, y=100)

    lb_life = Label(window, text="Generation lifetime (s)")
    lb_life.place(x=200, y=75)
    """"""""""""""""""
    text_top = Entry(window)
    text_top.insert(0, str(def_top))
    text_top.place(x=200, y=150)

    lb_top = Label(window, text="Pick rate (%)")
    lb_top.place(x=200, y=125)
    """"""""""""""""""

    window.mainloop()

    return new_params


def show_error(message):
    window = Tk()
    window.withdraw()
    messagebox.showerror(title="Error", message=message)
    window.destroy()


def show_info(message):
    window = Tk()
    window.withdraw()
    messagebox.showinfo(title="Info", message=message)
    window.destroy()
