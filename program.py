# Chen Wang 672409
# COMP90059 2017 Project 2
# 2017-02-26

import numpy as np
import os, re
import string
from collections import Counter
import codecs
from edit_distance import levenshtein
from fuzzy_match import FuzzyMatcher

coding_table = {'A': '0', 'E': '0', 'H': '0', 'I': '0',
                'O': '0', 'U': '0', 'W': '0', 'Y': '0',
                'B': '1', 'F': '1', 'P': '1', 'V': '1',
                'C': '2', 'G': '2', 'J': '2', 'K': '2',
                'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
                'D': '3', 'T': '3', 'L': '4', 'M': '5',
                'N': '5', 'R': '6'}

DICT_FILE = '/usr/share/dict/words'
dictionary = set([word.lower() for word in open(DICT_FILE).read().split()])

search_path = "documents"


def word_normalize(word) -> str:
    # remove punctuation characters
    punctuation_remover = str.maketrans('', '', string.punctuation)
    word = word.lower().translate(punctuation_remover)
    # just keep english characters
    word = re.sub("[^a-zA-Z]", "", word).strip()
    return word


def soundex(word):
    ''' Compute the soundex code for the word'''

    ''' replace characters with digits except the first one '''
    prev = None
    word = word_normalize(word)
    try:
        enc = word[0].upper()
        for c in word[1:]:
            letter = coding_table[c.upper()]
            ''' remove 0 and repeated digits '''
            if letter == prev or letter == '0':
                continue
            else:
                enc += letter
            prev = letter

        ''' return the results with 4 characters '''
        if len(enc) < 4:
            enc += '0' * (4 - len(enc))
        else:
            enc = enc[:4]
    except:
        enc = None
    return word, enc

def get_dictionary_soundex() -> dict:
    dictionary_soundex = dict()
    for word in dictionary:
        word, word_soundex = soundex(word)
        try:
            dictionary_soundex[word_soundex].append(word)
        except:
            dictionary_soundex[word_soundex] = []
            dictionary_soundex[word_soundex].append(word)
    return dictionary_soundex

dictionary_soundex = get_dictionary_soundex()

def if_spell_right(word) -> bool:
    if word in dictionary or word.lower() in dictionary:
        return True
    else:
        return False


def word_spell_checker(orig_word, n=3):
    spell_right = False
    similar_words = None
    if if_spell_right(orig_word):
        spell_right = True
    else:
        # if the last character is not alphabetical, remove it
        if re.match(r"\w+\W{1}$", orig_word) is not None:
            word = orig_word[:-1]
            if if_spell_right(word):
                spell_right = True
        else:
            word = orig_word

        if spell_right == False:
            normalized_word, word_soundex = soundex(word)
            word_distances = Counter()
            for dict_word in dictionary_soundex.get(word_soundex, []):
                word_distances[dict_word] = levenshtein(normalized_word, dict_word)

            if len(word_distances) > 0:
                similar_words = word_distances.most_common()[::-1]
                if n < 4:
                    similar_words = similar_words[:n]

    return spell_right, similar_words


