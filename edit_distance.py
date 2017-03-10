# Chen Wang 672409
# COMP90059 2017 Project 2
# 2017-02-26

import numpy as np

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
    