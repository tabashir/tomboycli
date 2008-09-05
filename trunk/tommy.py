import dbus, gobject, dbus.glib, sys, optparse, datetime, tempfile, os

def printUsage():
    print "Use better"
    
class Tommy:
    listCount = 10
    bus = dbus.SessionBus()
    obj = bus.get_object("org.gnome.Tomboy", "/org/gnome/Tomboy/RemoteControl")
    tomboy = dbus.Interface(obj, "org.gnome.Tomboy.RemoteControl")
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
    
    def findNoteString(self,string):
        string = string.lower()
        allNotes = self.tomboy.ListAllNotes()
        for noteURI in allNotes:
            title = self.tomboy.GetNoteTitle(noteURI)
            if string in title.lower():
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
                    print "No note found with " + self.noteName + " in title"            
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
            
def stuff(tomboy):
    # Display the Start Here note                                      
    tomboy.DisplayNote(tomboy.FindStartHereNote()) 
    # Display the title of every note 
    
    
    # Display the contents of the note called Test
    print tomboy.GetNoteContents(tomboy.FindNote("Test"))
    # Add a tag to the note called Test
    tomboy.AddTagToNote(tomboy.FindNote("Test"), "sampletag")
    # Display the titles of all notes with the tag 'sampletag'
    for note in tomboy.GetAllNotesWithTag("sampletag"):
        print tomboy.GetNoteTitle(note)

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
    string = ""
    while(True):
        line = sys.stdin.readline()
        if not line:
            break
        string += line
    return string

def main():
    parser = optparse.OptionParser("%prog <mode> [<option>,...] [\"Note Title\"]")
    parser.add_option("-a", "--append", dest="append", action="store_true")
    parser.add_option("-c", "--create", dest="create", action="store_true")
    parser.add_option("-d", "--display", dest="display",action="store_true")
    parser.add_option("-e", "--edit", dest="edit", action="store_true")
    #parser.add_option("-l", "--list", dest="list", action="callback", callback=va_callback)
    parser.add_option("-l", "--list", dest="list", action="store_true")
    parser.add_option("-L", "--listall", dest="listall", action="store_true")
    parser.add_option("-s", "--search", dest="search", action="store_true")


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
    if (options.edit): modeCount+=1
    if (options.list): modeCount+=1
    if (options.listall): modeCount+=1
    if (options.search): modeCount+=1
    if (modeCount < 1):
        printUsage()
    if (modeCount > 1):
        print "Only one of {append, create, display, edit, list, search} can be specified"
        
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
    
  
    #if (options.append):
    #    appendNote(tomboy,options.append)
    if (options.append):
        t.appendNote()
        
    if (options.edit):
       t.editNote()
        
        
    if (options.list):
        t.listNotes(listCount)
        
    if (options.display):
        t.displayNote()

    if (options.search):
        t.search()
    

main()
#list(tomboy)
#print getNote(tomboy,"some", False)
#tomboy.DisplayNote(tomboy.FindNote("some"))
#stuff(tomboy)
