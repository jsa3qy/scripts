import sys
import os
from os import listdir
from os.path import isfile, join
import re
import json
import copy

#global variables instantiation
template2Path = {}
soyFiles = []
jsonPaths = []
file2Cfs = {}
version8 = True
usedFiles = []

def main(path):
    #global variables defined as global
    global template2Path
    global soyFiles
    global jsonPaths
    global file2Cfs
    global version8
    global usedFiles

    #Using the rootdir we get the paths to all configs
    configPaths = getConfigPaths(path)

    #this loop allows for multiple configs
    for config in configPaths:
        topSoyTemplates = []
        soyFiles = []
        jsonPaths = []
        file2Cfs = {}
        version8 = True
        usedFiles = []

        output_file_name = config.split('/')[len(config.split('/')) - 1].strip('.json') + '.txt'
        topSoyTemplates = getTopLevelTemplates(config)

        #We don't need to repeat hierarchies -- saves time here
        topSoyTemplates = list(dict.fromkeys(topSoyTemplates))

        #builds the template map, tempalte2path
        buildTemplateMap(path)

        #root node which connects all top level templates
        rootNode = nodeObj(topSoyTemplates, None, 'rootNodeTemplate', 'rootNodeFilePath', 'root node')

        #turns the children into nodes, and remembers the raw children by copying the pre-function children into that field
        rootNode = tempChildren2Nodes(rootNode)

        #turn the rootNode into the root of a tree obj
        templateHierarchy = tree(rootNode)

        #now we have children that are nodes, so we can iterate through them and add children to them!
        for index, child in enumerate(templateHierarchy.root.children):
            templateHierarchy.root.children[index] = getChildren(child)
        templateHierarchy.root = childrenRecurse(templateHierarchy.root)
        
        getAllFiles(templateHierarchy.root)

        for fileName in usedFiles:
            if ('component' not in fileName or 'override' in fileName):
                getCustomField(fileName)
        
        exportCustomFields(output_file_name)

    print('\n')
    print('finished with custom field audit')

def getAllFiles(node):
    global usedFiles
    if node.file:
        usedFiles.append(node.file)
    for child in node.children:
        getAllFiles(child)

def getCustomField(path):
    global file2Cfs
    global version8
    cfs = []

    try:
        tmpFile = open(path, 'r')
    except:
        return

    namespace = ''
    for line in tmpFile:
        #if the line is too long give up, it will get stuck
        if len(line) > 200:
            continue 
        if (not version8 and re.findall('\$customByName', line)):
            cf = re.search('(customByName(.*)])', line)
            if cf:
                cf = cf.group(1)
                if file2Cfs.get(path) != None:
                    file2Cfs[path].append(cf.strip())
                else:
                    file2Cfs[path] = [cf.strip()]
        elif (version8 and re.findall('\$profile', line)):
            cf = re.search('(profile.c(.*)(}| |]|))', line)
            cf2 = re.search('(profile\[(.*)\])', line)
            if cf:
                cf = cf.group(1)
                if file2Cfs.get(path) != None:
                    file2Cfs[path].append(cf.strip().split(' ')[0].split('}')[0].replace('?','').split('|')[0].strip(')') + ' ' + path)
                else:
                    file2Cfs[path] = [cf.strip().split(' ')[0].split('}')[0].replace('?','').split('|')[0].strip(')') + ' ' + path]
            if cf2:   
                cf2 = cf2.group(1)
                if file2Cfs.get(path) != None:
                    file2Cfs[path].append(cf2.strip() + ' ' + path)
                else:
                    file2Cfs[path] = [cf2.strip() + ' ' + path]
    return    

def exportCustomFields(exportFileName):
    global file2Cfs
    myFile = open(exportFileName, "w")
    uniques = []
    for key in file2Cfs.keys():
        uniques+=file2Cfs[key]

    uniques = sorted(list(dict.fromkeys(uniques)))

    for index,unique in enumerate(uniques):
        unique = unique.split(' /Users')
        myFile.write(unique[0] + '\n' + unique[1].split('templates/')[1] + '\n \n')

