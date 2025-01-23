from tkinter import *
from tkinter import filedialog
import os
import lexer
import parse
import interpreter
from tkinter import ttk

class GUI(object):
    root = Tk()
    root.title("LOLTERPRETER")
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Horizontal.TScrollbar", gripcount=0, background="white", troughcolor="gray12", bordercolor="black", arrowcolor="gray25")
    style.configure("Vertical.TScrollbar", gripcount=0, background="white", troughcolor="gray12", bordercolor="black", arrowcolor="gray25")

    def __init__(self):
        self.file = ""


    def setup(self):
        root = self.root
        root.configure(bg='black')

        self.textEditor()
        self.lexemes()
        self.symbolTable()
        self.console()

        root.mainloop()


    # will be called every time execute button is pressed
    def execute(self, program):
        widgets = self.root.winfo_children()
        console = widgets[23]
        console.config(state=NORMAL)
        console.delete("1.0", END) # deletes the content of the console

        # #######################################
        # LEXICAL ANALYZER PART
        # #######################################
        lex = lexer.Lexer(program, self.root)
        # then call tokenize that will return the tokens from the program
        tokens = lex.tokenize()
        self.populateLexemes(tokens, lex.check)
    

        parser = parse.Parser(tokens, self.root)
        if lex.check != 0 and not program.isspace():
            ########################################
            # SYNTAX ANALYZER PART
            ########################################
            # calling the parser class from import parser.py, create an instance and pass the tokens from the lexer
            parser.program()
        

        if parser.checkErr() != 0:
            # ########################################
            # # INTERPRETER
            # ########################################

            identifier = widgets[16]
            value = widgets[18]
            identifier.delete(0, END)
            value.delete(0, END)

            print("\n\nInterpreter Part: ")
            interpret = interpreter.Interpreter(tokens, self.root)
            interpret.program()
            #interpret.symbol_table will be the list of identifiers and their values
            symbol_table = interpret.symbol_table
            for i in range(0, identifier.index("end")):
                identifier.itemconfig(i, {'fg': 'white'})
                value.itemconfig(i, {'fg': 'white'})



    # populates lexeme table
    def populateLexemes(self, tokens, err):
        widgets = self.root.winfo_children() # will return all the widgets in the GUI
        lexeme_col = widgets[8]
        class_col = widgets[10]
        lexeme_col.delete(0, END)
        class_col.delete(0, END)

        if err != 0:
            fg_idx = 0
            for i in range(len(tokens)-1):
                if tokens[i][1] != "EOL":
                    lexeme_col.insert(END, tokens[i][1])
                    lexeme_col.itemconfig(fg_idx, {'fg': 'white'})
                    class_col.insert(END, tokens[i][0])
                    class_col.itemconfig(fg_idx, {'fg': 'white'})
                    fg_idx += 1


    def fileExplorer(self, text_editor):
        root = self.root
        file_label = Label(root, text="No file selected...")
        file_label.grid(row=0, column=0, padx=20, pady=3, sticky=W)
        file_label.configure(background="black", foreground="magenta2")

        fileExplorer_btn = Button(root, text="SELECT FILE", command=lambda: self.selectFile(text_editor, file_label))
        fileExplorer_btn.grid(row=0, column=1, padx=20, pady=3, sticky=E)
        fileExplorer_btn.configure(background="black", foreground="magenta2")

    def textEditor(self):
        root = self.root
        text_editor = Text(root, width=50, height=15, wrap=NONE)
        text_editor.grid(row=1, column=0, rowspan=2, columnspan=2)
        text_editor.configure(background="gray12", foreground="plum1", insertbackground="white")

        scrollbarY = ttk.Scrollbar(root, orient="vertical")
        scrollbarY.grid(row=1, column=2, rowspan=2, sticky="NS, W")

        scrollbarX = ttk.Scrollbar(root, orient="horizontal")
        scrollbarX.grid(row=3, column=0, columnspan=2, sticky="EW, S")

        text_editor.config(yscrollcommand = scrollbarY.set, xscrollcommand=scrollbarX.set, height=23, width=50)
        scrollbarY.config(command = text_editor.yview)
        scrollbarX.config(command = text_editor.xview)

        self.fileExplorer(text_editor)

        execute_btn = Button(root, text="EXECUTE", command=lambda: self.execute(text_editor.get(1.0, END))) # pass the current contents of the text editor to execute function
        execute_btn.grid(row=4, column=0, columnspan=10, padx=20, pady=3, sticky="E, W")
        execute_btn.configure(background="orchid1", foreground="black", font="Helvetica 12 bold")


        
    def lexemes(self):
        root = self.root
        title = Label(root, text="LEXEMES")
        title.grid(row=0, column=3, columnspan=3, sticky="E, W")
        title.configure(background="black", foreground="white", font="bold")

        lex_label = Label(root, text="Lexeme")
        lex_label.grid(row=1, column=3)
        lex_label.configure(background="black", foreground="white")

        lexeme = Listbox(root)
        lexeme.grid(row=2, column=3)

        class_label = Label(root, text="Classification")
        class_label.grid(row=1, column=4)
        class_label.configure(background="black", foreground="white")

        classification = Listbox(root)
        classification.grid(row=2, column=4)

        lexeme.configure(background="gray12")
        classification.configure(background="gray12")

        self.tableScrollBar(lexeme, classification, 2, 3)


    def symbolTable(self):
        root = self.root
        title = Label(root, text="SYMBOL TABLE")
        title.grid(row=0, column=7, columnspan=3, padx=20, pady=3)
        title.configure(background="black", foreground="white", font="bold")

        ident_label = Label(root, text="Identifier")
        ident_label.grid(row=1, column=7, padx=20, pady=3)
        ident_label.configure(background="black", foreground="white")

        identifier = Listbox(root)
        identifier.grid(row=2, column=7)

        value_label = Label(root, text="Value")
        value_label.grid(row=1, column=8, padx=20, pady=3)
        value_label.configure(background="black", foreground="white")
        
        value = Listbox(root)
        value.grid(row=2, column=8)

        identifier.configure(background="gray12")
        value.configure(background="gray12")

        self.tableScrollBar(identifier, value, 2, 7)

    # adds scrollbar to lexemes table and symbol table
    # lengthy because the columns of the tables are independent from each other. Thus, binding/synchronizing them is necessary
    def tableScrollBar(self, col1, col2, rowNum, colNum):
        root = self.root

        scrollbarY = ttk.Scrollbar(root, orient="vertical")
        scrollbarY.grid(row=rowNum, column=colNum+3, sticky="NS, W")

        scrollbarX1 = ttk.Scrollbar(root, orient="horizontal")
        scrollbarX1.grid(row=rowNum+1, column=colNum, columnspan=1, sticky="EW, S")

        scrollbarX2 = ttk.Scrollbar(root, orient="horizontal")
        scrollbarX2.grid(row=rowNum+1, column=colNum+1, columnspan=2, sticky="EW, S")

        col1.config(yscrollcommand = scrollbarY.set, xscrollcommand=scrollbarX1.set, height=21, width=30)
        col2.config(yscrollcommand = scrollbarY.set, xscrollcommand=scrollbarX2.set, height=21, width=30)
        
        if colNum == 3:
            scrollbarY.config(command = self.scrollLexemes)
        else:
            scrollbarY.config(command = self.scrollSymbolTable)

        # enable proper scrolling through mouse wheel
        col1.bind("<MouseWheel>", lambda e: self.mousewheel(e, col2))
        col2.bind("<MouseWheel>", lambda e: self.mousewheel(e, col1)) 

        # enable proper scrolling through arrows
        col1.bind("<Up>", lambda e: self.arrowscroll(e, -1, col1, col2))
        col2.bind("<Up>", lambda e: self.arrowscroll(e, -1, col1, col2))
        col1.bind("<Down>", lambda e: self.arrowscroll(e, 1, col1, col2))
        col2.bind("<Down>", lambda e: self.arrowscroll(e, 1, col1, col2)) 

        scrollbarX1.config(command = col1.xview)
        scrollbarX2.config(command = col2.xview)

    # binds the y scrollbar to the lexeme table
    def scrollLexemes(self, *args):
        widgets = self.root.winfo_children()
        widgets[8].yview(*args)
        widgets[10].yview(*args)

    # binds the y scrollbar to the symbol table
    def scrollSymbolTable(self, *args):
        widgets = self.root.winfo_children()
        widgets[16].yview(*args)
        widgets[18].yview(*args)


    def mousewheel(self,event, lb):
        lb.yview_scroll(int(-4*(event.delta/120)), "units")


    def arrowscroll(self, event, num, lb1, lb2):
        lb1.yview("scroll", int(num), "units")
        lb2.yview("scroll", int(num), "units")


    def console(self):
        root = self.root

        title = Label(root, text="CONSOLE")
        title.grid(row=6, column=0, columnspan=10, padx=20, pady=3, sticky="E, W")
        title.configure(background="black", foreground="white", font="Helvetica 10 bold")

        console = Text(root, width=20, height=10)
        console.grid(row=7, column=0, columnspan=10, sticky="E, W")

        console.configure(background="gray12", foreground="white")

        
        scrollbarY = ttk.Scrollbar(root, orient="vertical")
        scrollbarY.grid(row=7, column=10, sticky="NS, W")

        console.config(yscrollcommand = scrollbarY.set, height=10, width=50)
        scrollbarY.config(command = console.yview)


    def selectFile(self, text_editor, file_label):
        root = self.root
        root.filename = filedialog.askopenfilename(initialdir=".", title="Select A File", filetypes=(("lol files", "*.lol"), ("all files", "*.*")))
        
        if root.filename != "":
            with open(root.filename, 'r') as file:
                self.file = file.read()
            
            file_label.config(text = os.path.basename(root.filename)) # display the name of the selected file

            # overwrites the text editor
            text_editor.delete("1.0", END)
            text_editor.insert(END, self.file) # write the contents of the selected file