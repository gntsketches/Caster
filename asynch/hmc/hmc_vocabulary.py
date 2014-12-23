from Tkinter import Frame, Label, Entry, Checkbutton
import sys
import time
BASE_PATH = r"C:\NatLink\NatLink\MacroSystem"
if BASE_PATH not in sys.path:
    sys.path.append(BASE_PATH)
import Tkinter as tk
from asynch.hmc.homunculus import Homunculus
from lib import settings







QTYPE_SET="set"
QTYPE_REM="rem"





class Homunculus_Vocabulary(Homunculus):
    
    def get_row(self, cut_off=0):
        result = self.grid_row - cut_off
        self.grid_row += 1
        return result

    def __init__(self, params):
        global QTYPE_SET
        global QTYPE_REM
        self.grid_row = 0
        Homunculus.__init__(self, params[0])
        self.title(settings.HOMUNCULUS_VERSION + " :: Vocabulary Manager")
        
        self.last_key=""
        self.bind("<Control-Key>", self.key)
            
        self.mode = params[0]
        clipboard_text=params[1]
        
        if self.mode == QTYPE_SET:
            self.geometry("640x480+" + str(int(self.winfo_screenwidth() / 2 - 320)) + "+" + str(int(self.winfo_screenheight() / 2 - 240)))
            self.instructions = "Add/Modify Word"
            Label(self, text=self.instructions, name="pathlabel").grid(row=self.get_row(), column=1, sticky=tk.E)
                      
            wf_row = self.get_row()
            Label(self, text="(W)ord:", name="wordlabel").grid(row=wf_row, column=0, sticky=tk.W)
            self.word_box = Entry(self, name="word_box")
            self.word_box.grid(row=wf_row, column=1, sticky=tk.W)
            if clipboard_text!=None:
                self.word_box.insert(0, clipboard_text)
            
            p_row = self.get_row()
            Label(self, text="(P)ronunciation:", name="pronunciationlabel").grid(row=p_row, column=0, sticky=tk.W)
            self.pronunciation_box = Entry(self, name="pronunciation_box")
            self.pronunciation_box.grid(row=p_row, column=1, sticky=tk.W)
            
            
            
            Label(self, text="Options", name="optionslabel").grid(row=self.get_row(), column=1, sticky=tk.E)
            self.word_state = []
            cb_number = 1
            for state in [("Word added by user", 0x00000001),
                          ("Can't be deleted", 0x00000008),
                          ("Usually cap next (like period)", 0x00000010),
                          ("Always cap next (like Cap Next)", 0x00000020),
                          ("Uppercase next (All Caps Next)", 0x00000040),
                          ("Lowercase next (No Caps Next)", 0x00000080),
                          ("No space following (left paren)", 0x00000100),
                          ("Two spaces following (period)", 0x00000200),
                          ("No spaces between words (numbers)", 0x00000400),
                          ("Capitalization mode on (Caps On)", 0x00000800),
                          ("Uppercase mode on (All Caps On)", 0x00001000),
                          ("Lowercase mode on (No Caps On)", 0x00002000),
                          ("Space betw words off (No Space On)", 0x00004000),
                          ("Restore normal spacing (No Space Off)", 0x00008000),
                          ("Suppress period (...)", 0x00020000),
                          ("No formatting (like Cap)", 0x00040000),
                          ("No reset spacing (like Cap)", 0x00080000),
                          ("No reset caps (close quote)", 0x00100000),
                          ("No space preceeding (comma)", 0x00200000),
                          ("Restore normal caps (Caps Off)", 0x00400000),
                          ("Follow with new line (New-Line)", 0x00800000),
                          ("Follow with new-p (New-Paragraph)", 0x01000000),
                          ("Don't cap in title (like and)", 0x02000000),
                          ("Follow with extra space (space)", 0x08000000),
                          ("Word added by vocab builder.", 0x40000000)
                          
                          ]:
                cb_row = 0  # self.get_row()
                cb_col = 0
                row_cut_off = 14
                col2_inc = -1
                word_state_var = tk.IntVar()
                
                if cb_number == 1:
                    word_state_var.set(True)
                    
                if cb_number < row_cut_off:
                    cb_row = cb_row = self.get_row()
                else :
                    cb_row = cb_row = self.get_row(row_cut_off + col2_inc)
                    cb_col = 2
                    col2_inc += 1
                
                Checkbutton(self, text="(" + str(cb_number) + ")", variable=word_state_var).grid(row=cb_row, column=cb_col + 1, sticky=tk.W)
                cb_number += 1
                Label(self, text=state[0], name="cb_label" + str(cb_number)).grid(row=cb_row, column=cb_col, sticky=tk.W)
                self.word_state.append((word_state_var, state[1]))
        elif self.mode == QTYPE_REM:
            self.geometry("300x100+" + str(int(self.winfo_screenwidth() / 2 - 150)) + "+" + str(int(self.winfo_screenheight() / 2 - 50)))
            
            self.instructions = "Delete Word"
            Label(self, text=self.instructions, name="pathlabel").grid(row=self.get_row(), column=1, sticky=tk.E)
                      
            wf_row = self.get_row()
            Label(self, text="(W)ord:", name="wordlabel").grid(row=wf_row, column=0, sticky=tk.W)
            self.word_box = Entry(self, name="word_box")
            self.word_box.grid(row=wf_row, column=1, sticky=tk.W)
        
        
        
    
    def complete(self, e):
        ''''''   
        global QTYPE_SET
        response={"mode": self.mode}
        word=self.word_box.get()
        if len(word)==0:
            self.on_exit()
        response["word"]=word
        if self.mode==QTYPE_SET:
            
            pronunciation=self.pronunciation_box.get()
            if len(pronunciation)==0:
                pronunciation=""
            response["pronunciation"]=pronunciation
            word_info=0x00000000
            for ws in self.word_state:
                if ws[0].get()==1:
                    word_info+=ws[1]
            response["word_info"]=word_info
        with self.server.lock:
            self.server.response=response
        self.withdraw()
    
    def key(self, e):
        global QTYPE_REM
        '''acceptable keys are numbers and w and p'''
        if self.mode!=QTYPE_REM:
            if e.keycode in [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 80, 87]:
                self.last_key+=chr(e.keycode)
            if self.last_key in ["W", "P"] or len(self.last_key)==2:
                if self.last_key=="W":
                    ''' focus word box '''
#                     self.unhide()
#                     self.word_box.focus_force()
#                     self.word_box.focus_set() 
                    self.word_box.focus_set()
                elif self.last_key=="P":
                    ''' focus pronunciation box '''
                    self.pronunciation_box.focus_set()
                else:
                    box_index=int(self.last_key)
                    if box_index>=1 and box_index<=25:
                        if self.word_state[box_index-1][0].get()==0:
                            self.word_state[box_index-1][0].set(True)
                        else:
                            self.word_state[box_index-1][0].set(False)
                
                self.last_key=""
            

