import re
import string
import pysbd
import os
from pathlib import Path


PRONOUNS = ["I", "you", "he", "she", "they", "it", "him", "her", "them", "his", "hers", "their", "its", "himself", "herself", "themselves", "himself", "herself", "themselves", "himself", "herself", "themselves"]



def contains_words(sentence, words):
    sentence = sentence.lower()
    words = [word.lower() for word in words]
    for word in words:
        if re.search(r'\b' + re.escape(word) + r'\b', sentence):
            return True
    return False


def check_english_strings(lines):
    words = [" the ", " is ", " it ", " in ", " on ", " with"]
    joined = " ".join(lines)
    joined = joined.lower()
    if all([val in joined for val in words]):
        return True
    return False


def contains_singlequote_patterns(sent):
    # Check for quotes with single quotes
    # Pattern for single quote followed by a capital letter
    pattern1 = r"'\[A-Z]"
    # Pattern for a punctuation mark (.,;!? and others) followed by a single quote
    pattern2 = r"[.,;!?]'"
    return bool(re.search(pattern1, sent)) or bool(re.search(pattern2, sent))

def contains_patterns(sent):
    pattern = r'^[IVXLCDM]+\.\s.{0,53}$'
    pattern2 = r"CHAPTER|Chapter|VOLUME|Volume|PART|SECTION"
    return bool(re.search(pattern2, sent)) or bool(re.search(pattern, sent))

def cleaner(text):
    # full text,  not lines.
    # replace quotes first
    pattern1 = r"^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]+$" # digitletter codes - do first
    pattern2 = r'^\[Illustration[^]]*\].*$'  # illos - needs multiline
    pattern3 = r'(?im)^Chapter.*\n+.{1,50}$' # # chapter plus newline(s) and name of it
    pattern5 = r'(?im)^Chapter.*$' # chapter followed by name of it, do after 3 
    pattern6 = r'(?im)^Volume.*$' # chapter followed by name of it, do after 3
    pattern8 = r'^PART.+$' # part labels
    pattern7 = r'^[\s*]+$' # asterisks, use multiline
    #pattern4 = r'^["].*$' # line starting dialogue, after quote fix, needs multiline flag
    pattern9 = r'^-?\d+(\.\d+)?$' # line with only a number on it
    pattern10 = r'\[Image unavailable\.\]'
    pattern11 = r'^[\dA-Z,:&.\s\"\-]{0,50}$' # P&P pub info in between volumes
    pattern12 = r'^London:$'  # P&P
    pattern14 = r'^[IVXLCDM]+\.\s.{0,53}$'
    pattern15 = r'^See page \d+\.$'
    pattern16 = r'^(.{1,50})\n\n(.{1,50})$'  # poetry or song line attempt 2 short lines
    pattern13 = r'^.*"$' # end of dialogue line - scrappy
    #pattern17 = r";.*;" # multiple semicolons are awful
    
    text = re.sub(r'[“”]', '"', text)
    text = re.sub(r'[’]', "'", text)
    text = re.sub(pattern1, '', text, flags=re.MULTILINE)
    text = re.sub(pattern2, '', text, flags=re.MULTILINE)
    text = re.sub(pattern3, '', text) # has newlines so don't use multiline?
    #text = re.sub(pattern4, '', text, flags=re.MULTILINE) # remove dialogue lines 
    text = re.sub(pattern5, '', text, flags=re.MULTILINE)
    text = re.sub(pattern6, '', text, flags=re.MULTILINE)
    text = re.sub(pattern7, '', text, flags=re.MULTILINE) # asterisk lines
    text = re.sub(pattern8, '', text, flags=re.MULTILINE)
    text = re.sub(pattern9, '', text, flags=re.MULTILINE)
    text = re.sub(pattern10, '', text)
    text = re.sub(pattern11, '', text, flags=re.MULTILINE)
    text = re.sub(pattern12, '', text, flags=re.MULTILINE)
    text = re.sub(pattern13, '', text, flags=re.MULTILINE)
    text = re.sub(pattern15, '', text, flags=re.MULTILINE)
    text = re.sub(pattern16, '', text, flags=re.MULTILINE)
    text = re.sub(pattern14, '', text, flags=re.MULTILINE)
    #text = re.sub(pattern17, '', text, flags=re.MULTILINE)
    return text 