def getTopLevelTemplates(path):
    global version8
    tmpFile = open(path, 'r')
    tmpList = []
    for line in tmpFile:
        if re.search('\"templateVersion\":', line):
            try:
                version8 = (re.search('(8)', line).group(1) == '8')
            except:
                version8 = False
        #if "template" is in the line then we're going to grab what follows -- i.e. the top level template
        if re.search("\"template\"", line):
            stripIndex = line.find('template')
            template = line[stripIndex + len('template": '):]
            tmpList.append(template.strip().strip(",").strip("\""))
    return tmpList

def buildTemplateMap(path):
    global soyFiles
    global template2Path

    templatesDir = path + 'src/templates'

    #explanation within function 
    recurse(templatesDir)
    
    #adding to map, template name --> file path
    for fileName in soyFiles:
        addToMap(fileName)

def recurse(rootdir):
    #grab all files else recurse on directories within, and then add them all to the global soyFiles to be used in map construction 
    for filename in os.listdir(rootdir):
        onlyfiles = []
        onlyDirs = []

        #if we're a soy file
        if isfile(join(rootdir, filename)) or re.search('.soy', filename):
            onlyfiles.append(join(rootdir, filename))

        #otherwise we're a directory
        else: 
            onlyDirs.append(join(rootdir, filename))

        #if we have found any files, add them to our list of files
        if (len(onlyfiles) > 0):
            for fileN in onlyfiles:
                soyFiles.append(fileN)

        #otherwise we need to recurse on all directories we found (and look for files and further directories within those)
        else:
            for dirN in onlyDirs:
                recurse(join(join(rootdir, filename), dirN))

def addToMap(path):
    global template2Path
    templates = []
    tmpFile = open(path, 'r')
    namespace = ''
    for line in tmpFile:
        #if the line is too long give up, it will get stuck
        if len(line) > 200:
            continue
        if (re.search('(.*){namespace (.*)}', line) or (re.search('(.*){template (.*)}', line))):
            if re.search('namespace', line):
                namespace = re.search('(.*){namespace (.*)}', line).group(2)
            if re.search('{template', line):
                template = re.search('{template (.*)( |})', line)
                if template:
                    template = template.group(1)
                    template2Path[namespace.strip() + template.strip()] = path
    return

def getConfigPaths(path):
    configPaths = []
    for filename in os.listdir(rootdir):
        if filename.startswith('config.') and filename.endswith('.json'):
            configPaths.append(join(path, filename))
    return configPaths

#CLASSES USED
class tree:
    #only used to define the graph as a whole, give us something to reference that links to the entirety of the graph
    def __init__(self, rootNode):
        self.root = rootNode

class nodeObj:
    def __init__(self, children, parent, template, filePath, data):
        self.children = children #list of nodeobjs
        self.childrenRaw = [] #list of raw children, readable
        self.parent = parent #points to parent node
        self.template = template #what template does this node represent
        self.file = filePath #what is the filepath to this template
        self.data = data #a string describing anything arbitrary we'd like to to keep track of 

    def addChildren(self, listOfChildren):
        self.children += listOfChildren #add a a list of children to the chidlren field of self
    
    def toString(self):
        #prints all children to any arbitrary level
        print('Children: ')
        for child in self.children:
            child.tempString()

        #prints arbitrary data field of parent
        if self.parent:
            print('Parent: ' + self.parent.data)
        print('Template: ' + self.template) #print template
        print('File: ' + self.file) #prints file that this template lives in
        if self:
            print('data: ' + self.data) #prints data element of child
        print('')

    #prints the template of a node and all templates of children within (to any arbitrary level)
    def tempString(self):
        print('Template: ' + self.template)
        print(' ')
        for i in self.children:
            i.tempString()

def tempChildren2Nodes(node):
    node.childrenRaw = copy.deepcopy(node.children)
    for index,template in enumerate(node.children):
        node.children[index] = nodeObj([], node, template, template2Path.get(template), '')
    return node

