#!/usr/bin/python
import dbus, gobject, dbus.glib, sys, optparse, datetime, tempfile, os, string, urllib
import getpass
from login import HttpRpcServer

def GetUserCredentials():
    """Prompts the user for a username and password."""
    email = None
    if email is None:
        email = raw_input("Email: ")
        
        password_prompt = "Password for %s: " % email
        password = getpass.getpass(password_prompt)
        return (email, password)
        


def printUsage():
    print "Use better"
    
class Tommy:
    listCount = 10
    try:
        bus = dbus.SessionBus()
    except:
        print "Could not connect to dbus session"
        exit
    try:
        obj = bus.get_object("org.gnome.Tomboy", "/org/gnome/Tomboy/RemoteControl")
        tomboy = dbus.Interface(obj, "org.gnome.Tomboy.RemoteControl")
    except:
        print "Could not connect to Tomboy"
        exit
    noteName = ""
    verbose = False
    #xml = False
    tags = []
    text = ""
    #startdate
    #enddate
        
    def appendNote(self):    
        noteURI = self.findNoteString(self.noteName)
        oldNote = self.tomboy.GetNoteContents(noteURI)
        print oldNote
        newText = getInput()
        oldNote = self.tomboy.GetNoteContentsXml(noteURI) 
        oldNote = oldNote[:-15] + newText + "\n</note-content>"
        self.tomboy.SetNoteContentsXml(noteURI, oldNote)
    
    def editNote(self):
        noteURI = self.findNoteString(self.noteName)
        oldNote = self.tomboy.GetNoteContentsXml(noteURI)
        
        (fd, tfn) = tempfile.mkstemp()
        
        os.write(fd, oldNote)
        os.close(fd)
        editor = os.environ.get("editor")
        if not (editor):
            editor = os.environ.get("EDITOR")
        if not (editor):
            editor = "vi"
        os.system(editor + " " + tfn)
        file = open(tfn,'r')
        contents = file.read()
        try:
            self.tomboy.SetNoteContentsXml(noteURI,contents)
        except:
            print "Your XML was malformed. Edit again (Y/N)?"
            answer = ""
            while (answer.lower() != 'n' and answer.lower() != 'y'):
                answer = getInput(1)
            if (answer.lower() == 'y'):
                self.editNote()
    
    def findNoteString(self,mystring):
        mystring = mystring.lower()
        allNotes = self.tomboy.ListAllNotes()
        for noteURI in allNotes:
            title = self.tomboy.GetNoteTitle(noteURI)
            #if mystring in title.lower():
            if title.lower().find(mystring,0) == 0:
                return noteURI
    
    def findMostRecentNote(self):
        allNotes = self.tomboy.ListAllNotes()
        bestDate = self.tomboy.GetNoteChangeDate(self.tomboy.FindNote(allNotes[0]))
        recentNote = allNotes[0]
        for note in allNotes:
            date = self.tomboy.GetNoteChangeDate(note)
            if (date > bestDate):
                bestDate = date
                recentNote = note
        return recentNote
    
    #for arg in sys.argv:
    def search(self):
        if self.noteName:
            words = self.noteName.lower().split(" ")
            print words
            noteURIs = self.tomboy.SearchNotes(self.noteName, False)
            if noteURIs:
                for noteURI in noteURIs:
                    title = self.tomboy.GetNoteTitle(noteURI)
                    note = self.tomboy.GetNoteContents(noteURI)
                    notel = note.lower()
                    leftpos = 1e10
                    rightpos = 0
                    for w in words:
                        lp = notel.find(w, len(title))
                        rp = notel.rfind(w)
                        if (lp < leftpos): leftpos=lp
                        if (rp > rightpos): rightpos=rp
                    tmp1 = note.rfind(" ",0,leftpos-15)+1
                    if (tmp1 > leftpos): tmp1 = leftpos
                    tmp2 =  note.rfind("\n",0,leftpos)+1
                    if (tmp1>tmp2): leftpos = tmp1
                    else: leftpos = tmp2
                    tmp1 = note.find(" ", rightpos+20)
                    if tmp1 < rightpos: tmp1=rightpos+20
                    tmp2 = note.find("\n", rightpos)
                    if tmp2 < rightpos: tmp2=tmp1
                    if (tmp1<tmp2): rightpos = tmp1
                    else: rightpos = tmp2
                    if (leftpos < 0): leftpos = 0
                    if (rightpos > len(note)): rightpos = len(note)
                    print title + ": ..." + note[leftpos:rightpos] + "..."
            else:
                print "No notes with search term \"" + self.noteName + "\" found."
        return
    
    def displayNote(self):
        if self.noteName:
            note = self.getNote(self.noteName, False)
            if note:
                print note
            else:
                noteURI = self.findNoteString(self.noteName)
                if noteURI:
                    print self.tomboy.GetNoteContents(noteURI)
                else:
                    print "No note found begining with title  " + self.noteName            
        else:
            noteURI = self.findMostRecentNote()
            print self.tomboy.GetNoteContents(noteURI)
        
        
    def getNote(self, name, full):
        if full:
            return self.tomboy.GetNoteContentsXml(self.tomboy.FindNote(name))
        else:
            return self.tomboy.GetNoteContents(self.tomboy.FindNote(name))
    
    def listNotes(self, listCount):
        loopCount=0;
        for noteURI in self.tomboy.ListAllNotes(): 
            note = self.tomboy.GetNoteTitle(noteURI)
            if "Template" not in note:
                dt = datetime.datetime.fromtimestamp(self.tomboy.GetNoteChangeDate(noteURI))
                printString = dt.strftime("%D | ")
                tags = self.tomboy.GetTagsForNote(noteURI)
                printString += note
                if tags:
                    printString += "  ("
                    for t in tags:
                        if ("system:notebook:" in t):                        
                            printString += t[16:]
                        else:
                            printString += t
                        printString += ", "
                    printString = printString[:-2] + ")"
                print printString
            loopCount+=1
            if loopCount == listCount:
                break


    def uploadNote(self):
        if self.noteName:
            note = self.getNote(self.noteName, False)
            if note:
                print note
            else:
                noteURI = self.findNoteString(self.noteName)
                if noteURI:
                    #print resp
                    self.doUpload(noteURI,self.tomboy.GetNoteCompleteXml(noteURI))
                else:
                    print "No note found begining with title  " + self.noteName            
        else:
            print "Must specify title of note to upload"


    def uploadAllNotes(self):
        h = HttpRpcServer("tomboyweb.appspot.com",GetUserCredentials)
        h._Authenticate()
        for noteURI in self.tomboy.ListAllNotes(): 
            self.doUpload(h,noteURI,self.tomboy.GetNoteCompleteXml(noteURI))


    def doUpload(self,server, URI, noteContent):
        #if need Google auth to remote server
       
        resp = server.Send("/sendnote",urllib.urlencode({"noteid" :self.tomboy.GetNoteTitle(URI) , "note" : noteContent}))
        #else do this (simple)
        #data = urllib.urlencode({"noteid" : URI, "note" : noteContent})
        #f = urllib.urlopen("http://localhost:8080/sendnote",data)
        print resp
 