def clean_text_for_web(text):
    # Strip initial punctuation
    text = text.strip()
    text = re.sub(r'^[^\w\s]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    
    # Replace duplicated commas
    text = re.sub(r',{2,}', ',', text)
    
    # Turn double dashes into em dash
    text = text.replace(",--", ", --")
    text = text.replace('--', '\u2014')
    
    # Replace straight quotes with curly quotes
    text = text.replace('"', '\u201c')  # Opening double quote
    text = text.replace('"', '\u201d')  # Closing double quote
    text = text.replace("'", '\u2018')  # Opening single quote
    text = text.replace("'", '\u2019')  # Closing single quote
     # Remove underscores
    text = text.replace('_', '')
    
    # Remove angle brackets
    text = text.replace('<', '').replace('>', '')
    
    return text

def simple_removals(lines):
    clean = []
    for line in lines:
        text = line.strip()
        text = re.sub(r'^[^\w\s]+', '', text)
        text = re.sub(r'\s+', ' ', text)
        # Replace duplicated commas
        text = re.sub(r',{2,}', ',', text)
        # Remove underscores
        text = text.replace('_', '')
        # Remove angle brackets
        text = text.replace('<', '').replace('>', '')
        clean.append(text)
    return clean


def count_punctuation_and_numbers(text):
    # Count punctuation
    punctuation_count = sum(1 for char in text if char in string.punctuation)
    
    # Count numbers
    number_count = sum(1 for char in text if char.isdigit())
    
    # Count specific types of punctuation
    period_count = text.count('.')
    
    # Count groups of numbers (e.g., "123" counts as one group)
    number_group_count = len(re.findall(r'\d+', text))
    alphabetic_chars = [char for char in text if char.isalpha()]
    is_all_caps = all(char.isupper() for char in alphabetic_chars) if alphabetic_chars else False
    
    return {
        'total_punctuation': punctuation_count,
        'total_numbers': number_count,
        'periods': period_count,
        'number_groups': number_group_count,
        'all_caps': is_all_caps
    }


def detect_punct_numbers(sentences):
    cutoffs = {
        'total_punctuation': 6,
        'total_numbers': 2,
        'periods': 3,
        'number_groups': 2,
        'all_caps': True
    }

    clean = []
    for sent in sentences:
        result = count_punctuation_and_numbers(sent)
        if result['total_punctuation'] > cutoffs['total_punctuation']:
            continue
        if result['total_numbers'] > cutoffs['total_numbers']:
            continue
        if result['periods'] > cutoffs['periods']:
            continue
        if result['number_groups'] > cutoffs['number_groups']:
            continue
        if result['all_caps']:
            continue
        clean.append(sent)
    return clean


def remove_dialogue_etc(sents, remove_dialogue=True, min_len=80, max_len=310):
    # short but not too short, non dialogue, not metatexty
    clean = []
    for sent in sents:
        # no dialogue
        if remove_dialogue:
            if "\"" in sent:  # dialogue lines
                continue
            if contains_words(sent, ['said', 'says', 'shouted', 'exclaimed', 'asked', 'wondered', 'cried']):
                continue
            if contains_singlequote_patterns(sent):
                continue
        if len(sent.strip()) < min_len or len(sent.strip()) > max_len: # short are bad, so are long
            continue
        if "["  in sent or "]" in sent: # no bracket lines
            continue
        if "{" in sent or "}" in sent:
            continue
        if contains_patterns(sent):
            continue
        if sent.lower() == sent.upper(): # all lower or upper case
            continue
        if sent.strip() == "":  # remove empty lines
            continue
        clean.append(sent.strip())
    return clean


def read_book(path):
    """Will paragraphize if double newline.
    """
    with open(path) as handle:
        text = handle.read()
        text = text.replace("\n\n", "<para>").replace("\n", " ").replace("<para>", "\n")
        return text
    
def make_para_sents(text):
    # after read book
    paras = text.split("\n\n")
    sents = []
    for para in paras:
        seg = pysbd.Segmenter(language='en', clean=False)
        sents.append([x.strip() for x in seg.segment(para)])
    return sents

def write_sent_per_line(sentslist, dirname="data/sents/", filename="out.txt"):
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(f"{dirname}{filename}", 'w') as handle:
        if not sentslist or len(sentslist) == 0:
            print("No sentlist found.")
            return
        if type(sentslist[0]) == list:
            for sents in sentslist:
                for sent in sents:
                    handle.write(sent + "\n")
                handle.write("\n\n") # keeping the paras together?
        if type(sentslist[0]) == str:
            for sent in sentslist:
                handle.write(sent + "\n")
    print('wrote', filename)

def make_filename(path, strip="_raw", new_ext="_sents.txt"):
    base = Path(path).stem
    base = base.rstrip(strip)
    new = base + new_ext
    return new

def read_sents(path):
    ## non-empty strings returned, no other filtering
    with open(path) as handle:
        lines = handle.readlines()
        lines = [line.strip() for line in lines if line.strip()]
    return lines


def cleaning_operations(lines):
    lines = detect_punct_numbers(lines)
    #print('after detect_punct_numbers', len(lines))
    lines = remove_dialogue_etc(lines, remove_dialogue=False, min_len=70, max_len=320)
    #print('after remove_dialogue_etc', len(lines))
    return lines


def run_dir_sents(files, read_from_path = "data/text/", write_to_path="data/sents"):
    if not os.path.exists(write_to_path):
        os.makedirs(write_to_path)
    for file in files:
        print(file)
        text = read_book(file)
        new_filename = make_filename(file, strip="_clean", new_ext="_sents.txt")
        text = cleaner(text)
        paras = make_para_sents(text)
        write_sent_per_line(paras, dirname=write_to_path, filename=new_filename)

def run_dir_filter_sents(files, read_from_path = "data/sents/", write_to_path="data/filt-sents"):
    ## Expects to work on sentence files.
    if not os.path.exists(write_to_path):
        os.makedirs(write_to_path)
    for file in files:
        sents = read_sents(file)
        if not check_english_strings(sents):
            print("not english", file)
            continue
        newsents = simple_removals(sents)
        newsents = cleaning_operations(newsents)
        new_filename = make_filename(file, strip="_sents", new_ext="_sents_filt.txt")
        write_sent_per_line(newsents, dirname=write_to_path, filename=new_filename)



# raw -> clean -> sents -> filtered
#myfiles = [str(file) for file in Path("top100_clean/").glob("*.txt")]
#run_dir_sents(myfiles, read_from_path="top100_clean/", write_to_path="top100_sents/")
myfiles = [str(file) for file in Path("top100_sents/").glob("*.txt")]
run_dir_filter_sents(myfiles, read_from_path="top100_sents/", write_to_path="top100_sents_filtered/")