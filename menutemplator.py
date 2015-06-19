import os
import sys

class MenuGenerator:
 rootUrl = ""
 logoHTML  = ""
 parentPath = ""

 def __init__(self, root, path):
  self.rootUrl = root
  self.parentPath = path

 def readFile(self,filename):
  txt = open(filename)
  print "Reading file: " + filename
  return txt.read()

 def scanFolder(folder,extensions, exclude):
  for dirname, dirnames, filenames in os.walk(folder):
   for subdirname in dirnames:
    print (os.path.join(dirname, subdirname))

  for filename in filenames:
   print (os.path.join(dirname, filename))

 def parseMenu(self,menus):
  title = ""
  link = ""
  depth = ""
  folder = ""
  ms = []
  for i in range(0, len(menus) - 1):
   line = menus[i]
   if line.startswith("--") == False:
    ms.append([title,link,depth,folder])
    title = line
    link = ""
    depth = ""
    folder = ""
   elif line.startswith("--l"):
    link = line[len("--l::"):]
   elif line.startswith("--f"):
    folder = line[len("--f::"):]
   elif line.startswith("--d"):
    depth = line[len("--d::"):]
   
  ms.append([title,link,depth,folder])
  return ms

 def buildMenuFromFolder(self,name):
  f = open(name,'w+')
  print "Implement AutoDiscover in buildMenuFromFolder"
  entries = []
  entries.append([name, name])
  return entries

 def getMenuEntryFromFile(self,parenturl, fname):
  if os.path.isfile(fname):
   mfile = open(fname)
   ftext = mfile.read().split('\n')
   entries = []
   for text in ftext:
    if (text == ""):continue
    iSeperator = text.index("::")
    title = text[:iSeperator]
    url = text[iSeperator + len("::"):]
    #url is relative
    if url.startswith("http") == False:
     url = rootUrl + "/" + parenturl + "/" + url
    else:
     url = url
    entries.append([title, url])
  else:
   entries = self.buildMenuFromFolder(fname)
  return entries

 def processSubmenu(self,path,menu,level):
  html = ""
  strLvl = str(level)
  if (level < int(menu[2])):
   html = "<div class=\"submenu "+strLvl+"\">"
   html+= "<div class=\"menu-container\">"
   if menu[3] != "":
    childpath = os.path.join(path, menu[3])
    entries = self.getMenuEntryFromFile(menu[3],childpath + "/menu.mhtml") 
   else:
    print "Implement links"

   for entry in entries:
    html+= "<div class=\"menu-lvl-" + str(level + 1) + " menu-item \">"
    html+= "<a href=\"" + entry[1] + "\">" + entry[0] + "</a>"
    html+= "</div>"
   
   html+= "</div>"
   html+= "</div>"
  return html 

 def addLink(self,text, url):
  #url is not absolute
  if (url.startswith("http") == False):
    url = rootUrl+"/" + url
  return "<a href=\"" + url + "\">" + text + "</a>"

 def processMenus(self,path,menus):
  html = "<div id=\"nav-menu\" class=\"nav\">"
  print len(menus)
  for i in range(0,len(menus)):
   menu = menus[i]
   print "Processing Top Menu " + menu[0]
   if (menu[0] !=""):
    toplevel = "<div class=\"menu-lvl-1 menu-item\">\n"
    if (menu[1] != ""): #links
     toplevel += self.addLink(menu[0], menu[1])
    else:
     toplevel += "<span class=\"parent topmenu\">" + menu[0] + "</span>\n"
     toplevel += self.processSubmenu(path,menu,1) + "\n"
    toplevel += "</div>\n"
    html += toplevel
  html += "\n</div>"
  return html
    

 def readMenu(self,path):
  txt = self.readFile(path + "/menu").split('\n')
  print ("Reading configuration file from " + path)
  for i in range (0, len(txt) - 1):
   line = txt[i]
   if line.startswith("Extensions:"):
    extensions = line[len("Extensions:"):].split('\;')
    print ("Extensions:" + line)
   if line.startswith("DirExclude:"):
    exclude = line[len("DirExclude:"):].split('\;')
    print ("exclude:" + line)
   if line.startswith("Logo:"):
    self.logoHTML = line[len("Logo:"):]
    print ("logo:" + self.logoHTML)
   if line.startswith("~BEGIN:"):
    menus = self.parseMenu(txt[i+1:])
  return self.processMenus(path,menus)

 def updateLogo(self,html, logo):
  print "Processing logo " + logo
  if logo != "":
   startindex = html.index("<!--generate:logo-->") + len("<!--generate:logo-->")
   eol = html.index("<!--end:logo-->")
   html = html[:startindex] + "\n" + "<div id='logo'>\n" + logo + "\n</div>\n" + html[eol:]
  return html

 def updateMenu(self,path, navHtml):
  f = open(path, 'r+')
  html = f.read()
  html = self.updateLogo(html, self.logoHTML)
  startindex = html.index("<!--generate:menu-->") + len("<!--generate:menu-->")
  eom = html.index("<!--end:menu-->")
  html = html[:startindex] + "\n" + navHtml + html[eom:]
  f.seek(0)
  f.write(self.processRaw(html)) 
  f.truncate()
  f.close()

 def updateFiles(self,path,fname, text):
  print "Starting to update file\n"
  fPath = path + "/" + fname;
  f = open(fPath, 'r')
  files = f.read().split('\n')
  for i in range(0,len(files)):
   if (files[i]!='' and files[i].startswith('#') == False):
    if files[i].startswith('.'):
     files[i] = files[i][1:]
    print "Processing " + files[i] + " in " + path + "\n"
    self.updateMenu(path + "/" + files[i], text)

 def processRaw(self,html):
  words = {"{ROOTPATH}": rootUrl, "{}":""}
  for key,value in words.iteritems():
   html = html.replace(key,value)
  return html


 def oddJobBottom(self,path, navHtml):
  f = open(path, 'r+')
  html = f.read()
  html = self.updateLogo(html, self.logoHTML)
  startindex = html.index("</body>")
  eom = html.index("</html>")
  html = html[:startindex] + "\n" + navHtml + html[eom:]
  f.seek(0)
  f.write(self.processRaw(html)) 
  f.truncate()
  f.close()

 def updateFilesOddJob(self,path,fname, text):
  print "Starting to run odd job update file\n"
  fPath = path + "/" + fname;
  f = open(fPath, 'r')
  files = f.read().split('\n')
  for i in range(0,len(files)):
   if (files[i]!='' and files[i].startswith('#') == False):
    if files[i].startswith('.'):
     files[i] = files[i][1:]
    print "Processing " + files[i] + " in " + path + "\n"
    self.oddJobBottom(path + "/" + files[i], text)

rootUrl = ""
if len(sys.argv) > 1:
 path = sys.argv[1]
 if len(sys.argv) > 2:
  rootUrl = sys.argv[2]

 gen = MenuGenerator(path, rootUrl)
 htmlNav = gen.readMenu(path)
 print "logo is " + gen.logoHTML
 gen.updateFiles(path,"menufiles", htmlNav)
 #gen.updateFilesOddJob(path,"menufiles","<body>\n<script type='text/javascript' src='/js/common/mobilemenu.js'></script>\n")
 
