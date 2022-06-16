import os
import json
from tkinter import *
from tkinter.simpledialog import askinteger
from defaultvalues import *

file_matchings = set()

print(os.environ.get("USERNAME"))

if not os.path.isdir("results/evaluated/"):
    os.mkdir("results/evaluated/")

websites = ["www.apotheken-umschau.de",
            "www.behindertenbeauftragter.de",
            "www.brandeins.de",
            "www.lebenshilfe-main-taunus.de",
            "www.mdr.de",
            "www.sozialpolitik.com",
            "www.stadt-koeln.de",
            "www.taz.de"]
string = "\n".join(["0: all websites [Default]"] + [f"{i + 1}: {website}" for i, website in enumerate(websites)])
global filtered_files

# Print out number of already evaluated results per website
website_count = [0 for _ in websites]
set_evaluated = set([file[:-8] for file in os.listdir("results/evaluated")])
for i, website in enumerate(websites):
    with open(os.path.join(dataset_location, f"{website}/parsed_header.json")) as fp:
        header = json.load(fp)
        website_keys = header.keys()

    with open("results/header_matching.json") as fp:
        header = json.load(fp)
        set_matched = set()
        for key in header:
            if key[:-4] in website_keys:
                for file in header[key]:
                    set_matched.add(file.split("--")[0].split("/")[-1])
    print(f"{website}: {len(set_evaluated & set_matched)}")

# prepare the filtering per website
window = Tk()
website_selection = askinteger("Choose website", string, minvalue=0, maxvalue=len(websites), initialvalue=0)
if website_selection:
    with open(os.path.join(dataset_location, f"{websites[website_selection - 1]}/parsed_header.json")) as fp:
        header = json.load(fp)
        website_keys = header.keys()
    with open("results/header_matching.json") as fp:
        header = json.load(fp)
        filtered_files = []
        for key in header:
            if key[:-4] in website_keys:
                for file in header[key]:
                    filtered_files.append(file.split("/")[-1])
elif website_selection==0:
    filtered_files = os.listdir("results/matched")
else:
    exit()

for root, dirs, files in os.walk("results/matched"):
    for file in files:
        if file.endswith(".matches"):
            filepath = os.path.join(root, file)
            combination = file.split('--')[0]
            file_matchings.add(combination)


def get_matches():
    user = os.environ.get("USERNAME")
    for comb in all_files:
        matches = set()
        for file in filtered_files:
            if file.endswith("1.5.matches") and file.startswith(comb):
                with open(os.path.join("results/matched", file), 'r') as fp:
                    doc_matches = json.load(fp)
                    for ind, sentences, sim in doc_matches:
                        sentence_tuple = (sentences[0], sentences[1])
                        matches.add(sentence_tuple)

        for match in matches:
            yield comb, match




def correct():
    if simple_label.get() not in current_results:
        current_results[simple_label.get()] = dict()

    current_results[simple_label.get()][normal_label.get()] = True
    write_results(current_comb, current_results)
    update_sentences()


def incorrect():
    if simple_label.get() not in current_results:
        current_results[simple_label.get()] = dict()

    current_results[simple_label.get()][normal_label.get()] = False
    write_results(current_comb, current_results)
    update_sentences()


def undefined():
    if simple_label.get() not in current_results:
        current_results[simple_label.get()] = dict()

    current_results[simple_label.get()][normal_label.get()] = None
    write_results(current_comb, current_results)
    update_sentences()




def write_results(comb, res):
    with open("results/evaluated/" + comb + ".results", 'w') as fp:
        json.dump(res, fp, indent=2, ensure_ascii=False)


def load_results(comb):
    try:
        with open("results/evaluated/" + comb + ".results", 'r') as fp:
            return json.load(fp)
    except FileNotFoundError:
        return dict()


def update_sentences():
    global current_comb, current_results
    try:
        next_elem = next(match_generator)
        next_simple = next_elem[1][0]
        next_normal = next_elem[1][1]
        new_comb = next_elem[0]
    except StopIteration:
        new_comb = "FINISHED"
        next_simple = "Finished Evaluating All Pairs"
        next_normal = "No more work to do :)"
        buttonYes['state'] = 'disabled'
        buttonNo['state'] = 'disabled'
        buttonUndefined['state'] = 'disabled'

    if current_comb != new_comb:
        if current_comb != "":
            current_results["finished"] = True
            write_results(current_comb, current_results)
        current_comb = new_comb
        current_results = load_results(current_comb)

    if "finished" in current_results:
        update_sentences()
        return

    if str(next_simple) in current_results:
        if str(next_normal) in current_results[next_simple]:
            print("Already evaluated!")
            update_sentences()
            return

    simple_label.set(next_simple)
    normal_label.set(next_normal)


window.title("Evaluate results of sentence matching")

window.geometry('700x200')

match_generator = get_matches()

simple_label = StringVar()
normal_label = StringVar()

current_comb = ""
current_results = dict()

buttonYes = Button(text="Similar", command=correct)
buttonNo = Button(text="Not similar", command=incorrect)
buttonUndefined = Button(text="Undefined", command=undefined)

for i in range(3):
    window.columnconfigure(i, weight=1, minsize=75)
    window.rowconfigure(i, weight=1, minsize=50)

update_sentences()

labelSimpleSentence = Label(textvariable=simple_label, wraplength=700, bg='white', font=('Helvetica 14'))

labelSimpleSentence.grid(column=0, row=0, columnspan=3)

labelNormalSentence = Label(textvariable=normal_label, wraplength=700, bg='white', font=('Helvetica 14'))

labelNormalSentence.grid(column=0, row=1, columnspan=3)

buttonYes.grid(column=0, row=2)
buttonNo.grid(column=1, row=2)
buttonUndefined.grid(column=2, row=2)

window.mainloop()
