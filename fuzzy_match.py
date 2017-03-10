# Chen Wang 672409
# COMP90059 2017 Project 2
# 2017-03-10

import string
from edit_distance import levenshtein

punctuation_remover = str.maketrans('', '', string.punctuation)

class FuzzyMatcher:
    """FuzzyMatcher supports queries with multiple words,
    and allows either the query or the content to have slight spelling mistakes.
    """
    def __init__(self, target_file):
        self.target_file = target_file
        
    def match(self, query, threshold=20):
        """Find matches according to the query."""
        query_words = query.split()
        result = []
        with open(self.target_file, 'r') as target_content:
            for line in target_content:
                line = line.strip().lower().translate(punctuation_remover)
                content_words = line.split()
                if len(content_words) < len(query_words):
                    # The content is even shorter than the query.
                    continue
                tokens = []
                # Group every N content words, where N equals the number of query words.
                # e.g. query = "hello world", content = "this is a test",
                # the result of tokens is [[this, is], [is, a], [a, test]]
                i = 0
                while i + len(query_words) <= len(content_words):
                    tokens.append(content_words[i: i+len(query_words)])
                    i += 1
                # If one token matches, then this sentence is marked as matched.
                matched_flag = False
                for token in tokens:
                    if matched_flag:
                        continue
                    dissimilarity = []
                    for idx, query_word in enumerate(query_words):
                        if len(query_word) == 0 or len(token[idx]) == 0:
                            continue
                        distance = levenshtein(query_word, token[idx])
                        dissimilarity.append(distance * 100 / len(query_word))
                    if len(dissimilarity) == 0:
                        continue
                    overall_dissimilarity = float(sum(dissimilarity)) / len(dissimilarity)
                    if overall_dissimilarity < threshold:
                        result.append(line)
                        matched_flag = True
        return result

def main():
    matcher = FuzzyMatcher('./fuzzy_search_test.txt')
    print(matcher.match("housholds are renter"))

if __name__ == '__main__':
    main()
