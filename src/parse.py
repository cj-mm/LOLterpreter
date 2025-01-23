from tkinter import *

class Parser(object):

    def __init__(self, tokens, tk):
        self.console = tk.winfo_children()[23] # gui
        # the tokens will be the one from the lexer.py
        self.tokens = tokens
        self.i = 0  #for iterating later
        self.errFlag = 0


    #########################################################
    # OTHERS/ESSENTIALS

    def linebreak(self):
        if self.tokens[self.i][1] == "EOL":
            self.i += 1
            return True
        return False

    # statements/code block (recursive)
    def statement(self):
        if self.output() or self.input() or self.declaration() or self.assignment() or self.expr() or self.loops() or self.conditional() or self.typecast(): # check one of these if match
            if self.next():
                return True
        return False

    # next statement
    def next(self):
        if self.linebreak():
            if self.endprog() or self.statement() or self.tokens[self.i][1] == "OIC":
                return True
        return False


    def expr(self):
        if self.arithmetic() or self.comparison() or self.boolean() or self.concat() or self.typecast():
            return True
        return False

    
    def an_key(self):
        if self.tokens[self.i][1] == "AN":
            self.i += 1
            return True
        return False

    
    def literal(self):
        literal = ["YARN", "TROOF", "NUMBR", "NUMBAR"]
        if self.tokens[self.i][0] in literal or self.tokens[self.i][1] in literal:
            self.i += 1
            return True
        return False
    

    def identifier(self):
        if self.tokens[self.i][0] == "IDENTIFIER":
            self.i += 1
            return True
        return False
    #########################################################
    
    #########################################################
    # CONDITIONAL

    def conditional(self):
        if self.if_then() or self.switch_case():
            return True
        return False


    def if_then_codeblock(self):
        if self.output() or self.input() or self.declaration() or self.assignment() or self.expr() or self.loops() or self.conditional():
            if self.if_then_next():
                return True
        return False
    
    # for multiple statements inside the if-block
    def if_then_next(self):
        if self.linebreak():
            if self.tokens[self.i][1] == "NO WAI" or self.tokens[self.i][1] == "OIC" or self.if_then_codeblock():
                return True
        return False

    # for the line of code currently evaluated to be matched in this function, it should satisfy each if statements (Generally applicable to every function)
    def if_then(self):
        if self.tokens[self.i][1] == "O RLY?":
            self.i += 1
            if self.linebreak():
                if self.tokens[self.i][1] == "YA RLY":
                    self.i += 1
                    if self.if_then_next():
                        if self.tokens[self.i][1] == "NO WAI":
                            self.i += 1
                            if self.if_then_next():
                                if self.tokens[self.i][1] == "OIC":
                                    self.i += 1
                                    return True
                                else:
                                    return False
                            else:
                                self.i -= 3 # point back since it did not match
                        elif self.tokens[self.i][1] == "OIC":
                            self.i += 1
                            return True
                    else:
                        self.i -= 2 
                else:
                    self.i -= 1
            else:
                self.i -= 1
        return False


    def switch_case(self):
        if self.tokens[self.i][1] == "WTF?":
            self.i += 1
            if self.linebreak():
                if self.tokens[self.i][1] == "OMG":
                    self.i += 1
                    if self.literal():
                        if self.linebreak():
                            if self.switch_case_codeblock():
                                if self.tokens[self.i][1] == "OIC":
                                    self.i += 1
                                    return True
                                elif self.tokens[self.i][1] == "OMGWTF":
                                    self.i += 1
                                    if self.linebreak():
                                        if self.statement():
                                            if self.tokens[self.i][1] == "OIC":
                                                self.i += 1
                                                return True
                                        else:
                                            self.i -= 3
                                    else:
                                        self.i -= 3
                                else:
                                    self.i -= 2
                            else:
                                self.i -= 2
                        else:
                            self.i -= 2
                    else:
                        self.i -= 2
                else:
                    self.i -= 1
        return False


    def switch_case_codeblock(self):
        if self.tokens[self.i][1] == "GTFO" or self.output() or self.input() or self.declaration() or self.assignment() or self.expr() or self.loops() or self.conditional():
            if self.tokens[self.i][1] == "GTFO":
                self.i += 1
            if self.linebreak():
                if self.tokens[self.i][1] == "OIC" or self.tokens[self.i][1] == "OMGWTF" or self.switch_case_op() or self.switch_case_codeblock():
                    return True
        return False


    def switch_case_op(self):
        if self.tokens[self.i][1] == "OMG":
            self.i += 1
            if self.literal():
                if self.linebreak():
                    if self.switch_case_codeblock():
                        if self.tokens[self.i][1] == "OIC" or self.tokens[self.i][1] == "OMGWTF" or self.switch_case_op():                            
                            return True
        return False
    #########################################################

    #########################################################
    # LOOPS

    def loops(self):
        if self.tokens[self.i][1] == "IM IN YR":
            self.i += 1
            if self.identifier():
                if self.tokens[self.i][1] == "UPPIN" or self.tokens[self.i][1] == "NERFIN":
                    self.i += 1
                    if self.yr_key():
                        if self.identifier():
                            if self.tokens[self.i][1] == "TIL" or self.tokens[self.i][1] == "WILE":
                                self.i += 1
                                if self.expr():
                                    if self.loops_next():
                                        if self.tokens[self.i][1] == "IM OUTTA YR":
                                            self.i += 1
                                            if self.identifier():
                                                return True
                                            else:
                                                self.i -= 4
                                        else:
                                            self.i -= 3
                                    else:
                                        self.i -= 3
                                else:
                                    self.i -= 3
                            else:
                                self.i -= 2
                        else:
                            self.i -= 2
                    else:
                        self.i -= 2
                else:
                    self.i -= 1
            else:
                self.i -= 1
        return False


    def loops_codeblock(self):
        if self.output() or self.input() or self.declaration() or self.assignment() or self.expr() or self.loops() or self.conditional():
            if self.loops_next():
                return True
        return False
    

    def loops_next(self):
        if self.linebreak():
            if self.tokens[self.i][1] == "IM OUTTA YR" or self.loops_codeblock():
                return True
        return False


    def yr_key(self):
        if self.tokens[self.i][1] == "YR":
            self.i += 1
            return True
        return False      
    #########################################################
    
    #########################################################
    # ASSIGNMENT/DECLARATION/TYPECAST

    def assignment(self):
        if self.identifier():
            if self.tokens[self.i][1] == "R":
                self.i += 1
                if self.literal() or self.identifier() or self.expr():
                    return True
                else:
                    self.i -= 1
                    return False
            else:
                self.i -= 1
                return False
    
    # variable declaration and initialization
    def declaration(self):
        if self.tokens[self.i][0] == "VARIABLE_DEC":
            self.i += 1
            if self.identifier():
                if self.tokens[self.i][1] == "ITZ":
                    self.i += 1
                    if self.identifier() or self.literal() or self.expr():
                        return True
                    else:
                        return False
                elif self.tokens[self.i][1] == "EOL":
                    return True
                else:
                    return False
            else:
                return False
        return False

    def typecast(self):
        if self.tokens[self.i][1] == "MAEK":
            self.i += 1
            if self.identifier():
                if self.tokens[self.i][1] == "A":
                    self.i += 1
                    if self.literal():
                        return True
                elif self.literal():
                    return True
                else:
                    return False 
        elif self.identifier():
            if self.tokens[self.i][1] == "IS NOW A":
                self.i += 1
                if self.literal():
                    return True
            elif self.tokens[self.i][1] == "R MAEK":
                self.i += 1
                if self.identifier():
                    if self.literal():
                        return True
            else:
                return False 
        else:
            return False
    #########################################################

    #########################################################
    # INPUT/OUTPUT

    def input(self):
        if self.tokens[self.i][0] == "INPUT_KEY":
            self.i += 1
            if self.identifier():
                return True
            else:
                return False
        else:
            return False
    

    # print
    def output(self):
        if self.tokens[self.i][1] == "VISIBLE":
            self.i += 1
            if self.print_arg():
                return True
            else:
                return False
        else:
            return False

    # for arguments of VISIBLE 
    def print_arg(self):
        if self.linebreak():
            self.i -= 1
            return True
        
        if self.identifier() or self.literal() or self.expr():
            self.print_arg()
            return True
        return False
    #########################################################

    #########################################################
    # BOOLEAN

    def boolean(self):
        if self.tokens[self.i][0] == "BOOL_OP":
            if self.tokens[self.i][1] == "NOT":
                self.i += 1
                if self.comparison() or self.literal() or self.identifier() or self.relational_op():
                    return True
                else:
                    self.i -= 1
                    return False
            elif self.tokens[self.i][1] == "ALL OF" or self.tokens[self.i][1] == "ANY OF":
                self.i += 1
                if self.bool_operand() or self.all_any_arg():
                    if self.bool_arg():
                        return True
                    else:
                        self.i -= 1
                        return False
                else:
                    self.i -= 1
                    return False
            else:
                self.i += 1
                if self.bool_operand():
                    if self.an_key():
                        if self.bool_operand():
                            return True
                        else:
                            self.i -= 1
                    else:
                        self.i -= 1
                else:
                    self.i -= 1
        return False


    def bool_operand(self):
        if self.literal() or self.identifier() or self.comparison():
            return True
        return False

    
    def bool_arg(self):
        if self.an_key():
            if self.bool_operand() or self.all_any_arg():
                if self.bool_arg():
                    return True
        elif self.tokens[self.i][1] == "MKAY":
            self.i += 1
            return True
        return False

    
    def all_any_arg(self):
        if not (self.tokens[self.i][1] == "ALL OF" or self.tokens[self.i][1] == "ANY OF") and self.boolean():
            return True
        return False
    #########################################################
    
    #########################################################
    # CONCATENATION

    def concat(self):
        if self.tokens[self.i][1] == "SMOOSH":
            self.i += 1
            if self.identifier() or self.literal():
                if self.concat_arg():
                    return True
        return False
            
    def concat_arg(self):
        if self.an_key():
            if self.identifier or self.literal():
                self.i += 1
                if self.concat_arg():
                    return True
                elif self.tokens[self.i][1] == "EOL":
                    return True
        return False
    #########################################################
        
    #########################################################
    # COMPARISON

    def comparison(self):
        if self.tokens[self.i][0] == "COMPARISON_OP":
            self.i += 1
            if self.literal() or self.identifier():
                if self.an_key():
                    if self.literal() or self.identifier() or self.relational_op():
                        return True
                    else:
                        self.i -= 1
            else:
                self.i -= 1
        return False

    # for BIGGR OF and SMALLR OF arg in comparison
    def relational_op(self):
        if self.tokens[self.i][1] == "BIGGR OF" or self.tokens[self.i][1] == "SMALLR OF":
            self.i += 1
            if self.identifier() or self.math_literal() or self.arithmetic():
                if self.an_key():
                    if self.identifier() or self.math_literal() or self.arithmetic():
                        return True
                    else:
                        self.i -= 1
                else:
                    self.i -= 1
            else:
                self.i -= 1
        return False
    #########################################################

    #########################################################
    # ARITHMETIC 

    def arithmetic(self):
        if self.tokens[self.i][0] == "ARITHMETIC_OP":
            self.i += 1
            if self.identifier() or self.literal() or self.math_typecast() or self.arithmetic():
                if self.an_key():
                    if self.identifier() or self.literal() or self.math_typecast() or self.arithmetic():
                        return True
                    else:
                        self.i -= 1
            else:
                self.i -= 1
        return False 
    
    # typecasting for arithmetic operations (to NUMBR/NUMBAR)
    def math_typecast(self):
        if self.tokens[self.i][1] == "MAEK":
            self.i += 1
            if self.identifier():
                if self.tokens[self.i][1] == "A":
                    self.i += 1
                    if self.math_type():
                        return True
                elif self.math_type():
                    return True
                else:
                    return False 
        elif self.identifier():
            if self.tokens[self.i][1] == "IS NOW A":
                self.i += 1
                if self.math_type():
                    return True
            elif self.tokens[self.i][1] == "R MAEK":
                self.i += 1
                if self.identifier():
                    if self.math_type():
                        return True
            else:
                return False 
        else:
            return False
       

    def math_type(self):
        if self.tokens[self.i][1] == "NUMBR" or self.tokens[self.i][1] == "NUMBAR":
            self.i += 1
            return True
        return False             
            

    def math_literal(self):
        literal = ["NUMBR", "NUMBAR"]
        if self.tokens[self.i][0] in literal:
            self.i += 1
            return True
        return False
    #########################################################

    
    def checkErr(self):
        return self.errFlag

    # Start
    def program(self):
        if self.tokens[self.i][1] == "HAI":
            self.i += 1
            if len(self.tokens) > 2 and self.linebreak():
                if self.statement() or self.endprog():
                    print("Passed!")
                    self.errFlag = 1
                    return

        self.errFlag = 0
        # get the line that caused the error
        lineError = ""
        if self.tokens[self.i][1] == "EOL":
            self.i -= 1

        while self.tokens[self.i][1] != "EOL":
            self.i -= 1
        self.i += 1

        while self.tokens[self.i][1] != "EOL":
            lineError += " " + self.tokens[self.i][1]
            self.i += 1

        err = "Error at" + lineError
        self.console.delete("1.0", END)
        self.console.insert(END, err)
        self.console.config(state=DISABLED)


    def endprog(self):
        if self.tokens[self.i][1] == "KTHXBYE":
            self.i += 1
            if self.linebreak():
                if self.i == len(self.tokens):
                    return True
        return False
