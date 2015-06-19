import os
import sys

rootUrl = ''
def processRaw(html):
 words = {"{ROOTPATH}": rootUrl, "{}":""}
 for key,value in words.iteritems():
  html = html.replace(key,value)
 return html

class SingleLevelProperties:
 item = ''
 properties = ''

class ProcessingJob:
 targetFile=""
 templateFile=""
 properties = []
 items = ""
 result = ""

 def __init__(self, target, template, items):
  self.targetFile = target
  self.templateFile = template
  self.items = items
 
 def readFile(self, filename):
  txt = open(filename)
  print "Opening file " + filename
  return txt.read()

 def getTag(self, line, offset):
  return line[9 + offset:len(line) - 3]

 def getSingleLevelProperties(self, item):
  self.properties = []
  if len(item.innerTags) > 0:
   for tag in item.innerTags:
    if len(tag.innerTags) == 0:
     self.properties.append(tag.tag)
  return self.properties
 
 def getLoopedItems(self, item, tag):
  results = []
  for iTag in item:
   if iTag.tag == tag:
    results.append(iTag)
  return results

 def getItemProperty(self, item, prop):
  for tag in item.innerTags:
   if tag.tag == prop:
    return tag.getValue()
  return "ERR"
 
 def processLoop(self, tag, item, txts):
  #assuming top level
  result = ""
  index = 0
  items = self.getLoopedItems(item, tag)
  for i in items:
   properties = self.getSingleLevelProperties(i)
   index = 0
   while index < len(txts):
    line = txts[index]
    if line.startswith("<!--loop:") and line.endswith("-->"):
     innerTag = self.getTag(line, 0)  
     startingLine = index + 1
     index = startingLine
     processTxt = ''
     while line != "<!--eloop:"+innerTag + "-->" and index < len(txts):
      line = txts[index]
      processTxt += '\n' + line
      index = index + 1
     result = result + '\n' + self.processLoop(innerTag, i.innerTags, processTxt.split('\n'))
    currentLine = ''
    if line.find('{' + tag + '}') > -1:
     line = currentLine = line.replace('{' + tag + '}', i.getValue())
     result = result + '\n' +  currentLine
    for prop in properties:
     if line.find('{' + prop + '}') > -1:
      line = currentLine = line.replace('{' + prop + '}', self.getItemProperty(i,prop))
    if currentLine != '':
     result = result + '\n' + currentLine
    else:
     result = result + '\n' + line
    index = index + 1
  return result

 def processLine(self, line):
  return '\n' + line

 def writeToTargetFile(self):
  f = open(targetFile, 'r+')
  html = f.read()
  startindex = html.index("<!--generate:TEMPLATE-->") + len("<!--generate:TEMPLATE-->")
  eom = html.index("<!--end:TEMPLATE-->")
  html = html[:startindex] + "\n" + self.processTemplateFile() + html[eom:]
  f.seek(0)
  f.write(processRaw(html)) 
  f.truncate()
  f.close()
  

 def processTemplateFile(self):
  txt = self.readFile(self.templateFile).split('\n')
  tag = ''
  mode = ''
  index = 0
  result = ''
  currentItem = self.items
  while index < len(txt):
   line = txt[index].strip()
   if line.startswith("<!--loop:") and line.endswith("-->"):
    tag = self.getTag(line, 0)  
    startingLine = index + 1
    processTxt = ''
    while line != "<!--eloop:"+tag + "-->" and index < len(txt):
     index = index + 1
     line = txt[index]
     processTxt += '\n' + line
    result = result + self.processLoop(tag, currentItem, processTxt.split('\n'))
   else:
    result = result + self.processLine(line)
   index = index + 1
  return result

