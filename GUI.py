import tkinter as tk
from tkinter import Tk, Label, Button, Entry, END, W, E, messagebox, StringVar, Canvas, NW, S, N, Listbox, MULTIPLE, \
    DISABLED
from tkinter.filedialog import askdirectory
import os


class GUI:

    def __init__(self, master):
        self.master = master
        master.title("Naive Bayes Classifier")

        # Members
        self.structure_path = ""
        self.train_path = ""
        self.test_path = ""

        # Labels
        self.directory_path_label = Label(master, text="Directory Path:")
        self.discretization_bins_label = Label(master, text="Discretization Bins:")

        # Vars
        self.directory_path_text = StringVar()
        self.directory_path_text.trace("w", lambda name, index, mode, sv=self.directory_path_text: self.check_path(sv))

        # Entries
        self.directory_path_entry = Entry(master, textvariable=self.directory_path_text, width=50)
        self.discretization_bins_entry = IntEntry(master, width=10)
        self.discretization_bins_entry.set('1')

        # Buttons
        self.browse_button = Button(master, text="Browse", command=lambda: self.browse())
        self.build_button = Button(master, text="Build", state=DISABLED, command=lambda: self.build(), width=20)
        self.classify_button = Button(master, text="Classify", state=DISABLED, command=lambda: self.classify(), width=20)

        # LAYOUT
        self.directory_path_label.grid(row=0, column=0, padx=10, pady=10, sticky=E)
        self.directory_path_entry.grid(row=0, column=1, padx=10, pady=10)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)
        self.discretization_bins_label.grid(row=1, column=0, sticky=E, padx=10, pady=10)
        self.discretization_bins_entry.grid(row=1, column=1, sticky=W, padx=10, pady=10)
        self.build_button.grid(row=2, column=0, columnspan=3,  padx=10, pady=10)
        self.classify_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    def browse(self):
        entry = self.directory_path_entry
        path = askdirectory()
        if path != '':
            entry.delete(0, END)
            entry.insert(0, path)

    def check_path(self, sv):
        if sv.get() != '':
            self.build_button['state'] = 'normal'
        else:
            self.build_button['state'] = 'disabled'
            self.classify_button['state'] = 'disabled'

    def build(self):
        for root_path, dirnames, filenames in os.walk(self.directory_path_entry.get()):
            for filename in filenames:

                # check if file is required
                if filename == 'Structure.txt':
                    if self.structure_path != '':
                        messagebox.showerror("Error", "more than one Structure.txt in directory")
                        return
                    else:
                        self.structure_path = root_path+'\\'+filename
                elif filename == 'train.csv':
                    if self.train_path != '':
                        messagebox.showerror("Error", "more than one train.csv in directory")
                        return
                    else:
                        self.train_path = root_path+'\\'+filename
                elif filename == 'test.csv':
                    if self.test_path != '':
                        messagebox.showerror("Error", "more than one test.csv in directory")
                        return
                    else:
                        self.test_path = root_path+'\\'+filename

        # check that all files were found
        if self.structure_path == '':
            messagebox.showerror("Error", "Structure.txt not found")
            return
        if self.train_path == '':
            messagebox.showerror("Error", "train.csv not found")
            return
        if self.test_path == '':
            messagebox.showerror("Error", "test.csv not found")
            return

        self.build_model()

    def build_model(self):
        # todo: build naive bayes model here
        # print('all files found\n')
        # with open(self.structure_path, 'r') as structure:
        #     for line in structure:
        #         print(line)

        # if the building of the model was successful
        messagebox.showinfo("Message", "Naive bayes model built successfully!")
        self.build_button['state'] = 'disabled'
        self.classify_button['state'] = 'normal'


class IntEntry(tk.Entry):
    def __init__(self, master=None, **kwargs):
        self.var = tk.StringVar()
        tk.Entry.__init__(self, master, textvariable=self.var, **kwargs)
        self.old_value = ''
        self.var.trace('w', self.check)
        self.get, self.set = self.var.get, self.var.set

    def check(self, *args):
        if self.get().isdigit():
            # the current value is only digits; allow this
            if self.get()[0] == '0':
                self.set(self.old_value)
            else:
                self.old_value = self.get()
        else:
            # there's non-digit characters in the input; reject this
            self.set(self.old_value)


root = Tk()
my_gui = GUI(root)
root.mainloop()
