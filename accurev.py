'''
Started 10 March 2016
Python script with GUI, to complement Accurev CLI ...
... mainly for sorting results and selecting items to process.
This was created out of the need to mitigate the slowness of AccuRev GUI ...
... by leveraging the faster and detailed CLI responses.
'''

import Tkinter
import subprocess

import tkFont
import ttk

import re
import xml.etree.ElementTree as ET

import socket
import os

from datetime import datetime

window=None
commandField1=None
commandField2=None
resultListView=None

def main():
    global window
    global commandField1
    global commandField2
    global resultListView
    
    #need cross team compatibility ... check if the target folder is indeed an accurev depo - cud use os.chdir() after socket.getfqdn() find on 'show wspaces -f x'
    #earlier just thought of having this script in the wspace folder... but git folder and making it more universal came into consideration
    changeToWspaceDir()
    
    window=Tkinter.Tk()
    window.title('AccuRev Lightweight Helper')
    window.lift()
    window.attributes('-topmost', True)
    window.attributes('-topmost', False)
    
    commandField1=Tkinter.Entry(window)
    commandField1.bind('<Return>', inputEntry1Action)
    commandField1.pack()
    
    #Previosuly had tried the basic list - non-tree, w/o columns
    #resultListView=Tkinter.Listbox(window, selectmode=Tkinter.EXTENDED)
    #resultListView.pack()
    
    resultListView=MultiColumnListbox()
    
    commandField2=Tkinter.Entry(window)
    #commandField2.bind('<Return>', button2Action)
    #disabled Enter key binding to avoid rash commands for the final step
    commandField2.pack()
    
    button2=Tkinter.Button(window, text="Confirm and Execute", command=button2Action)
    button2.pack()
    
    Tkinter.mainloop()

def changeToWspaceDir():    
    print '\nTrying to detect and change to your workspace directory...'
    getWspaceCmd='accurev show wspaces -f x'
    try:
        #funny how the absence of the second parameter blanks out e.output in Exception
        wspaceResult=subprocess.check_output(getWspaceCmd, stderr=subprocess.STDOUT)
    except Exception as e:
        print 'Error...'
        print e.output
        if(re.search(r'Not authenticated',e.output)!=None):
            subprocess.call('accurev login')
            wspaceResult=subprocess.check_output(getWspaceCmd)
        else:
            print 'Quitting'
            quit(1)
    
    print wspaceResult
    wspaceDir='.'
    
    treeRoot=ET.fromstring(wspaceResult)
    for child in treeRoot:
        if child.tag.lower() == 'element':
            print "child.attrib['Host'].lower()::"+child.attrib['Host'].lower()
            print 'socket.getfqdn().lower()::'+socket.getfqdn().lower()
            if(child.attrib['Host'].lower()==socket.getfqdn().lower()):
                wspaceDir=child.attrib['Storage']
                break
    
    print wspaceDir
    os.chdir(wspaceDir)

def inputEntry1Action(event=None):
    global commandField1
    #Keeping these arrow as comment as they might be useful as other kind of separator
    #Here, the 'in and out' representations seem better
    #print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print 'Command 1 Started...'
    #print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    command1=commandField1.get()
    ###Maybe check and just use .call() for commands not requiring parsing?
    commandOutputStr=subprocess.check_output(command1)
    print commandOutputStr
    #print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
    print 'Command 1 Complete'
    ###Remove below call if using .call()
    if(re.search(r'<AcResponse',commandOutputStr)!=None):
        parseAndFillList(commandOutputStr)
    #print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<';

def button2Action(event=None):
    global commandField2
    #Keeping these arrow as comment as they might be useful as other kind of separator
    #Here, the 'in and out' representations seem better
    #print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print 'Command 2 Started...'
    #print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    command2=commandField2.get()
    getSelectedAndCall(command2)
    #print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
    print 'Command 2 Complete'
    #print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
    
# the test data ...
my_headers = ['column-1', 'column-2']
my_list = [
('row1', 'you') ,
('row2', 'can') ,
('row3', 'sort'),
('row4', 'me')
]

###todo
#pass the headings as well as the items to populate the new list
def parseAndFillList(dataListStr):
    global resultListView
    resultListView.tree.delete(*(resultListView.tree.get_children()))
    print 'Parsing Result List...'
    
    # using split for standard list (non-xml)
    #list=dataListStr.split('\r\n')
    #for i, row in enumerate(list):
    #   list[i]=((row.split(' '))[0],'Data')
    
    list=[]
    timeFormat="%d %B %Y %H:%M:%S"  #%c : The preferred date and time representation for the current locale.
    
    treeRoot=ET.fromstring(dataListStr)
    for child in treeRoot:
        if child.tag.lower() == 'element':
            filePath=child.attrib['location']
            time=datetime.fromtimestamp( float(child.attrib['modTime']) ).strftime(timeFormat)
            list.append( (filePath, time) )
    
    print list
    resultListView._build_tree(items=list)
    print 'Parsing Done'

def getSelectedAndCall(commandStr):
    global resultListView
    print 'Appending Selected Items to the Command...'
    appendStr=commandStr
    for resultItem in resultListView.tree.selection():
        #resultItem is a coded identifier for the whole row
        temp = resultListView.tree.set(resultItem)
        print temp[temp.keys()[0]]
        appendStr=appendStr+' '+temp[temp.keys()[0]]
    print appendStr
    subprocess.call(appendStr)
    print 'Executing Command...'
    
###Add reference source
"""use a ttk.TreeView as a multicolumn ListBox"""
class MultiColumnListbox(object):

    def __init__(self):
        self.tree = None
        self._setup_widgets()
        #disabled loading of test data
        #self._build_tree()

    def _setup_widgets(self):
        global window
        s = 'Click on header to sort by that column\nto change width of column, drag boundary'
        msg = ttk.Label(window, wraplength="4i", justify="left", anchor="n",
            padding=(10, 2, 10, 6), text=s)
        msg.pack(fill='x')
        container = ttk.Frame(window)
        container.pack(fill='both', expand=True)
        # create a treeview with dual scrollbars
        self.tree = ttk.Treeview(columns=my_headers, show="headings")
        vsb = ttk.Scrollbar(orient="vertical",
            command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal",
            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set,
            xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=container)
        vsb.grid(column=1, row=0, sticky='ns', in_=container)
        hsb.grid(column=0, row=1, sticky='ew', in_=container)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

    def _build_tree(self, titles=my_headers, items=my_list):
        self.tree.delete(*(self.tree.get_children()))
        
        for col in titles:
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.tree.column(col,
                width=tkFont.Font().measure(col.title()))

        for item in items:
            self.tree.insert('', 'end', values=item)
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(item):
                col_w = tkFont.Font().measure(val)
                if self.tree.column(titles[ix],width=None)<col_w:
                    self.tree.column(titles[ix], width=col_w)
        
        sortby(self.tree, titles[1], 1)

def sortby(tree, col, descending):
    """sort tree contents when a column header is clicked on"""
    # grab values to sort
    data = [(tree.set(child, col), child) \
        for child in tree.get_children('')]
    # if the data to be sorted is numeric change to float
    #data =  change_numeric(data)
    # now sort the data in place
    data.sort(reverse=descending)
    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)
    # switch the heading so it will sort in the opposite direction
    tree.heading(col, command=lambda col=col: sortby(tree, col, \
        int(not descending)))
        
main()
