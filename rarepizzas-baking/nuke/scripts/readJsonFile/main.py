import os
import sys
from os import walk
import json
import fnmatch

#get path to render of selected node
node = nuke.selectedNode()
CGRenderNode = node['name'].value()
#modify the path to get the directory of the json files
renderImagePath = nuke.toNode(CGRenderNode).knob('file').value()
indivfilename = renderImagePath.split("/")[-1]
pathtoSearchForJson = renderImagePath.replace(indivfilename,"")
pathtoSearchForJson = pathtoSearchForJson.replace("beauty", "object_deep_id")
#set lists to add the extracted data too for each json file / frame of render
shaderNameList = []
geoNameList = []
objectCountList = []
fileNameList = []
jsonFileList = []

#filling in places where there might might issues
jsonFileCount = len(fnmatch.filter(os.listdir(pathtoSearchForJson), '*.json'))
errorMsg = 'Info Not Found'
for i in range(jsonFileCount):
    shaderNameList.append(errorMsg)
    geoNameList.append(errorMsg)
    objectCountList.append(errorMsg)
    #fileNameList.append(errorMsg)
    jsonFileList.append(errorMsg)

#for all the json files in the modified path get the data
for root, dirs, files in os.walk(pathtoSearchForJson):
    for fileName in sorted(files):
        if fileName.endswith(".json"):
            
            fileNameList.append(fileName)
for jsonFile in fileNameList:
    with open(str(pathtoSearchForJson+jsonFile)) as f:
        data = json.load(f)
    #extract the json data
    RAWmaterialsList = data["attributes"][0]["values"]
    RAWgeometryList = data["attributes"][1]["values"]
    for item in RAWmaterialsList:
        shaderName = item.split("/")[-1]
        shaderNameList[int(jsonFile.split(".")[-2])-1001] = shaderName
        #print shaderName
                        
        assetName = str(RAWgeometryList[0].split("/")[-2])
        geoName = assetName
        geoNameList[int(jsonFile.split(".")[-2])-1001] = geoName
        #print geoName
    
        objectCount = len(RAWgeometryList)
        objectCountList[int(jsonFile.split(".")[-2])-1001] = objectCount

        jsonFileList[int(jsonFile.split(".")[-2])-1001] = jsonFile
        #print objectCount


nodeNameList = []
for node in nuke.selectedNodes():
    CGRenderNode = node['name'].value()
    renderImagePath = nuke.toNode(CGRenderNode).knob('file').value()
    pathtoSearchForJson = renderImagePath.split("/")[-1]
    pathtoSearchForJson = pathtoSearchForJson.replace(str(".####.exr"),".json")
    renderImagePath = renderImagePath.replace("beauty", "object_deep_id")
    pathtoSearchForJson = renderImagePath.replace(str(".####.exr"),".json")  
    sourceFormat = node.format()
    
    #create reformat node matching the format of the render
    newReformatNode = nuke.createNode('Reformat')
    newReformatNodeName =  newReformatNode['name'].value()
    nuke.toNode(newReformatNodeName).knob('format').setValue(sourceFormat.name())

    #create text node   
    newTextNode = nuke.createNode('Text')
    newTextNodeName =  newTextNode['name'].value()
    #sets a python expression in the text node which referance lists and variables in this script
    nuke.toNode(newTextNodeName).knob('message').setValue("Asset Name: [python {geoNameList[int(nuke.frame()-1001)]}]"+"\n"+ "Shader Name: [python {shaderNameList[int(nuke.frame()-1001)]}]"+"\n"+"Object count (approx): [python {objectCountList[int(nuke.frame()-1001)]}]")
    nuke.toNode(newTextNodeName).knob('size').setValue(30)
    nuke.toNode(newTextNodeName).knob('xjustify').setValue("left")
    
    #create write node for the asset info to be written out to as images locally
    RAWnaming = renderImagePath.strip(".####.exr")
    RAWnaming = RAWnaming.split("/")[-1]
    outputPath = RAWnaming+"_assetInfoRef.####.exr"
    alteredOutputPath = renderImagePath.replace("ivy/CG/{0}/object_deep_id/2156x903/".format(RAWnaming),"REF/assetInfoRenderOUT/")
    newWriteNode = nuke.createNode('Write')
    newWriteNodeName =  newWriteNode['name'].value()
    nk.toNode(newWriteNodeName).knob('file').setValue(alteredOutputPath)
    nk.toNode(newWriteNodeName).knob('create_directories').setValue(True)
    
    #selected all the newly created nodes and separate them form the node tree to be rendered spearately. you can then merge in the out put of this.
    createdNodes = [newReformatNode,newTextNode,newWriteNode]
    for i in createdNodes: 
        i.setSelected(True)
    nuke.extractSelected()
#set frame range to number of json files plus offset
nuke.knob("root.last_frame",str(1001+jsonFileCount))
