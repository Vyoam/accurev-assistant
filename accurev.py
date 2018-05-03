'''
Started 10 March 2016
Python script with GUI, to complement Accurev CLI ...
... mainly for sorting results and selecting items to process.
This was created out of the need to mitigate the slowness of AccuRev GUI ...
... by leveraging the faster and detailed CLI responses.
'''

# to do? http://stackoverflow.com/questions/6548837/how-do-i-get-an-event-callback-when-a-tkinter-entry-widget-is-modified link to activate custom when field changed manually?
# to do, update button?

import Tkinter
import subprocess

import tkFont
import ttk

import re
import xml.etree.ElementTree as ET

import socket
import os

import sys #
import traceback #

from datetime import datetime

window=None
commandField1=None
commandField2=None
resultListView=None

defaultCommandOptionStr="List modified elements"
defaultCommandOptionValStr='accurev stat -f x -m'

commandOptionsDict = {defaultCommandOptionStr:defaultCommandOptionValStr,
                      "List kept":'accurev stat -f x -k',
                      "List pending":'accurev stat -f x -p',
                      "List overlapping":'accurev stat -f x -o',
                      "List external":'accurev stat -f x -x',
                      "List missing":'accurev stat -f x -M',
					  "List files status for the folder":'accurev stat -f x -s <stream like Auth_BLR_Pepper_InternalEvents_Lane> <path like db\appdbs\auth30\cdata\*>',
                      "List default group":'accurev stat -f x -d',
                      "List default group, Parent Stream":'accurev stat -f x -d -b',
                      "List default group, Custom Stream":'accurev stat -f x -d -s <stream>',
                      "Update preview":'accurev update -i -f x', #response doesn't return status... maybe one of the reason GUI is slow... it fetches status one by one?
                      "Custom command":'accurev <cmd>'}

defaultCommandOptionStr2="Keep selected"
defaultCommandOptionValStr2='accurev keep -c ""'

commandOptionsDict2 = {defaultCommandOptionStr2:defaultCommandOptionValStr2,
                      "Diff against backed":"accurev diff -b -G",
                      "Diff against backed (custom stream)":"accurev diff -b -v <stream> -G",
                      "Revert selected to backed":'accurev purge',
                      "Promote selected":'accurev promote -c ""',
                      "Update":"accurev update",
                      "Show status of selected (console o/p)": "accurev stat -f x",
                      "Custom command":'accurev <cmd>'}                   
                      
def main():
    global window
    global commandField1
    global commandField2
    global resultListView
    global defaultCommandOptionStr
    global commandOptionsDict
    global defaultCommandOptionStr2
    global commandOptionsDict2
    
    #using accurev, detect the workspace folder for the system and cd to that folder
    changeToWspaceDir()
    
    window=Tkinter.Tk()
    window.title('AccuRev Assistant')
    window.lift()
    window.attributes('-topmost', True)
    window.attributes('-topmost', False)
    
    label1Text = 'Select a command from list, or type in the field...\nThen press enter or the button to enlist elements...'
    label1 = ttk.Label(window, wraplength="4i", justify="left", anchor="n", padding=(10, 2, 10, 6), text=label1Text)#, background="DarkSeaGreen2" , font="default 9 bold")
    label1.pack(fill='x')
    
    #>>>
    container1=ttk.Frame(window)
    container1.pack()
    
    defaultCommandOption=Tkinter.StringVar(container1)
    defaultCommandOption.set(defaultCommandOptionStr)
    commandOptions=commandOptionsDict.keys()
    commandMenu=Tkinter.OptionMenu(container1, defaultCommandOption, *commandOptions, command=fillCommandField1)
    commandMenu.config(bg="DarkSeaGreen2")
    commandMenu.pack(side=Tkinter.LEFT, padx=10)
    
    commandField1=Tkinter.Entry(container1, bg="DarkSeaGreen1")
    commandField1.bind('<Return>', inputEntry1Action)
    commandField1.pack(side=Tkinter.LEFT, padx=10)
    
    button1=Tkinter.Button(container1, text="Execute", command=inputEntry1Action, bg="SeaGreen3")
    button1.pack(side=Tkinter.LEFT, padx=10)
    #<<<
        
    resultListView=MultiColumnListbox()
    
    label2Text = 'Select elements and apply operation...\nWhere required, insert comments inside the quotes...'
    label2 = ttk.Label(window, wraplength="4i", justify="left", anchor="n", padding=(10, 2, 10, 6), text=label2Text)
    label2.pack(fill='x')
    
    #>>>
    container2=ttk.Frame(window)
    container2.pack()
    
    defaultCommandOption2=Tkinter.StringVar(container2)
    defaultCommandOption2.set(defaultCommandOptionStr2)
    commandOptions2=commandOptionsDict2.keys()
    commandMenu2=Tkinter.OptionMenu(container2, defaultCommandOption2, *commandOptions2, command=fillCommandField2)
    commandMenu2.config(bg="DarkSlateGray2")
    commandMenu2.pack(side=Tkinter.LEFT, padx=10)
    
    commandField2=Tkinter.Entry(container2, bg="DarkSlateGray1")
    #commandField2.bind('<Return>', button2Action)
    #disabled Enter key binding to avoid rash commands for the final step
    commandField2.pack(side=Tkinter.LEFT, padx=10)
    
    button2=Tkinter.Button(container2, text="Confirm and Execute", command=button2Action, bg="RoyalBlue1")
    button2.pack(side=Tkinter.LEFT, padx=10)
    #<<<
    
    fillCommandField1(defaultCommandOptionStr)
    fillCommandField2(defaultCommandOptionStr2)
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
        if(re.search(r'Not authenticated', e.output)!=None) or (re.search(r'Expired', e.output)!=None):
            print 'Login...'
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
            if(re.search(socket.getfqdn().lower(),child.attrib['Host'].lower())!=None) or (re.search(child.attrib['Host'].lower(),socket.getfqdn().lower())!=None): #changed from equals comparison after accurev update (child.attrib['Host'].lower()==socket.getfqdn().lower())
                wspaceDir=child.attrib['Storage']
                break
    
    print wspaceDir
    os.chdir(wspaceDir)

