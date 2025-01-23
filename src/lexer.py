import re
from tkinter import *

class Lexer(object):
    Keywords1 = ['HAI', 'KTHXBYE', 'BTW', 'OBTW', 'TLDR', 'ITZ', 'NOT', 'DIFFRINT', 'SMOOSH', 'MAEK', 'VISIBLE', 'GIMMEH',
            'MEBBE', 'OIC', 'WTF?', 'A', 'OMG', 'OMGWTF', 'UPPIN', 'NERFIN', 'YR', 'TIL', 'WILE', 'R', 'AN', 'NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'GTFO']

    Keywords2 = [ 'I HAS A', 'BOTH SAEM', 'SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF', 'BIGGR OF', 
            'ANY OF', 'ALL OF', 'SMALLR OF', 'BOTH OF', 'EITHER OF', 'WON OF',   
            'IS NOW A', 'O RLY?', 'YA RLY', 'NO WAI', 'IM IN YR',  'IM OUTTA YR', 'R MAEK', 'HOW DUZ I', 'IF YOU SAY SO']
            
    def __init__(self, program, tk):
        self.program = program
        self.console = tk.winfo_children()[23] # gui
        self.check = 1   # flag if the program passed the lexical analysis, initialize to true
    
    def check(self):
        return self.check
        
    # removes empty strings
    def remove_empty(self, prog):
        tokens = []
        for line in prog:
            if(line.strip() != ''):
                tokens.append(line.strip())
        return tokens
    

    # remove all comments (+ find all yarns)
    def remove_comments(self, program, yarn_temp):
        temp = "\n " + program # add new line and space to consider the occurence of a comment in the first line

        # convert the source code from str to list using separators for btw and obtw comments, and new line
        # this is to fix strings in comments and BTW/OBTW in strings/identifiers
        prog_arr = re.split('(\n\s*OBTW(.|\n)*?TLDR\s*?\n|\sBTW.*\n|\n)', temp) 
        prog_arr = list(filter(None, prog_arr)) # remove None elements

        for i in range(len(prog_arr)):
            if bool(re.search('\sBTW', prog_arr[i])) or bool(re.search('\n\s*OBTW', prog_arr[i])): # check if it is not a comment
                prog_arr[i] = ""

        lines = []
        for item in prog_arr:
            temp = re.split('(".*?")', item)
            line = ""
            for i in range(len(temp)):
                if len(temp[i]) > 0 and temp[i][0] == '"' and temp[i][-1] == '"': # yarn
                    yarn_temp.append(temp[i])
                    line += ' "this_is_yarn" '
                else:
                    line += temp[i].strip()
            lines.append(line)
        
        # remove the "" caused by strip()
        lines = self.remove_empty(lines)
        return lines
    

    # classify keywords
    def classify_keywords(self, word):
        if word == 'HAI' or word == 'KTHXBYE': return "CODE_DELIMITER"
        # literal type
        elif word == 'NUMBR' or word == 'NUMBAR' or word == 'YARN' or word == 'TROOF': return "TYPE"
        # variable declaration
        elif word == 'I HAS A': return "VARIABLE_DEC"
        # variable assignment
        elif word == 'ITZ' or word == 'R': return "VARIABLE_ASSIGN"
        # arithmetic operations
        elif word == 'SUM OF' or word == 'DIFF OF' or word == 'PRODUKT OF' or word == 'QUOSHUNT OF' or  word == 'MOD OF' or word == 'BIGGR OF' or word == 'SMALLR OF': return "ARITHMETIC_OP"
        # boolean operations
        elif word == 'BOTH OF' or word == 'EITHER OF' or word == 'WON OF' or word == 'NOT' or word == 'ALL OF' or word == 'ANY OF': return "BOOL_OP"
        # comparison operations
        elif word == 'BOTH SAEM' or word == 'DIFFRINT': return "COMPARISON_OP"
        # typecasting
        elif word == 'MAEK' or word == 'IS NOW A' or word == 'R MAEK': return "TYPECAST"
        # printing
        elif word == 'VISIBLE': return "OUTPUT_KEY"
        elif word == 'GIMMEH': return "INPUT_KEY"
        # conditional statements
        elif word == 'O RLY?': return "IF_THEN_DELIMITER"
        elif word == 'YA RLY' or word == 'NO WAI': return "IF_ELSE"
        elif word == 'WTF?': return "SWITCH_DELIMITER"
        elif word == 'OMG' or word == 'OMGWTF': return "SWITCH_CASE"
        elif word == 'OIC': return "COND_END"
        # loops
        elif word == 'IM IN YR' or word == 'IM OUTTA YR': return "LOOP"
        # function
        elif word == 'HOW DUZ I' or word == 'IF YOU SAY SO': return "FUNCTION"
        else: return 'KEYWORD'
    
    
    def tokenize(self):
        program = self.program
        yarn_temp = []
        program = self.remove_comments(program, yarn_temp) 

        # keywords
        keywords1_temp = []
        keywords2_temp = []

        #will hold all tokens
        tokens = []

        #for accessing
        yarn_num = 0
        keyword1_num = 0
        keyword2_num = 0
        for line in program:
            # separate keywords with space/s and one 'word' keywords to consider identifiers with keywords in it. e.g. thiNERFINngs
            # find all keywords with space/s first
            line_arr = line.split()
            for i in range(3,0,-1):
                for j in range(len(line_arr)-i):
                    if i == 3:
                        kw = line_arr[j]+" "+line_arr[j+1]+" "+line_arr[j+2]+" "+line_arr[j+3]
                        if kw in self.Keywords2:
                            keywords2_temp.append(kw)
                            line = line.replace(kw, '"this_is_keyword2"') # placeholder
                    if i == 2:
                        kw = line_arr[j]+" "+line_arr[j+1]+" "+line_arr[j+2]
                        if kw in self.Keywords2:
                            keywords2_temp.append(kw)
                            line = line.replace(kw, '"this_is_keyword2"') # placeholder
                    if i == 1:
                        kw = line_arr[j]+" "+line_arr[j+1]
                        if kw in self.Keywords2:
                            keywords2_temp.append(kw)
                            line = line.replace(kw, '"this_is_keyword2"') # placeholder

            line = line.split() # we can now split using space since keywords with spaces are already evaluated
            # find all one 'word' keywords
            for i in range(len(line)):
                if line[i] in self.Keywords1:
                    keywords1_temp.append(line[i])
                    line[i] = '"this_is_keyword1"'

            # tokens
            for word in line:
                if word == '"this_is_keyword2"':
                    temp = self.classify_keywords(keywords2_temp[keyword2_num]) # look for the classification
                    tokens.append([temp, keywords2_temp[keyword2_num]]) # update the token
                    keyword2_num += 1
                elif word == '"this_is_keyword1"':
                    temp = self.classify_keywords(keywords1_temp[keyword1_num])
                    tokens.append([temp, keywords1_temp[keyword1_num]])
                    keyword1_num += 1
                elif word == '"this_is_yarn"':
                    tokens.append(["YARN", yarn_temp[yarn_num]])
                    yarn_num += 1
                elif re.match('WIN', word) or re.match('FAIL', word):   #for troof
                    tokens.append(["TROOF", word])
                elif re.match('^[a-zA-Z][a-zA-Z\d_]*$', word):  #for identifier
                    tokens.append(["IDENTIFIER", word])
                elif re.match('^-?\d+$', word):  #for numbr
                    tokens.append(["NUMBR", word])
                elif re.match('^-?\d*\.\d+$', word):  #for numbar
                    tokens.append(["NUMBAR", word])
                else:
                    err = "Error at "+ word + "\nSyntax error: invalid syntax!\n"
                    self.console.delete("1.0", END)
                    self.console.insert(END, err)
                    self.console.config(state=DISABLED)
                    self.check = 0
                    break
            # linebreak, since program was broke into lines by spliting every newline
            tokens.append(["LINEBREAK", "EOL"])
        
        # the tokens that will be returned will be the tokenized program that is categorized with newline as EOL
        return tokens
        
        
    