from tkinter import Tk, Label, Button, Entry, END, W, E, messagebox, StringVar, Canvas, NW, S, N, Listbox, MULTIPLE
from tkinter.filedialog import askopenfilename, askdirectory
from keras.models import load_model
import numpy
from scipy import ndimage, misc
import os


class GUI:

    def __init__(self, master):
        self.master = master
        master.title("Flower Classifier")

        # Labels
        self.img_path_label = Label(master, text="Path of image dir:")
        self.model_label = Label(master, text="Path of model file:")
        # self.flower_class_text = StringVar()
        # self.flower_class_label = Label(master, textvariable=self.flower_class_text, font='Helvetica 14 bold')

        # Entries
        self.img_dir_path_entry = Entry(master, width=100)
        self.model_path_entry = Entry(master, width=100)

        # Buttons
        self.img_browse_button = Button(master, text="Browse...", command=lambda: self.browse_dir(self.img_dir_path_entry))
        self.model_browse_button = Button(master, text="Browse...",
                                          command=lambda: self.browse_file(self.model_path_entry))
        self.predict_button = Button(master, text="Predict", command=lambda: self.predict(), width=15)

        # table
        self.listBox = Listbox(root, selectmode=MULTIPLE, width=100)  # create Listbox

        # LAYOUT
        self.img_path_label.grid(row=0, column=0)
        self.img_dir_path_entry.grid(row=0, column=1)
        self.img_browse_button.grid(row=0, column=2)
        self.model_label.grid(row=1, column=0)
        self.model_path_entry.grid(row=1, column=1)
        self.model_browse_button.grid(row=1, column=2)
        self.predict_button.grid(row=3, column=0, sticky=W + N)
        # self.flower_class_label.grid(row=3, column=1)
        self.listBox.grid(row=3, column=1, sticky=W)

    def browse_file(self, entry):
        path = askopenfilename()
        if path != '':
            entry.delete(0, END)
            entry.insert(0, path)

    def browse_dir(self, entry):
        path = askdirectory()
        if path != '':
            entry.delete(0, END)
            entry.insert(0, path)

    def predict(self):
        if self.img_dir_path_entry.get() == '' or self.model_path_entry.get() == '':
            messagebox.showerror("Error", "Please enter both paths")
        else:
            # self.flower_class_text.set(self.predict_class(model, self.img_path_entry.get()))
            i = 0
            self.listBox.delete(0, END)
            model = self.load_model_from_path(self.model_path_entry.get())
            for root_path, dirnames, filenames in os.walk(self.img_dir_path_entry.get()):
                for filename in filenames:
                    i += 1
                    row = str(i)+") "+filename+" -> "+self.predict_class(model, os.path.join(root_path, filename))
                    self.listBox.insert(END, row)

    def load_image(self, path):
        image_readed = ndimage.imread(path, mode="RGB")
        image_resized = misc.imresize(image_readed, (128, 128))
        image = numpy.expand_dims(image_resized, axis=0)
        return image

    def load_model_from_path(self, model_path):
        ans = load_model(model_path)
        return ans

    def predict_class(self, model, image_path):
        answer = model.predict(self.load_image(image_path))
        class_dictionary = {0: 'daisy', 1: 'dandelion', 2: 'rose', 3: 'sunflower', 4: 'tulip'}
        one_idx = 0
        for i in range(0, len(answer[0])):
            if answer[0][i] == 1:
                one_idx = i
        return class_dictionary[one_idx]


root = Tk()
my_gui = GUI(root)
root.mainloop()