class TemplateItem:
 tag = ""
 title = ""
 innerTags = list()
 rawText = []
 level = 0

 def __init__(self, tag, title, text, level):
  self.tag = tag
  self.title = title
  self.rawText = text
  self.rawText.append('')
  self.level = level
  self.innerTags = list()
  self.processInnerTags()

 def nextLevelText(self):
  return "-" * (self.level + 1) + " "

 def currentLevelText(self):
  return "-" * (self.level) + " "

 def isNextLevel(self, line):
  return line.startswith(self.nextLevelText())
 
 def getValue(self):
  if self.title != '':
   return self.title
  else:
   return self.innerText()

 def getTitle(self, line):
  return line[line.index(":.:")+3:]

 def getTag(self, line):
  #first space to ::
  return line[len(self.nextLevelText()):line.index(":.:")]

 def processInnerTags(self):
  print "Processing level " + str(self.level) + ":" + self.tag
  inner = self.rawText
  innerTag = ''
  title = ''
  startingLine = 0
  foundEnd = False
  index = 0
  while index < len(inner):
   line = inner[index]
   if innerTag == '' and self.isNextLevel(line):
    innerTag = self.getTag(line)
    title = self.getTitle(line)
    startingLine = index
    print "Found tag " + innerTag
   elif innerTag != '' and (self.isNextLevel(line) or line == ''):
    print "Process inner tag:" + innerTag + " starting: " + str(startingLine) + " to " + str(index)
    templateItem = TemplateItem(innerTag, title, inner[startingLine:index], int(self.level + 1))
    self.innerTags.append(templateItem)
    innerTag = '' #clear to prepare for the next one   
    index = index - 1 #redo the current line
   index = index + 1
  print "End Processing level " +  str(self.level) + ":" + self.tag

 def innerText(self):
  result = ''
  for x in self.rawText:
   line = x.strip()
   if line.startswith(self.currentLevelText()) == False and line.endswith(":.:") == False:
    result = result + '\n' + str(line)
  return result

 def listInnerContent(self):
  print "Printing " + self.tag + " " + self.title
  if len(self.innerTags) > 0:
   for item in self.innerTags:
    item.listInnerContent()
  else:
    print self.tag + ":" + self.innerText()

class ContentGenerator:
 contentFile = ""
 tags = []

 def __init__(self, fpath):
  self.contentFile = fpath

 def readFile(self):
  txt = open(self.contentFile)
  print "Opening file " + contentFile
  return txt.read()

 def stripTags(self, taggedLine):
  res = taggedLine;
  if (res.startswith("::")):
   res = res[2:]
  if res.endswith("::"):
   res = res[:len(res) - 2]
  if res.find(":.:") > -1:
   res = res[0:res.index(":.:")]
  return res

 def addTag(self, line):
  tag = self.stripTags(line)
  return tag

 def endTag(self, line):
  tag = self.stripTags(line)
  tag = tag[1:] #strip out the E as well
  return tag

 def processMainFile(self):
  txt = self.readFile().split('\n') #read line by line
  tagStarting = 0
  tagEnding = 0

  for lIndex in range(0, len(txt)):
   line = txt[lIndex]
   if (line.startswith("::")):
    #add tag if it doesn't exist
    tag = self.addTag(line)
    if (tag != ''):
     tagStarting = lIndex + 1
   elif (line == '' and tag != ''):
     print "Processing tag " + tag + "..."
     tagEnding = lIndex - 1
     self.tags.append(TemplateItem(tag, tag, txt[tagStarting:lIndex], 0))
     tag = ''
  
 def listTemplateItems(self):
  for item in self.tags:
   item.listInnerContent()

if len(sys.argv) > 1:
 contentFile = sys.argv[1]  

gen = ContentGenerator(contentFile)
gen.processMainFile()
gen.listTemplateItems() 

if len(sys.argv) > 2:
 templateFile = sys.argv[2]
 targetFile = sys.argv[3]
if len(sys.argv) == 5:
 rootUrl = sys.argv[4]

job = ProcessingJob(targetFile, templateFile, gen.tags)
#print job.processTemplateFile()
job.writeToTargetFile()
