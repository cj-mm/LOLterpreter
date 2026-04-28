import re
from errors import InterpreterError


class Interpreter(object):

    def __init__(
        self,
        tokens,
        on_error=None,
        on_input=None,
        on_output=None,
        on_symbol_update=None,
    ):
        """
        on_error         : callable(message) for runtime errors
        on_output        : callable(text) for VISIBLE output
        on_symbol_update : callable(symbol_table) when variables change
        """
        self.tokens = tokens
        self.i = (
            2  # for iterating later, will start with two, won't include HAI and EOL
        )
        self.symbol_table = []  # will store identifiers, their data type and value
        self.temp = []  # will store multiple values
        self.single = ""
        self.type = ""
        self.on_error = on_error or (lambda msg: print(msg))
        self.on_input = on_input or (lambda prompt: input(prompt))
        self.on_output = on_output or (lambda text: print(text, end=""))
        self.on_symbol_update = on_symbol_update or (lambda table: None)

    def get_table(self):
        return self.symbol_table

    ################################################################
    # INTERPRETER
    ################################################################

    def program(self):
        if (
            self.variables()
            or self.assignment()
            or self.output()
            or self.input()
            or self.operations()
            or self.if_then()
            or self.switch_case()
            or self.loops()
            or self.typecast()
        ):
            print(
                "\nSymbol Table:\n", self.symbol_table, "\n"
            )  # just to see the changes in the symbol table
            self.i += 1  # linebreak
            if self.program():
                return True
        elif len(self.tokens) - 2 == self.i:
            return True
        else:
            raise InterpreterError("Error at" + self.getError())

    # would update the value of the variable in the symbol table
    # if the variable is new, the just add
    def var_update(self, var, val, type):
        i = 0
        doesExist = False
        while i < len(self.symbol_table):
            if var == self.symbol_table[i][0]:
                self.symbol_table[i][1] = val
                self.symbol_table[i][2] = type
                doesExist = True
                break
            i += 1

        if not doesExist:
            self.symbol_table.append([var, val, type])

        # update the symbol table (GUI)
        self.on_symbol_update(self.symbol_table)

    # would return the value of the existing variable that will be used (from global var self.single)
    def get_val(self, var):
        i = 0
        while i < len(self.symbol_table):
            if var == self.symbol_table[i][0]:
                # if variable is declared but was not initialized
                if self.symbol_table[i][1] == "NO VALUE":
                    raise InterpreterError(
                        "Error (identifier has no value) at" + self.getError()
                    )

                else:
                    self.single = self.symbol_table[i][1]
                    self.type = self.symbol_table[i][2]
                    return True
            i += 1
        return False

    ####################
    # variable declaration and initialization
    ####################
    def variables(self):
        if self.tokens[self.i][1] == "I HAS A":
            self.i += 1
            if self.identifier():
                c = self.i - 1
                if self.tokens[self.i][1] == "ITZ":
                    self.i += 1
                    if self.identifier():
                        if self.get_val(self.tokens[self.i - 1][1]):
                            self.var_update(
                                self.tokens[self.i - 3][1], self.single, self.type
                            )
                            return True
                        else:
                            return False
                    elif self.literal():
                        self.var_update(
                            self.tokens[self.i - 3][1],
                            self.tokens[self.i - 1][1],
                            self.tokens[self.i - 1][0],
                        )
                        return True
                    elif self.operations():
                        self.var_update(self.tokens[c][1], self.single, self.type)
                        return True
                elif self.tokens[self.i][1] == "EOL":
                    self.var_update(self.tokens[self.i - 1][1], "NO VALUE", "NOOB")
                    return True
        else:
            return False

    ####################
    # assignment
    ####################
    def assignment(self):
        if self.identifier():
            c = self.i - 1
            if self.tokens[self.i][1] == "R":
                self.i += 1
                if self.identifier():
                    if self.get_val(self.tokens[self.i - 1][1]):
                        self.var_update(
                            self.tokens[self.i - 3][1], self.single, self.type
                        )
                        return True
                    else:
                        return False
                elif self.literal():
                    self.var_update(
                        self.tokens[self.i - 3][1],
                        self.tokens[self.i - 1][1],
                        self.tokens[self.i - 1][0],
                    )
                    return True
                elif self.operations():
                    self.var_update(self.tokens[c][1], self.single, self.type)
                    return True
            else:  # casting using R MAEK and IS NOW A
                if not self.get_val(self.tokens[c][1]):
                    return False
                if self.tokens[self.i][1] == "IS NOW A":
                    self.i += 1
                elif self.tokens[self.i][1] == "R MAEK":
                    self.i += 2  # for R MAEK and the identifier after
                temp = self.tokens[self.i][1]  # literal
                self.i += 1
                if temp == "YARN":
                    self.var_update(self.tokens[c][1], str(self.single), "YARN")
                elif temp == "NUMBR":
                    self.my_type(self.single)
                    if self.type == "NUMBR" or self.type == "NUMBAR":
                        self.single = float(self.single)
                        self.var_update(self.tokens[c][1], int(self.single), "NUMBR")
                    else:
                        raise InterpreterError(
                            "Error (identifier cannot be typecasted) at"
                            + self.getError()
                        )
                elif temp == "NUMBAR":
                    self.my_type(self.single)
                    if self.type == "NUMBR" or self.type == "NUMBAR":
                        self.var_update(self.tokens[c][1], float(self.single), "NUMBAR")
                    else:
                        raise InterpreterError(
                            "Error (identifier cannot be typecasted) at"
                            + self.getError()
                        )
                else:  # TROOF
                    self.my_type(self.single)
                    if self.type == "YARN":
                        if self.single == "WIN" or self.single == "FAIL":
                            self.var_update(
                                self.tokens[c][1], str(self.single), "TROOF"
                            )
                        else:
                            raise InterpreterError(
                                "Error (identifier cannot be typecasted) at"
                                + self.getError()
                            )
                    elif self.type == "TROOF":
                        self.var_update(self.tokens[c][1], self.single, "TROOF")
                    else:
                        raise InterpreterError(
                            "Error (identifier cannot be typecasted) at"
                            + self.getError()
                        )
                return True
        return False

    ####################
    # printing
    ####################
    def output(self):
        if self.tokens[self.i][1] == "VISIBLE":
            self.i += 1
            self.temp = []
            if self.print_arguments():
                self.var_update("IT", self.temp, "NO TYPE")

                # printing
                print(self.temp)

                for item in self.temp:
                    if (
                        isinstance(item, str)
                        and item[0] == '"'
                        and item[len(item) - 1] == '"'
                    ):
                        # remove double quotes
                        item = item[0:0:] + item[1::]
                        item = item[0 : len(item) - 1 :] + item[len(item) + 1 : :]
                    self.updateConsole(item)

                self.updateConsole("\n")

                if self.tokens[self.i + 1][1] == "GIMMEH":
                    self.i += 1
                    self.input()
                    return True

                return True
            return False
        return False

    # print arguments
    def print_arguments(self):  # since visible can have many arguments
        if self.literal():
            self.temp.append(self.tokens[self.i - 1][1])
            if self.print_arguments():
                return True
            elif self.tokens[self.i][1] == "EOL":
                return True
        elif self.identifier():
            if self.get_val(self.tokens[self.i - 1][1]):
                self.temp.append(self.single)
            else:
                return False
            if self.print_arguments():
                return True
            elif self.tokens[self.i][1] == "EOL":
                return True
        elif self.operations():
            self.temp.append(self.single)
            if self.print_arguments():
                return True
            elif self.tokens[self.i][1] == "EOL":
                return True
        return False

    ####################
    # input
    ####################
    def input(self):
        if self.tokens[self.i][1] == "GIMMEH":
            self.i += 1
            if self.identifier():
                temp = self.on_input("Input: ")
                self.my_type(temp)
                self.var_update(self.tokens[self.i - 1][1], temp, self.type)
                self.updateConsole(temp + "\n")
                return True
        return False

    ####################
    # typecast (MAEK)
    ####################
    def typecast(self):
        if self.tokens[self.i][1] == "MAEK":
            self.i += 1
            if self.identifier():
                if not self.get_val(self.tokens[self.i - 1][1]):
                    return False
                if self.tokens[self.i][1] == "A":
                    self.i += 1
                if self.typecast_ope():
                    return True
                else:
                    return False
        else:
            return False

    def typecast_ope(self):
        # by this part, self.single has the value of the identifier and self.type has the data type
        temp = self.tokens[self.i][1]  # literal
        self.i += 1
        if temp == "YARN":
            self.var_update("IT", str(self.single), "YARN")
        elif temp == "NUMBR":
            self.my_type(self.single)
            if self.type == "NUMBR" or self.type == "NUMBAR":
                self.single = float(self.single)
                self.var_update("IT", int(self.single), "NUMBR")
            else:
                raise InterpreterError(
                    "Error (identifier cannot be typecasted) at" + self.getError()
                )

        elif temp == "NUMBAR":
            self.my_type(self.single)
            if self.type == "NUMBR" or self.type == "NUMBAR":
                self.var_update("IT", float(self.single), "NUMBAR")
            else:
                raise InterpreterError(
                    "Error (identifier cannot be typecasted) at" + self.getError()
                )

        else:  # TROOF
            self.my_type(self.single)
            if self.type == "YARN":
                if self.single == "WIN" or self.single == "FAIL":
                    self.var_update("IT", str(self.single), "TROOF")
                else:
                    raise InterpreterError(
                        "Error (identifier cannot be typecasted) at" + self.getError()
                    )
            elif self.type == "TROOF":
                self.var_update("IT", self.single, "TROOF")
            else:
                raise InterpreterError(
                    "Error (identifier cannot be typecasted) at" + self.getError()
                )
        return True

    ####################
    # if-then statements
    ####################
    def if_then_codeblock(self):
        if (
            self.output()
            or self.input()
            or self.variables()
            or self.assignment()
            or self.operations()
        ):
            if self.if_then_next():
                return True
        return False

    def if_then_next(self):
        self.i += 1  # linebreak
        if (
            self.tokens[self.i][1] == "NO WAI"
            or self.tokens[self.i][1] == "OIC"
            or self.if_then_codeblock()
        ):
            return True
        return False

    def skip(self, temp):
        if temp == 0 and self.tokens[self.i][1] == "OIC":
            self.i += 1
        elif temp == 1 and self.tokens[self.i][1] == "NO WAI":
            self.i += 1
        else:
            self.i += 1
            self.skip(temp)

    def if_then(self):
        if self.tokens[self.i][1] == "O RLY?":
            self.i += 3  # O RLY? keyword, linebreak, YA RLY

            temp = 0  # 0 for if, then 1 for else
            # if IT is WIN or can be typecasted to WIN, executes YA RLY
            self.get_val("IT")  # get IT value
            # check if IT can be implicitly tpecasted
            if self.type == "YARN":
                if self.single == "":
                    temp = 1
            elif self.type == "NUMBR" or self.type == "NUMBAR":
                if int(self.single) == 0:
                    temp = 1
            else:
                if self.single == "FAIL":
                    temp = 1
            # by this time, temp has the value (0 or 1) to decide whether to execute YA RLY or NO WAI

            if temp == 0:  # if
                if self.if_then_next():
                    if self.tokens[self.i][1] == "NO WAI":
                        self.i += 1
                        self.skip(temp)
                        return True
            else:  # else
                self.skip(temp)
                self.if_then_next()
                if self.tokens[self.i][1] == "OIC":
                    self.i += 1
                    return True
        return False

    ####################
    # switch-case statements
    ####################
    def switch_case(self):
        if self.tokens[self.i][1] == "WTF?":
            self.get_val("IT")  # get IT value
            self.i += 3  # WTF? keyword, linebreak, and OMG keyword
            val = str(self.tokens[self.i][1])  # literal after OMG
            self.single = str(self.single)

            if self.single == val:
                self.i += 2  # literal and linebreak
                self.execute()
                return True
            else:
                self.skip_switch_case(0)
                if (
                    self.tokens[self.i - 2][1] == "OMGWTF"
                ):  # if no other OMG exists, then execute OMGWTF
                    self.execute()
                    return True
                self.switch_case_op()
                return True
        return False

    def execute(self):
        self.switch_case_codeblock()
        self.skip_switch_case(1)  # 1 will indicate to ignore other OMG

    def skip_switch_case(self, flag):
        if flag == 1 and self.tokens[self.i][1] == "OIC":
            self.i += 1
        elif flag == 0 and self.tokens[self.i][1] == "OMG":
            self.i += 1
        elif flag == 0 and self.tokens[self.i][1] == "OMGWTF":
            self.i += 2
        else:
            self.i += 1
            self.skip_switch_case(flag)

    def switch_case_codeblock(self):
        if (
            self.tokens[self.i][1] == "GTFO"
            or self.output()
            or self.input()
            or self.variables()
            or self.assignment()
            or self.operations()
        ):
            if self.tokens[self.i][1] == "GTFO":
                self.i += 1
                return True
            elif self.tokens[self.i][1] == "EOL":
                self.i += 1
                if (
                    self.tokens[self.i][1] == "OIC"
                    or self.tokens[self.i][1] == "OMGWTF"
                    or self.tokens[self.i][1] == "OMG"
                    or self.switch_case_codeblock()
                ):
                    return True
        return False

    def switch_case_op(self):
        val = self.tokens[self.i][1]  # literal after OMG
        self.i += 2  # literal and linebreak

        if self.single == val:
            self.execute()
        else:
            self.skip_switch_case(0)
            if self.tokens[self.i - 2][1] == "OMGWTF":
                self.execute()
                return True
            self.switch_case_op()
            return True

    ####################
    # loops
    ####################
    def loops(self):
        if self.tokens[self.i][1] == "IM IN YR":
            self.i += 2  # for IM IN YR and identifier
            willInc = 0  # UPPIN or NERFIN
            if self.tokens[self.i][1] == "UPPIN":
                willInc = 1  # if UPPIN then will increment
            self.i += 2  # for UPPIN/NERFIN and YR keyword
            variable = (
                ""  # will hold the indentifier name to be processed by UPPIN/NERFIN
            )
            iteration = 0  # will hold the value of the identifier
            if self.identifier():
                variable = self.tokens[self.i - 1][1]
                if self.get_val(
                    self.tokens[self.i - 1][1]
                ):  # cast identifier value to numerical value
                    if self.type == "TROOF":
                        if self.single == "WIN":
                            self.single = 1
                        else:
                            self.single = 0
                        self.type = "NUMBR"
                    elif (
                        self.type == "YARN"
                    ):  # check first if the YARN can be casted to either NUMBAR or NUMBR
                        self.my_type(self.single)
                        if self.type == "NUMBR":
                            self.single = int(self.single)
                        else:
                            raise InterpreterError(
                                "Error (data type) at" + self.getError()
                            )  # if YARN can't be casted into NUMBAR or NUMBR
                    elif self.type == "NUMBR":
                        self.single = int(self.single)
                    else:
                        raise InterpreterError("Error (data type) at" + self.getError())

                else:
                    return False
            iteration = self.single
            self.var_update(variable, iteration, "NUMBR")
            condition = 0  # TIL or WILE
            if self.tokens[self.i][1] == "WILE":
                condition = 1  # if the loop will repeat if expression is WIN
            self.i += 1

            c = self.i  # for the loop to go back to the condition expression
            self.comparison()  # after this self.single is either WIN or FAIL
            if condition == 0:
                while self.single == "FAIL":
                    self.loops_next()
                    if willInc == 1:
                        self.var_update(variable, iteration + 1, "NUMBR")
                        iteration += 1
                    else:
                        self.var_update(variable, iteration - 1, "NUMBR")
                        iteration -= 1
                    self.i = c
                    self.comparison()
            else:
                while self.single == "WIN":
                    self.loops_next()
                    if willInc == 1:
                        self.var_update(variable, iteration + 1, "NUMBR")
                        iteration += 1
                    else:
                        self.var_update(variable, iteration - 1, "NUMBR")
                        iteration -= 1
                    self.i = c
                    self.comparison()

            self.exit_loop()
            return True
        return False

    # if the loop stops then find IM OUTTA YR to update self.i
    def exit_loop(self):
        if self.tokens[self.i][1] == "IM OUTTA YR":
            self.i += 2  # IM OUTTA YR and identifier
        else:
            self.i += 1
            self.exit_loop()

    def loops_codeblock(self):
        if (
            self.output()
            or self.input()
            or self.variables()
            or self.assignment()
            or self.operations()
        ):
            if self.loops_next():
                return True
        return False

    def loops_next(self):
        self.i += 1  # linebreak
        if self.tokens[self.i][1] == "IM OUTTA YR" or self.loops_codeblock():
            return True
        return False

    ################################################################
    # OPERATIONS
    ################################################################

    def operations(self):
        if self.arithmetic() or self.bool() or self.comparison() or self.concat():
            return True
        return False

    ####################
    # arithmetic operations
    ####################
    def arithmetic(self):
        if self.tokens[self.i][0] == "ARITHMETIC_OP":
            ope = self.tokens[self.i][1]
            self.i += 1
            num1 = 0
            num2 = 0
            if self.arith_implicit():
                num1 = self.single
                self.i += 1  # for the AN keyword
            else:
                return False

            if self.arith_implicit():
                num2 = self.single
                self.solve(num1, num2, ope)
                return True
            else:
                return False
        return False

    # implicit typecasting
    def arith_implicit(self):
        if self.identifier():
            if self.get_val(self.tokens[self.i - 1][1]):
                if self.type == "TROOF":
                    if self.single == "WIN":
                        self.single = 1
                    else:
                        self.single = 0
                    self.type = "NUMBR"
                    return True
                elif (
                    self.type == "YARN"
                ):  # check first if the YARN can be casted to either NUMBAR or NUMBR
                    self.my_type(self.single)
                    if self.type == "NUMBR":
                        self.single = int(self.single)
                    elif self.type == "NUMBAR":
                        self.single = float(self.single)
                    else:
                        return False
                elif self.type == "NUMBR":
                    self.single = int(self.single)
                    return True
                elif self.type == "NUMBAR":
                    self.single = float(self.single)
                    return True
                else:
                    raise InterpreterError("Error (data type) at" + self.getError())

        elif self.math_literal():
            self.type = self.tokens[self.i - 1][0]
            self.single = self.tokens[self.i - 1][1]
            if self.type == "NUMBR":
                self.single = int(self.single)
            else:
                self.single = float(self.single)
            return True
        elif self.arithmetic() or self.arith_explicit():
            return True
        else:
            return False

    # explicit typecasting
    def arith_explicit(self):
        if self.tokens[self.i][1] == "MAEK":
            self.i += 1
            if self.identifier():
                if not self.get_val(self.tokens[self.i - 1][1]):
                    return False
                if self.tokens[self.i][1] == "A":
                    self.i += 1
            # by this part, self.single has the value of the identifier and self.type has the data type
            temp = self.tokens[self.i][1]  # literal
            self.i += 1
            self.my_type(self.single)
            if temp == "NUMBR":
                if self.type == "NUMBR" or self.type == "NUMBAR":
                    self.single = float(self.single)
                    self.single = int(self.single)
                    return True
                else:
                    raise InterpreterError(
                        "Error (identifier cannot be typecasted) at" + self.getError()
                    )
            elif temp == "NUMBAR":
                if self.type == "NUMBR" or self.type == "NUMBAR":
                    self.single = float(self.single)
                    return True
                else:
                    raise InterpreterError(
                        "Error (identifier cannot be typecasted) at" + self.getError()
                    )
            else:
                return False
        else:
            return False

    # solving
    def solve(self, num1, num2, ope):
        if ope == "SUM OF":
            self.single = num1 + num2
        elif ope == "DIFF OF":
            self.single = num1 - num2
        elif ope == "PRODUKT OF":
            self.single = num1 * num2
        elif ope == "QUOSHUNT OF":
            self.single = num1 / num2
        elif ope == "MOD OF":
            self.single = num1 % num2
        elif ope == "BIGGR OF":
            self.single = max(num1, num2)
        elif ope == "SMALLR OF":
            self.single = min(num1, num2)
        self.my_type(str(self.single))

    # literals for arithmetic operations
    def math_literal(self):
        literal = ["NUMBR", "NUMBAR"]
        if self.tokens[self.i][0] in literal:
            self.i += 1
            return True
        else:
            return False

    ####################
    # boolean operations
    ####################
    def boolean(self):
        if self.tokens[self.i][0] == "BOOL_OP":
            if self.bool():
                return True
            else:
                return False
        return False

    # boolean operations aside from all-of and any-of
    def bool(self):
        args = ["BOTH OF", "EITHER OF", "WON OF"]
        ope = self.tokens[self.i][1]
        var1 = ""
        var2 = ""
        if self.tokens[self.i][1] in args:
            self.i += 1
            if self.bool_check():
                var1 = self.single
                self.i += 1
            else:
                return False
            if self.bool_check():
                var2 = self.single
                self.bool_solve(var1, var2, ope)
                self.var_update("IT", self.single, "TROOF")  # save result to IT
                return True
            else:
                return False
        elif self.tokens[self.i][1] == "NOT":
            self.i += 1
            if self.bool_check():
                var1 = self.single
                self.bool_solve(var1, var2, ope)
                self.var_update("IT", self.single, "TROOF")  # save result to IT
                return True
            else:
                return False
        elif self.tokens[self.i][1] == "ALL OF" or self.tokens[self.i][1] == "ANY OF":
            self.i += 1
            if self.bool_check() or self.all_any_arg():
                var1 = self.single
                self.bool_arg(ope, var1)
                self.var_update(
                    "IT", self.single, "TROOF"
                )  # fixed type from "YARN" to "TROOF"
            return True
        else:
            return False

    # ALL OF and ANY OF operands
    def bool_arg(self, ope, var1):
        if self.tokens[self.i][1] == "AN":
            self.i += 1
            var2 = ""
            if ope == "ALL OF":
                if self.bool_check() or self.all_any_arg():
                    var2 = self.single
                    var1 = var1 and var2
                    self.bool_arg(ope, var1)
            elif ope == "ANY OF":
                if self.bool_check() or self.all_any_arg():
                    var2 = self.single
                    var1 = var1 or var2
                    self.bool_arg(ope, var1)
        elif self.tokens[self.i][1] == "MKAY":
            self.i += 1
            self.single = var1

    def all_any_arg(self):
        if (
            not (
                self.tokens[self.i][1] == "ALL OF" or self.tokens[self.i][1] == "ANY OF"
            )
            and self.bool()
        ):
            return True
        return False

    # if operands are not TROOFS, will implicitly typecast
    # for NUMBR and NUMBAR: numerical zero will be FAIL
    # for YARN: "" will be FAIL
    # AFTER
    def bool_check(self):
        if self.identifier():
            if self.get_val(self.tokens[self.i - 1][1]):
                if self.type == "TROOF":
                    return True
                elif self.type == "NUMBR" or self.type == "NUMBAR":
                    if int(self.single) == 0:
                        self.single = "FAIL"
                    else:
                        self.single = "WIN"
                    return True
                elif self.type == "YARN":
                    if self.single == "":
                        self.single = "FAIL"
                    else:
                        self.single = "WIN"
                    return True
            else:
                return False
        elif self.tokens[self.i][0] == "TROOF":
            self.single = self.tokens[self.i][1]
            self.i += 1  # move forward after reading
            return True
        elif self.tokens[self.i][0] == "NUMBR" or self.tokens[self.i][0] == "NUMBAR":
            if int(self.tokens[self.i][1]) == 0:
                self.single = "FAIL"
            else:
                self.single = "WIN"
            self.i += 1  # move forward after reading
            return True
        elif self.tokens[self.i][0] == "YARN":
            if self.tokens[self.i][1] == "":
                self.single = "FAIL"
            else:
                self.single = "WIN"
            self.i += 1  # move forward after reading
            return True
        elif self.comparison():
            return True

    def bool_solve(self, var1, var2, ope):
        if var1 == "WIN":
            var1 = True
        else:
            var1 = False
        if var2 == "WIN":
            var2 = True
        elif var2 == "FAIL":
            var2 = False

        if ope == "BOTH OF":
            self.single = var1 and var2
        elif ope == "EITHER OF":
            self.single = var1 or var2
        elif ope == "WON OF":
            self.single = (var1 and not var2) or (not var1 and not var2)
        elif ope == "NOT":
            self.single = not var1

        if self.single:
            self.single = "WIN"
        else:
            self.single = "FAIL"
        self.my_type(self.single)

    ####################
    # comparison operations
    ####################
    def comparison(self):
        if self.tokens[self.i][0] == "COMPARISON_OP":
            ope = self.tokens[self.i][1]
            var1 = ""
            var2 = ""
            self.i += 1
            if self.identifier():
                if not self.get_val(self.tokens[self.i - 1][1]):
                    return False
            elif self.literal():
                self.single = self.tokens[self.i - 1][1]
                self.type = self.tokens[self.i - 1][0]
            else:
                self.relational_op()

            var1 = str(self.single)

            self.i += 1
            if self.identifier():
                if not self.get_val(self.tokens[self.i - 1][1]):
                    return False
            elif self.literal():
                self.single = self.tokens[self.i - 1][1]
                self.type = self.tokens[self.i - 1][0]
            else:
                self.relational_op()
            var2 = str(self.single)

            if ope == "BOTH SAEM":
                if var1 == var2:
                    self.single = "WIN"
                else:
                    self.single = "FAIL"
            else:
                if var1 != var2:
                    self.single = "WIN"
                else:
                    self.single = "FAIL"

            # FIXED — comparison results are always TROOF, regardless of operand types
            self.var_update("IT", self.single, "TROOF")
            return True
        return False

    # for BIGGR OF and SMALLR OF arg in comparison
    def relational_op(self):
        if (
            self.tokens[self.i][1] == "BIGGR OF"
            or self.tokens[self.i][1] == "SMALLR OF"
        ):
            ope = self.tokens[self.i][1]
            self.i += 1
            num1 = 0
            num2 = 0
            if self.relational_operands():
                num1 = self.single
                self.i += 1  # for the AN keyword
            else:
                return False

            if self.relational_operands():
                num2 = self.single
                self.solve(num1, num2, ope)
                return True
            else:
                return False
        return False

    def relational_operands(self):
        if self.identifier():
            if self.get_val(self.tokens[self.i - 1][1]):
                if self.type == "NUMBR":
                    self.single = int(self.single)
                    return True
                elif self.type == "NUMBAR":
                    self.single = float(self.single)
                    return True
                else:
                    raise InterpreterError("Error (data type) at" + self.getError())
        elif self.math_literal():
            self.type = self.tokens[self.i - 1][0]
            self.single = self.tokens[self.i - 1][1]
            if self.type == "NUMBR":
                self.single = int(self.single)
            else:
                self.single = float(self.single)
            return True
        elif self.arithmetic():
            return True

    ####################
    # concatenation
    ####################
    def concat(self):
        if self.tokens[self.i][1] == "SMOOSH":
            self.i += 1
            if self.identifier():
                if not self.get_val(self.tokens[self.i - 1][1]):
                    return False
            elif self.literal():
                self.single = self.tokens[self.i - 1][1]

            self.concat_arg(self.single)
            self.var_update("IT", self.single, "YARN")
            return True
        return False

    def concat_arg(self, temp):
        self.i += 1  # for AN keyword
        if self.identifier():
            if self.get_val(self.tokens[self.i - 1][1]):
                temp = temp + str(self.single)
            else:
                return False
        elif self.literal():
            self.single = self.tokens[self.i - 1][1]
            temp = temp + str(self.single)

        if self.tokens[self.i][1] == "EOL":
            self.single = temp
            return True
        elif self.concat_arg(temp):
            return True
        return False

    ################################################################
    # OTHERS
    ################################################################
    def my_type(self, token):
        token = str(token)
        if re.match("^-?\d+$", token):  # for numbr
            self.type = "NUMBR"
        elif re.match("^-?\d*\.\d+$", token):  # for numbar
            self.type = "NUMBAR"
        elif token == "FAIL" or token == "WIN":
            self.type = "TROOF"
        else:
            self.type = "YARN"

    # literals
    def literal(self):
        literal = ["YARN", "TROOF", "NUMBR", "NUMBAR"]
        if self.tokens[self.i][0] in literal:
            self.i += 1
            return True
        else:
            return False

    # identifiers
    def identifier(self):
        if self.tokens[self.i][0] == "IDENTIFIER":
            self.i += 1
            return True
        else:
            return False

    def updateConsole(self, output):
        self.on_output(output)

    # get the line that caused the error
    def getError(self):
        lineError = ""
        if self.tokens[self.i][1] == "EOL":
            self.i -= 1

        while self.tokens[self.i][1] != "EOL":
            self.i -= 1
        self.i += 1

        while self.tokens[self.i][1] != "EOL":
            lineError += " " + self.tokens[self.i][1]
            self.i += 1

        err = lineError + "\n"
        return err