def argsToString(args):
    if (args):
        full_string = ""
        for a in args:
            full_string += a + " "
        full_string = full_string[:-1]
        return full_string

def processDateString(dateString):
    try:
        date = datetime.datetime.strptime(dateString, "%d/%m/%y")
    except:
        #if (verbose): print "Cannot parse date " + dateString + ". Ignoring"
        return
    return date

def va_callback(option, opt_str, value, parser):
    assert value is None
    done = 0
    value = []
    vals = getattr(parser.values, option.dest)
    if vals:
        for v in vals:
            value.append(v)
        value.append(",")
    rargs = parser.rargs
    while rargs:
        arg = rargs[0]

        if ((arg[:2] == "--" and len(arg) > 2) or
            (arg[:1] == "-" and len(arg) > 1 and arg[1] != "-")):
            break
        else:
            value.append(arg)
            del rargs[0]
    setattr(parser.values, option.dest, value)

def getInput():
    mystring = ""
    while(True):
        line = sys.stdin.readline()
        if not line:
            break
        mystring += line
    return mystring

def main():
    parser = optparse.OptionParser("%prog <mode> [<option>,...] [\"Note Title\"]")
    parser.add_option("-a", "--append", dest="append", action="store_true", help="Append to an existing note")
    parser.add_option("-c", "--create", dest="create", action="store_true", help="Create a new note")
    parser.add_option("-d", "--display", dest="display",action="store_true",help="Print a note to terminal")
    parser.add_option("-u", "--upload", dest="upload",action="store_true",  help="Upload a note")
    parser.add_option("-U", "--uploadAll", dest="uploadAll",action="store_true",  help="Upload ALL notes")
    parser.add_option("-e", "--edit", dest="edit", action="store_true",     help="Interactively edit a note")
    #parser.add_option("-l", "--list", dest="list", action="callback", callback=va_callback)
    parser.add_option("-l", "--list", dest="list", action="store_true",     help="List recent notes")
    parser.add_option("-L", "--listall", dest="listall", action="store_true",help="List all notes")
    parser.add_option("-s", "--search", dest="search", action="store_true", help="Search for text in notes")


    parser.add_option("-t", "--tag", dest="tag", action="store")
    parser.add_option("-x", "--xml", dest="xml", action="store_true")
    parser.add_option("--no-xml", dest="forcexml", action="store_false")
    parser.add_option("--force-xml", dest="forcexml", action="store_true")
    parser.add_option("--startdate", dest="startdate", action="store")
    parser.add_option("--enddate", dest="enddate", action="store")
    parser.add_option("--count", dest="count", action="store", type="int")
    (options, args) = parser.parse_args()

    modeCount = 0
    if (options.append): modeCount+=1
    if (options.create): modeCount+=1
    if (options.display): modeCount+=1
    if (options.upload): modeCount+=1
    if (options.uploadAll): modeCount+=1
    if (options.edit): modeCount+=1
    if (options.list): modeCount+=1
    if (options.listall): modeCount+=1
    if (options.search): modeCount+=1
    if (modeCount < 1):
        options.list = True
    if (modeCount > 1):
        print "Only one of {append, create, display, edit, list, search} can be specified. Use '--help' for details"
        sys.exit(1)
        
    noteName = argsToString(args)       
    listCount = 10
    if (options.count):
        listCount = options.count
    if (options.listall):
        options.list = True
        listCount = -1
   
    t = Tommy()
    t.noteName = noteName

    t.startDate = processDateString(options.startdate)
    t.endDate = processDateString(options.enddate)       
    
    if (options.append):
        t.appendNote()
        
    if (options.edit):
       t.editNote()
        
        
    if (options.list):
        t.listNotes(listCount)
        
    if (options.display):
        t.displayNote()

    if (options.upload):
        t.uploadNote()

    if (options.uploadAll):
        t.uploadAllNotes()

    if (options.search):
        t.search()
    

main()