def inputEntry1Action(event=None):
    global commandField1

    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print 'Command 1 Started...'
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    command1=commandField1.get()
    ###Maybe check and just use .call() for commands not requiring parsing?
    commandOutputStr=subprocess.check_output(command1)
    print commandOutputStr
    print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
    print 'Command 1 Complete'
    ###Remove below call if using .call()
    if(re.search(r'<AcResponse',commandOutputStr, re.IGNORECASE)!=None):
        parseAndFillList(commandOutputStr)
    print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<';

def button2Action(event=None):
    global commandField2
    
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print 'Command 2 Started...'
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    command2=commandField2.get()
    getSelectedAndCall(command2)
    print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
    print 'Command 2 Complete'
    print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
    
def fillCommandField1(option):
    global commandField1
    global commandOptionsDict
    
    commandField1.delete(0,Tkinter.END)
    commandField1.insert(0,commandOptionsDict[option])
    
def fillCommandField2(option):
    global commandField2
    global commandOptionsDict2
    
    commandField2.delete(0,Tkinter.END)
    commandField2.insert(0,commandOptionsDict2[option])
    
# the test data ...
my_headers = ['location', 'modTime', 'status', 'namedVersion']
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
    global my_headers
    
    print 'Parsing Result List...'
    list=[]
    headers=my_headers
    timeFormat="%d %B %Y %H:%M:%S"
    messageStr='Not Available'
    
    try:
        treeRoot=ET.fromstring(dataListStr)
        for child in treeRoot:
            if child.tag.lower() == 'message': # for update preview
                messageStr=child.text
                
            elif child.tag.lower() == 'element':
            
                filePath=matchKeyAndGetVal(child, 'location') #child.attrib['location']
                
                temp=matchKeyAndGetVal(child, 'modTime')
                
                try:
                    temp=float(temp)
                except ValueError:
                    print "Not a float. modTime N/A."
                    temp=None
                    
                if(temp):
                    time = str(temp)+' = '+datetime.fromtimestamp( temp ).strftime(timeFormat)
                else:
                    time='N/A'
                
                status=matchKeyAndGetVal(child, 'status') #child.attrib['status']
                
                if status == 'N/A':
                    status=messageStr # for update preview
                
                namedVersion=matchKeyAndGetVal(child, 'namedVersion') #child.attrib['namedVersion']
                
                list.append( (filePath, time, status, namedVersion) )
        
        #print list
        #need change here to call specific code to change the columns only instead of the below costlier call. P.S. doesn't work well either - creates extra box, column re-linking doesn't happen
        #resultListView._setup_widgets(titles=headers)
        resultListView._build_tree(titles=headers, items=list)
        
        print 'Parsing Done'
        
    except Exception as e:
        print "Error. Couldn't finish parsing..."
        print e
        traceback.print_exc() #
        #sys.exc_info()

def matchKeyAndGetVal(dict, keyPattern):
    for key in dict.keys():
        if(re.search(keyPattern, key, re.IGNORECASE)!=None):
            return dict.attrib[key]
    return 'N/A'
        
def getSelectedAndCall(commandStr):
    global resultListView
    print 'Appending Selected Items to the Command...'
    appendStr=commandStr
    for resultItem in resultListView.tree.selection():
        #resultItem is a coded identifier for the whole row
        temp = resultListView.tree.set(resultItem)
        #print temp[temp.keys()[0]] # using first column as the one contaning file name
        #appendStr=appendStr+' '+temp[temp.keys()[0]]
        print temp['location']
        appendStr=appendStr+' \"'+temp['location']+'\"'
    print appendStr
    subprocess.call(appendStr)
    print 'Executing Command...'
    
### Ref. http://stackoverflow.com/questions/5286093/display-listbox-with-columns-using-tkinter >>>
"""use a ttk.TreeView as a multicolumn ListBox"""
class MultiColumnListbox(object):

    def __init__(self):
        self.tree = None
        self._setup_widgets()
        #disabled loading of test data
        #self._build_tree()

    def _setup_widgets(self, titles=my_headers):
        global window
        
        container = ttk.Frame(window, width=1600, height=500) #ref. .grid_propagate(0) http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/ttk-Frame.html
        container.grid_propagate(0)
        container.pack(fill='both', expand=True)
        # create a treeview with dual scrollbars
        self.tree = ttk.Treeview(columns=titles, show="headings")
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
        
        max_width=729
        
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
                if col_w>max_width: # limit width
                    col_w=max_width
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

### <<<
        
main()
