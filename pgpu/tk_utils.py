'''
Tkinter widgets and helper functions.

AUTHORS:
v0.2.0+         --> pydsigner
'''

from tkinter2x.font import families
import tkinter2x as tk
from tkinter2x.constants import *
import tkinter2x.scrolledtext as stext

OLDSTYLE_FONTS = ['ShadowedBlack', 'Benighted', 'Old English Text']
FLOWING_FONTS = ['Palace Script MT', 'Bradley Hand ITC', 'French Script',
        'French Script MT', 'Edwardian Script ITC', 'Blackadder ITC',
        'Script Bold', 'Script MT Bold', 'Zola', 'Vivaldi']
SEMIFLOWING_FONTS = ['URW Chancery L']
SANS_FONTS = ['Liberation Sans', 'FreeSans', 'DejaVu Sans', 'Sans']
MONO_FONTS = ['Liberation Mono', 'DejaVu Sans Mono', 'Monospace', 'FreeMono']
ALLCAP_FONTS = ['Algerian', 'Castellar']


def best_font(master, fonts=[]):
    '''
    Returns the first font name in @fonts that tkinter can find. Pass a Tk() 
    instance to @master.
    
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    sysfonts = families(root=master)
    for font in fonts:
        if font in sysfonts:
            return font


class SList(tk.Frame):
    '''
    A basic scrolling list display based on Mark Lutz's ScrolledList() widget 
    from Programming Python, 3rd edition.
    
    AUTHORS:
    v1.0.2+         --> pydsigner/Mark Lutz
    '''
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        
        sbar = tk.Scrollbar(self)
        l = tk.Listbox(self, relief=SUNKEN)
        
        sbar.config(command=l.yview)
        l.config(yscrollcommand=sbar.set)
        
        sbar.pack(side=RIGHT, fill=Y)
        l.pack(side=LEFT, expand=YES, fill=BOTH)
        
        self.listbox = l
    
    def set(self, l):
        '''
        Fill the listbox.
        '''
        self.listbox.delete(0, END)
        self.listbox.insert(END, *l)


class TextPlus(tk.Text):
    '''
    A version of Text() with additional methods for getting, setting, and 
    clearing the text contained by it. The afore mentioned methods are based on
    some from Mark Lutz's scrolledtext.ScrolledText() widget as seen in 
    Programming Python, 3rd Edition.
    
    AUTHORS:
    v0.4.4+     --> pydsigner/Mark Lutz
    '''
    def gettext(self):
        return self.get('1.0', END + '-1c')
    def settext(self, text):
        self.clear()
        self.insert('1.0', text)
    
    def clear(self):
        self.delete('1.0',END)


class STextPlus(stext.ScrolledText, TextPlus):
    '''
    A simple subclass of TextPlus() with scrolling.
    
    AUTHORS:
    v0.2.0-v0.4.3   --> pydsigner/Mark Lutz
    v0.4.4+         --> pydsigner
    '''


class Console(TextPlus):
    '''
    An extension of TextPlus() widget that additionally acts like a file. 
    However, due to the implications of being editable externally e.g. by 
    someone using an interface, Console() uses a cache that must be manually 
    refresh()ed.
    
    AUTHORS:
    v0.4.4+         --> pydsigner
    '''
    def __init__(self, master, *args, **kw):
        TextPlus.__init__(self, master, *args, **kw)
        self.refresh()
    
    def get_fresh(self):
        '''
        Returns True if the content of the widget has changed since the last 
        refresh(), otherwise it returns False.
        '''
        return self._oldcache == self.gettext()
    
    def refresh():
        '''
        Refresh the cache (equivalent to closing and opening a file).
        '''
        self._cache = self._oldcache = self.gettext()
    
    def peek(size=-1):
        '''
        Same as read, but does not affect the cache.
        '''
        val = self.read(size)
        self._cache = val + self._cache
        return val
    
    ### Standard file read methods
    
    def read(size=-1):
        if size < 0:
            size = len(self._cache)
        sz = int(size)
        res = self._cache[:sz]
        self._cache = self._cache[sz:]
        return res
    
    def readline(size=-1):
        maxdata = self.peek(size)
        pos = maxdata.find('\n')
        if pos != -1:
            return self.read(pos + 1)
        else:
            return self.read(size)
    
    def readlines(size=-1):
        '''
        Uses .readline() to get lines; if size is positive, the total data 
        size will be roughly bounded by it.
        '''
        res = []
        dsize = 0
        while 1:
            data = self.readline()
            dsize += len(data)
            if not data:
                return res
            res.append(data)
            if size > 0 and dsize >= size:
                return res
    
    ### Standard file write methods
    
    def write(self, data):
        self.insert(END + '-1c', data)
    
    def writelines(self, seq):
        [self.write(line) for line in seq]
    xwritelines = writelines


class SConsole(stext.ScrolledText, Console):
    '''
    A simple subclass of Console() with scrolling.
    
    AUTHORS:
    v0.4.4+         --> pydsigner
    '''


class RadioBar(tk.Frame):
    '''
    A RadioBar mega widget. Borrows from Mark Lutz's demoRadio.Demo() widget 
    in Programming Python, 3rd Edition.
    
    AUTHORS:
    v0.2.0+         --> pydsigner/Mark Lutz
    '''
    def __init__(self, parent=None, default=None, picks=[], side=LEFT, 
            anchor=W):
        '''
        Pass the desired master to @parent. If @default is not None, the radio 
        bar will initialized to it. @side and @anchor will be passed to the 
        packer for each RadioButton() created with a value from @picks.
        '''
        tk.Frame.__init__(self, parent)
        self.var = tk.StringVar()
        for pick in picks:
            rad = tk.Radiobutton(self, text=pick, value=pick, variable=self.var)
            rad.pack(side=side, anchor=anchor, expand=YES)
        if default != None:
            self.var.set(default)
    
    def state(self):
        return self.var.get()


class FontDialog(tk.Toplevel):
    '''
    A font picker megawidget.
    
    AUTHORS:
    v0.2.2+         --> pydsigner
    '''
    def __init__(self, defaults = ('courier', 11, 'normal'), **kw):
        '''
        @default determines the default font. **@kw is passed to the 
        Toplevel() providing the window the font picker is displayed in.
        '''
        tk.Toplevel.__init__(self, **kw)
        
        self.title('Choose Font')
        self.protocol('WM_DELETE_WINDOW', self.cancel)
        
        self.preview = tk.Label(self, font=('courier', 15, 'bold'), text='Font')
        self.preview.pack(side=TOP)
        
        buttonbar = tk.Frame(self)
        tk.Button(buttonbar, text='Ok', command=self.ok).pack(side=LEFT)
        tk.Button(buttonbar, text='Cancel', command=self.cancel
                ).pack(side=RIGHT)
        buttonbar.pack(side=BOTTOM)
        
        self.font = tk.StringVar()
        self.bold = tk.IntVar()
        
        if 'bold' in defaults[2]:
            self.bold.set(1)
        self.italic = tk.IntVar()
        if 'italic' in defaults[2]:
            self.italic.set(1)
        
        modbar = tk.Frame(self)
        mleft = tk.Frame(modbar)
        self.size = tk.IntVar()
        self.size.set(defaults[1])
        
        tk.OptionMenu(mleft, self.size, 
                7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 20, 22, 24).pack(side=TOP)
        tk.Checkbutton(mleft, variable=self.bold).pack(side=TOP)
        tk.Checkbutton(mleft, variable=self.italic).pack(side=TOP)
        mleft.pack(side=LEFT)
        mright = tk.Frame(modbar)
        tk.Label(mright, text='size').pack(side=TOP)
        tk.Label(mright, text='bold').pack(side=TOP)
        tk.Label(mright, text='italic').pack(side=TOP)
        mright.pack(side=LEFT)
        modbar.pack(side=RIGHT)
        fontbar = tk.Frame(self)
        self.font = tk.StringVar()
        tk.OptionMenu(fontbar, self.font, *sorted(self.fonts())).pack()
        self.font.set(defaults[0])
        fontbar.pack(side=LEFT)
        self.update()
        self.grab_set()
        self.focus_set()
        self.wait_window()
    
    def update(self):
        self.preview['font'] = self.getfont()
        self.after(100, self.update)
    
    def getfont(self):
        modifiers = ('bold ' if self.bold.get() else '' + 
                'italic' if self.italic.get() else '').rstrip()
        if not modifiers:
            modifiers = 'normal'
        return (self.font.get(), self.size.get(), modifiers)
    
    def ok(self):
        self.result = self.getfont()
        self.destroy()
    
    def cancel(self):
        self.result = None
        self.destroy()
    
    def fonts(self):
        res  = []
        for font in families(self):
            res.append(font.lower())
        return res


def ask_font(*args, **kw):
    '''
    Shortcut for using FontDialog(). *@args and **@kw will be passed to the 
    FontDialog() creator.
    
    AUTHORS:
    v0.2.2+         --> pydsigner
    '''
    return FontDialog(*args, **kw).result

