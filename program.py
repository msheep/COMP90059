# Chen Wang 672409
# COMP90059 2017 Project 2
# 2017-02-26

# /Users/eunice/Documents/essay.txt

import numpy as np
import os, re
import string
from collections import Counter

coding_table = {'A': '0', 'E': '0', 'H': '0', 'I': '0',
                'O': '0', 'U': '0', 'W': '0', 'Y': '0',
                'B': '1', 'F': '1', 'P': '1', 'V': '1',
                'C': '2', 'G': '2', 'J': '2', 'K': '2',
                'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
                'D': '3', 'T': '3', 'L': '4', 'M': '5',
                'N': '5', 'R': '6'}

DICT_FILE = '/usr/share/dict/words'
dictionary = set(open(DICT_FILE).read().split())

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
        print(word)
        enc = None
    return word, enc


def levenshtein(s1, s2):
    s1 = s1.lower()
    s2 = s2.lower()
    columns = len(s1) + 1
    rows = len(s2) + 1

    '''Construct a matrix with preset value of 0'''
    matrix = np.zeros([columns, rows], np.int32)

    for i in range(columns):
        matrix[i][0] = i
    for j in range(rows):
        matrix[0][j] = j

    for i in range(1, columns):
        for j in range(1, rows):

            delete_cost = matrix[i-1][j] + 1
            insert_cost = matrix[i][j-1] + 1

            if s1[i-1] != s2[j-1]:
                replace_cost = matrix[i-1][j-1] + 1
            else:
                replace_cost = matrix[i-1][j-1]

            matrix[i][j] = min(insert_cost, delete_cost, replace_cost)
    
    return matrix[columns-1][rows-1]


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


def if_spell_right(word) -> bool:
    if word in dictionary or word.lower() in dictionary:
        return True
    else:
        return False

def spell_checker(filename):
    punctuation_remover = str.maketrans('', '', string.punctuation)
    dictionary_soundex = get_dictionary_soundex()

    corrected_content = []
    with open(filename, 'r') as lines:
        for line in lines:
            if len(line) > 0:
                corrected_line = []
                words = line.split()
                if len(words) > 0:
                    for orig_word in words:
                        if if_spell_right(orig_word):
                            corrected_line.append(orig_word)
                        else:
                            # if the last character is not alphabetical, remove it
                            last_is_alpha = False
                            if re.match(r"\w+\W{1}$", orig_word) is not None:
                                last_is_alpha = True
                                word = orig_word[:-1]
                                if if_spell_right(word):
                                    corrected_line.append(orig_word)
                                    continue
                            else:
                                word = orig_word

                            normalized_word, word_soundex = soundex(word)
                            word_distances = Counter()
                            for dict_word in dictionary_soundex[word_soundex]:
                                word_distances[dict_word] = levenshtein(normalized_word, dict_word)

                            if len(word_distances) > 0:
                                three_similar_words = word_distances.most_common()[:-4:-1]

                                # user interface and let user to choose the 
                                print("\'%s\' seems to be incorrect. Please choose from the following similar words that might be the right word:" % word)
                                choose_notice = ''
                                for key, (choice_word, distance) in enumerate(three_similar_words):
                                    choose_notice += "%d. %s\n" % (key+1, choice_word)
                                choose_notice += "4. keep this word\n"
                                choice_num = input(choose_notice)
                                # check whether the chice is correct
                                while choice_num not in ["1", "2", "3", "4"]:
                                    choice_num = input("Your choice is invalid. Please choose again.\n" + choose_notice)
                                
                                try:
                                    corrected_word = three_similar_words[int(choice_num)-1][0]
                                except:
                                    corrected_word = word
                            else:
                                print("\'%s\'seems to be incorrect. You have following choices:"% word)
                                choose_notice = "1. keep this word\n2. skip this word"
                                while choice_num not in ["1", "2"]:
                                    choice_num = input("Your choice is invalid. Please choose again.\n" + choose_notice)
                                if choice_num == 1:
                                    corrected_word = word
                                else:
                                    corrected_word = ''

                            if last_is_alpha:
                                corrected_word += orig_word[-1]
                            corrected_line.append(corrected_word)

                corrected_content.append(' '.join(corrected_line))

    # write into the *-corrected file
    fpath_name, ftext = os.path.splitext(check_filename)
    corrected_file = fpath_name + "-corrected" + ftext
    with open(corrected_file, "w") as f:
        f.write('\n'.join(corrected_content))
    print("======== Finish writing the corrected content into the file %s. ========" % corrected_file)



if __name__ == "__main__": 
    # The interactive spell checker 
    check_filename = str(input("Write the filename that you want to correct any spelling errors: ").strip())

    # check whether the file exist
    while os.path.isfile(check_filename) == False:
        check_filename = str(input("Please insert the right file name that is available to access: ").strip())

    spell_checker(check_filename)