def file_spell_checker(filename):
    corrected_content = []
    with codecs.open(filename, 'r', encoding="utf-8") as lines:
        for line in lines:
            if len(line) > 0:
                corrected_line = []
                words = line.split()
                if len(words) > 0:
                    for orig_word in words:
                        spell_right, similar_words = word_spell_checker(orig_word, 3)

                        if spell_right == True:
                            corrected_word = orig_word
                        else:
                            if similar_words is None:
                                # The word is not in the dictionary, but we don't have any alternatives.
                                print("\'%s\'seems to be incorrect. You have following choices:"% orig_word)
                                choose_notice = "1. keep this word\n2. skip this word"
                                choice_num = "x"
                                while choice_num not in ["1", "2"]:
                                    choice_num = input("Your choice is invalid. Please choose again.\n" + choose_notice)
                                if choice_num == 1:
                                    corrected_word = orig_word
                                else:
                                    corrected_word = ''
                            else:
                                is_last_alpha = False
                                if re.match(r"\w+\W{1}$", orig_word) is not None:
                                    is_last_alpha = True
                                    word = orig_word[:-1]
                                else:
                                    word = orig_word

                                # user interface and let user to choose the correct one
                                print("\'%s\' seems to be incorrect. Do you mean?" % orig_word)
                                choose_notice = ''
                                for key, (choice_word, _) in enumerate(similar_words):
                                    choose_notice += "%d. %s\n" % (key+1, choice_word)
                                choose_notice += "4. keep this word\n"
                                choice_num = input(choose_notice)
                                # check whether the chice is correct
                                while choice_num not in ["1", "2", "3", "4"]:
                                    choice_num = input("Your choice is invalid. Please choose again.\n" + choose_notice)
                                
                                try:
                                    corrected_word = similar_words[int(choice_num)-1][0]
                                except:
                                    corrected_word = word

                            if is_last_alpha == True:
                                corrected_word += orig_word[-1]

                        corrected_line.append(corrected_word)

                corrected_content.append(' '.join(corrected_line))

    # write into the *-corrected file
    fpath_name, ftext = os.path.splitext(filename)
    corrected_file = fpath_name + "-corrected" + ftext
    with codecs.open(corrected_file, "w", encoding="utf-8") as f:
        f.write('\n'.join(corrected_content))
    print("======== Finish writing the corrected content into the file %s. ========" % corrected_file)

import string
translator = str.maketrans('', '', string.punctuation)


def search_engine(search_term):
    spell_right, similar_words = word_spell_checker(search_term, 4)
    search_terms = []
    if spell_right == True:
        search_terms.append(search_term)
    else:
        if similar_words is not None:
            print("\'%s\' seems to be incorrect. Do you mean?" % search_term)
            choose_notice = ''
            for key, (choice_word, distance) in enumerate(similar_words[:3]):
                choose_notice += "%d. %s\n" % (key+1, choice_word)
            choose_notice += "4. Show all the related results\n"
            choice_num = input(choose_notice)
            # check whether the chice is correct
            while choice_num not in ["1", "2", "3", "4"]:
                choice_num = input("Your choice is invalid. Please choose again.\n" + choose_notice)

            if choice_num == "4":
                search_terms += [word for (word, distance) in similar_words]
            else:
                search_terms += [word for (word, distance) in similar_words[:int(choice_num)]]
        else:
            search_terms.append(search_term)
            
    search_terms = set([word_normalize(word) for word in search_terms])
    search_result = []
    search_files = os.listdir(search_path)
    for file in search_files:
        if not os.path.isdir(file):
            fpath, fname = os.path.split(file)
            with codecs.open(search_path+"/"+file, 'r', encoding="utf-8") as lines:
                for line in lines:
                    orig_line_words = line.split()
                    line_words = []
                    found = False
                    for line_word in orig_line_words:
                        if word_normalize(line_word) in search_terms:
                            found = True
                            line_words.append(line_word.upper())
                        else:
                            line_words.append(line_word)
                    line = " ".join(line_words)
                    
                    if found:
                        print("%s %s" % (fname, line))


if __name__ == "__main__": 
    while True:
        print("Please choose the module:")
        try:
            choice = int(input("1.Spelling checker 2.Search 3.Fuzzy match 4.Exit\n"))
        except:
            print("Invalid choice! Please input the choice number.")
            continue

        if choice > 4 or choice < 1:
            print("Invalid choice! Please input the choice number.")
            continue
        if choice == 4:
            break
        if choice == 1:
            check_filename = str(input("Write the file name (or file path) that you want to correct any spelling errors: ").strip())
            while os.path.isfile(check_filename) == False:
                check_filename = str(input("Please input the right file name that is accessable: ").strip())
            file_spell_checker(check_filename)
        elif choice == 2:
            search_term = str(input("Please input a term that you want to search: ").strip())
            # term is not blank
            while len(search_term) == 0:
                search_term = str(input("Please input a term that you want to search: ").strip())
            search_engine(search_term)
        elif choice == 3:
            try:
                target_file = str(input("Please input the file that the fuzzy macher will perform on:").strip())
                matcher = FuzzyMatcher(target_file)
                phrase = str(input("Please input the phrase you want to search:").strip())
                print(matcher.match(phrase))
            except FileNotFoundError:
                print("Cannot open the file!")