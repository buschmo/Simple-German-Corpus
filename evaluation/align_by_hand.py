import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import askinteger
import os
import json
import spacy
import re
import pickle
import math
import random
import platform
from pathlib import Path

import matching.utilities as utl
from defaultvalues import *

SHORT = "vt"  # None


class gui:
    def __init__(self, root):
        self.root = root
        self.mainframe = ttk.Frame(root, padding="5", height=720, width=1280)
        self.mainframe.grid(column=0, row=0, sticky="NEWS")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        # Canvas
        self.canvas_left = tk.Canvas(self.mainframe  # , height=720, width=1280
                                     )
        self.canvas_left.grid(column=1, row=1, sticky="NEWS")
        self.canvas_right = tk.Canvas(self.mainframe  # , height=720, width=1280
                                      )
        self.canvas_right.grid(column=2, row=1, sticky="NEWS")

        # Configure sizes of columns and rows in mainframe
        self.mainframe.columnconfigure(1, weight=1)
        self.mainframe.columnconfigure(2, weight=1)
        self.mainframe.rowconfigure(1, weight=1)

        # Titles
        self.left_title = ttk.Label(self.mainframe, text="Normal sentence")
        self.left_title.grid(column=1, row=0, sticky="news")
        self.right_title = ttk.Label(self.mainframe, text="Simple sentence")
        self.right_title.grid(column=2, row=0, sticky="news")
        ttk.Style().configure("used.TLabel", foreground="grey")
        # self.right_title["style"] = "used.TLabel"

        # Scrollbars
        self.scrollbar_left = ttk.Scrollbar(
            self.mainframe, orient=tk.VERTICAL, command=self.canvas_left.yview)
        self.scrollbar_left.grid(column=0, row=1, sticky="NS")
        self.scrollbar_right = ttk.Scrollbar(
            self.mainframe, orient=tk.VERTICAL, command=self.canvas_right.yview)
        self.scrollbar_right.grid(column=3, row=1, sticky="NS")

        # configure scrollbar
        self.canvas_left.configure(yscrollcommand=self.scrollbar_left.set)
        self.canvas_left.bind("<Configure>", self.update_left_canvas_layout)
        self.canvas_right.configure(yscrollcommand=self.scrollbar_right.set)
        self.canvas_right.bind("<Configure>", self.update_right_canvas_layout)

        # Innerframes
        self.leftframe = ttk.Frame(self.canvas_left, padding="5")
        self.leftframe.grid(column=0, row=0, sticky="NEWS")
        self.canvas_left.create_window(
            0, 0, anchor="nw", window=self.leftframe)
        self.canvas_left.columnconfigure(0, weight=1)
        self.canvas_left.rowconfigure(0, weight=1)

        self.rightframe = ttk.Frame(self.canvas_right, padding="5")
        self.rightframe.grid(column=0, row=0, sticky="NEWS")
        self.canvas_right.create_window(
            0, 0, anchor="nw", window=self.rightframe)
        self.canvas_right.columnconfigure(0, weight=1)
        self.canvas_right.rowconfigure(0, weight=1)

        # configure sizes of columns and rows in innerframes
        self.leftframe.columnconfigure(0, weight=1)
        self.leftframe.rowconfigure(0, weight=1)
        self.rightframe.columnconfigure(0, weight=1)
        self.rightframe.rowconfigure(0, weight=1)

        # MouseWheel action
        def bind_mousewheel(widget, command):
            def bind(widget, command):
                widget.bind_all("<MouseWheel>", command)
                widget.bind_all("<Button-4>", command)
                widget.bind_all("<Button-5>", command)

            def unbind(widget):
                widget.unbind_all("<MouseWheel>")
                widget.unbind_all("<Button-4>")
                widget.unbind_all("<Button-5>")
            widget.bind("<Enter>", lambda _: bind(widget, command))
            widget.bind("<Leave>", lambda _: unbind(widget))

        bind_mousewheel(self.canvas_left, self.on_mousewheel_left)
        bind_mousewheel(self.canvas_right, self.on_mousewheel_right)

        self.match_generator = self.get_articles()
        self.pairs = utl.get_article_pairs()

        self.button_progress = tk.Button(
            self.mainframe, text="Show progress", command=self.show_progress)
        self.button_progress.grid(column=1, row=2, sticky="w")

        self.button_proceed = tk.Button(
            self.mainframe, text="Only proceed", command=self.next_website)
        self.button_proceed.grid(column=1, row=2, sticky="e")

        self.button_save = tk.Button(
            self.mainframe, text="Save and proceed", command=self.save)
        self.button_save.grid(column=2, row=2, sticky="e")
        self.next_website()

    def update_left_canvas_layout(self, event):
        self.canvas_left.config(scrollregion=self.canvas_left.bbox("all"))
        wraplength = int(event.width-50)
        for label in self.normal_labels.values():
            label.configure(wraplength=wraplength)

    def update_right_canvas_layout(self, event):
        self.canvas_right.config(scrollregion=self.canvas_right.bbox("all"))
        wraplength = int(event.width-50)
        for label in self.easy_labels:
            label.configure(wraplength=wraplength)

    def on_mousewheel_left(self, event):
        delta = 1
        # make mousewheel work in macOS
        if platform.system() == "Darwin":
            self.canvas_left.yview_scroll(-1 * event.delta, "units")
        else:
            if event.num == 5:
                # scroll down
                self.canvas_left.yview_scroll(delta, "units")
            elif event.num == 4:
                # scroll up
                self.canvas_left.yview_scroll(-delta, "units")
            else:
                self.canvas_left.yview_scroll(
                    int(-1*(event.delta/120)), "units")

    def on_mousewheel_right(self, event):
        delta = 1
        # make mousewheel work in macOS
        if platform.system() == "Darwin":
            self.canvas_right.yview_scroll(-1 * event.delta, "units")
        else:
            if event.num == 5:
                # scroll down
                self.canvas_right.yview_scroll(delta, "units")
            elif event.num == 4:
                # scroll up
                self.canvas_right.yview_scroll(-delta, "units")
            else:
                self.canvas_right.yview_scroll(
                    int(-1*(event.delta/120)), "units")

    def show_progress(self):
        n_aligned = int(len(os.listdir(ground_truth_location))/2)
        n_sample = len(self.pairs_sample)
        print(f"{n_aligned}/{n_sample} already aligned.")

    def get_articles(self):
        path = f"{results_location}/website_samples.pkl"
        if os.path.exists(path):
            print(f"Using presampled sites from {path}")
            # load existing subset
            with open(path, "rb") as fp:
                self.pairs_sample = pickle.load(fp)
        else:
            # sample new 5% subset
            with open(path, "wb") as fp:
                k = math.ceil(len(self.pairs)*0.05)

                # remove already aligned ones
                pairs = [pair for pair in self.pairs if (not os.path.exists(
                    utl.make_hand_aligned_path(pair[0], pair[1])[0]))]
                # relative path instead of absolute
                pairs = [(Path(pair[0]).relative_to(dataset_location), Path(
                    pair[1]).relative_to(dataset_location)) for pair in pairs]

                self.pairs_sample = random.sample(pairs, k)
                pickle.dump(self.pairs_sample, fp)

        for pair in self.pairs_sample:
            if not os.path.exists(utl.make_hand_aligned_path(pair[0], pair[1])[0]):
                yield pair

    def next_website(self):
        try:
            simple_path, normal_path = next(self.match_generator)
        except StopIteration:
            quit()

        # Paths from match_generator are relative to dataset_location
        simple_path = os.path.join(dataset_location, simple_path)
        normal_path = os.path.join(dataset_location, normal_path)

        print(f"New simple file: {os.path.split(simple_path)[1]}")
        print(f"New standard file: {os.path.split(normal_path)[1]}")

        self.save_path_easy, self.save_path_normal = utl.make_hand_aligned_path(
            simple_path, normal_path, short=SHORT)

        # delete old contents
        for child in self.leftframe.winfo_children():
            child.destroy()
        for child in self.rightframe.winfo_children():
            child.destroy()

        # setup new boxes
        wraplength = 600
        with open(simple_path) as fp:
            self.easy_check = []
            self.easy_check_bool = []
            self.easy_labels = []

            # Add easy lines to the right
            self.easy_lines = prep_text(fp.read())
            for i, line in enumerate(self.easy_lines):
                value = tk.BooleanVar(value=False)
                check = ttk.Checkbutton(
                    self.rightframe, text="", variable=value, command=self.pair_to_normal)
                check.grid(column=0, row=i, sticky="NEWS")
                label = ttk.Label(self.rightframe, text=line,
                                  wraplength=wraplength, justify="left")
                label.grid(column=1, row=i, sticky="NEWS")
                self.easy_check_bool.append(value)
                self.easy_check.append(check)
                self.easy_labels.append(label)

        with open(normal_path) as fp:
            self.normal_sentence = tk.StringVar()
            self.alignment = {}
            self.normal_labels = {}
            self.normal_lines = prep_text(fp.read())

            # Add normal lines to the left
            for i, line in enumerate(self.normal_lines):
                radio = tk.Radiobutton(self.leftframe, text="", variable=self.normal_sentence,
                                       value=line, command=self.show_paired_easy)
                radio.grid(column=0, row=i, sticky="news")
                label = ttk.Label(self.leftframe, text=line,
                                  wraplength=wraplength, justify="left")
                label.grid(column=1, row=i, sticky="news")
                self.normal_labels[line] = label
                self.alignment[line] = []
            # set default to first sentence
            self.normal_sentence.set(self.normal_lines[0])

        # print(self.innerframe.winfo_children())
        # for child in self.innerframe.winfo_children():
        #     child.grid_configure(padx=5,pady=5)

    def pair_to_normal(self):
        normal_sentence = self.normal_sentence.get()
        self.alignment[normal_sentence] = []
        for i, line in enumerate(self.easy_lines):
            if self.easy_check_bool[i].get() and self.easy_check[i].instate(["!disabled"]):
                self.alignment[normal_sentence].append(line)
        if len(self.alignment[normal_sentence]):
            self.normal_labels[normal_sentence]["style"] = "used.TLabel"
        else:
            self.normal_labels[normal_sentence]["style"] = "TLabel"

    def show_paired_easy(self):
        normal_sentence = self.normal_sentence.get()
        for i, easy_line in enumerate(self.easy_lines):
            if easy_line in self.alignment[normal_sentence]:
                self.easy_check[i].state(["!disabled"])
            elif self.easy_check_bool[i].get():
                self.easy_check[i].state(["disabled"])

    def save(self):
        with open(self.save_path_easy, "w", encoding="utf-8") as fp_easy, open(self.save_path_normal, "w", encoding="utf-8") as fp_normal:
            for normal in self.alignment:
                for easy in self.alignment[normal]:
                    if not easy.endswith("\n"):
                        easy += "\n"
                    if not normal.endswith("\n"):
                        normal += "\n"
                    fp_easy.write(easy)
                    fp_normal.write(normal)
        self.next_website()

    def quit(self):
        self.root.destroy()


def prep_text(text):
    text = text.replace('\n', ' ')
    text = re.sub('\s+', ' ', text)
    sents = [str(sent) for sent in nlp(text).sents]
    return sents


def choose_website():
    set_aligned = set([file[:-8]
                      for file in os.listdir(ground_truth_location)])
    global website_hashes

    for website in website_hashes:
        set_website = set(website_hashes[website])
        print(f"{website}: {len(set_aligned & set_website)}")

    string = "\n".join(["0: all websites [Default]"] +
                       [f"{i + 1}: {website}" for i, website in enumerate(website_hashes)])
    website_selection = askinteger(
        "Choose website", string, minvalue=0, maxvalue=len(website_hashes), initialvalue=0)

    return website_selection


website_hashes = utl.get_website_hashes()
nlp = spacy.load("de_core_news_lg")

if __name__ == "__main__":
    if not os.path.isdir(ground_truth_location):
        os.makedirs(ground_truth_location)
    root = tk.Tk()
    gui(root)
    root.mainloop()