def getChildren(node):
    if node.file and node.template:
        #if we run into a component or cobalt that's not overridden, we don't need to go into it
        if ((('components' in node.template) or ('cobalt' in node.template)) and 'override' not in node.file):
            node.children = []
            return node 

        #get the indices where the template name starts and ends
        start, end = returnStartAndEndLine(node.template, node.file)
        #pass in those indices 
        node.children = getCallsInLines(start, end, node.file)
        node = tempChildren2Nodes(node)
    return node

def returnStartAndEndLine(template, filePath):
    try:
        open(filePath, 'r')
    except:
        return 0, 0

    file = open(filePath, 'r')
    startBool = False
    start = 0
    for lineNum,line in enumerate(file):
        if (re.search('(.*){namespace (.*)}', line)):
            if re.search('namespace', line):
                namespace = re.search('(.*){namespace (.*)}', line).group(2).strip()
            template = template.replace(namespace, '', 1)
        if re.search('{template ' + template, line):
            start = lineNum
            startBool = True
        if re.search('{/template}', line) and start:
            end = lineNum
            return start, end

def getCallsInLines(startLine, endLine, filePath):
    try:
        file = open(filePath, 'r')
    except:
        return []

    childrenCalls = []  
    namespace = ''
    for lineNum,line in enumerate(file):
        if (re.search('(.*){namespace (.*)}', line)):
            if re.search('namespace', line):
                namespace = re.search('(.*){namespace (.*)}', line).group(2).strip()
        if lineNum < endLine and lineNum > startLine:
            if len(line) > 200:
                continue
            if (re.search('(.*){call (.*)}', line)):
                if re.search('{call (.*)( |data)', line):
                    call = re.search('{call (.*)( |data).*', line).group(1)
                    if call:
                        if call[0] == '.':
                            if re.search('data=', call):
                                call = call.split(" ")[0].strip()
                            childrenCalls.append(namespace + call)
                        else:
                            if re.search('data=', call):
                                call = call.split(" ")[0]
                            childrenCalls.append(call.strip())
    return list(dict.fromkeys(childrenCalls))

def getCalls(path):
    childrenCalls = []
    if not path:
        return []
    tmpFile = open(path, 'r')  
    namespace = ''
    for line in tmpFile:
        if len(line) > 200:
            continue
        if (re.search('(.*){namespace (.*)}', line) or (re.search('(.*){call (.*)}', line))):
            if re.search('namespace', line):
                namespace = re.search('(.*){namespace (.*)}', line).group(2).strip()
            if re.search('{call (.*)( |data)', line):
                call = re.search('{call (.*)( |data).*', line).group(1)
                if call:
                    if call[0] == '.':
                        if re.search('data=', call):
                            call = call.split(" ")[0].strip()
                        childrenCalls.append(namespace + call)
                    else:
                        if re.search('data=', call):
                            call = call.split(" ")[0]
                        childrenCalls.append(call.strip())
    return list(dict.fromkeys(childrenCalls))

def walker(src, res):
    for name, value in src.items():
        node = {'name': name}
        if name not in res:
            res[name] = []
        res[name].append(node)
        walker(value, node)

def childrenRecurse(node):
    if (node.file and node.template):
        if (('components' in node.template or 'cobalt' in node.template) and 'override' not in node.file):
            node.children = []
            return node 
    if len(node.children) == 0:
        node = getChildren(node)
    for index,child in enumerate(node.children):
        node.children[index] = getChildren(child)
        if len(getChildren(child).children) > 0:
            for index2,grandchild in enumerate(node.children[index].children):
                node.children[index].children[index2] = childrenRecurse(grandchild)
    return node

if __name__ == "__main__":
    repo_path = '/Users/jalloy/repo/'

    #rootdir is how we know where to get the config file from
    rootdir = '/Users/jalloy/repo/locations.tacobell.com/'
    
    #we can pass cmd line argument rootdir if we don't want to change it in the code
    if len(sys.argv) > 1:
        rootdir = repo_path + sys.argv[1] + '/'
    else:
        print('No argument passed, please pass name path of repo from $REPO folder that needs CF audit')
    
    #main function at the top of the file 
    main(rootdir)