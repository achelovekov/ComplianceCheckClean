
from typing import Dict, Generator, List
from pydantic import BaseModel

class Node(BaseModel):
    name: str
    bias: bool = False
    children: List['Node'] = []

Node.update_forward_refs()

def linesGeneratorFromFile(filename):
    with open(filename) as file:
        for line in file:
            line = line.rstrip()
            if line:
                yield line  

def linesGeneratorFromConfig(config):
    config = config.splitlines()
    for line in config:
        line = line.rstrip()
        if line:
            yield line 

def wordsList(line):
    return [(index, word) for index, word in enumerate(line.split())]

def getBias(line):
    count = 0
    for char in line:
        if char == " ":
            count += 1
        else:
            break
    return count

def go(parentNode:Node, wL, lastElement, nullBias):
    if wL:
        index, name = wL[0]

        if index == 0 and not nullBias:
            currentNode = Node(name=name, bias=True)
            nullBias = False
        else:
            currentNode = Node(name=name)

        lastElement = currentNode
        parentNode.children.append(currentNode)

        return go(currentNode, wL[1:], lastElement, nullBias)

    else:
        return lastElement
        
def walk(roots, prevBias, line, lastElement):
 
    wL = wordsList(line)
    currentBias = getBias(line)
    nullBias = False 

    if currentBias == 0:
        nullBias = True
    
    elif currentBias > prevBias:
        roots[currentBias] = lastElement

    lastElement = go(roots[currentBias], wL, None, nullBias)
       
    return (currentBias, lastElement)

def subTree(node:Node, path, buf):
    if path:
        if len(path) > 1:
            newPath = path[1:]
        else:
            newPath = []
        for child in node.children:
            if child.name == path[0]:
                subTree(child, newPath, buf)
    else:
        buf.append(node)

def biasChildren(node:Node) -> bool:
    res = True
    for child in node.children:
        if child.bias:
            res = res and True
        else: 
            res = res and False
    return res

def printNode(node:Node, depth, step, tmpStr, buf, filter):
    try:
        for child in node.children:
            if child.name not in filter:
                if not child.bias:
                    tmpStr = tmpStr + " " + child.name
                    if len(child.children) == 0 or biasChildren(child):
                        buf.append(tmpStr)
                    printNode(child, depth, step, tmpStr, buf, filter)
                if child.bias:
                    newDepth = depth + 1
                    tmpStr = " "*newDepth*step + child.name
                    if len(child.children) == 0:
                        buf.append(tmpStr)
                    printNode(child, newDepth, step, tmpStr, buf, filter)
    except AttributeError as e:
        print(f"may be wrong path? {e}")
        exit()

def streeFromFile(filename) -> Node:
    rootNode = Node(name='root')
    roots = {0: rootNode}
    lG = linesGeneratorFromFile(filename)
    currentBias = 0
    lastElement = None

    for line in lG: currentBias, lastElement = walk(roots, currentBias, line, lastElement) 

    return rootNode

def streeFromConfig(config) -> Node:
    rootNode = Node(name='root')
    roots = {0: rootNode}
    lG = linesGeneratorFromConfig(config)
    currentBias = 0
    lastElement = None

    for line in lG: currentBias, lastElement = walk(roots, currentBias, line, lastElement) 

    return rootNode

def printPath(
        rootNode: Node, 
        path: List, 
        filter: List):

    nodeBuf = []
    printBuf = []
    
    subTree(rootNode, path, nodeBuf) 

    for node in nodeBuf:
        printNode(node, 0, 2, '', printBuf, filter)
    
    return printBuf

if __name__ == "__main__":

    device = 'ACOD-PROD-LF10-1'

    rootNode = streeFromFile(f"RawConfigs/tmpTest/{device}/{device}-running.txt")

    #print(rootNode.json())

    path = [
        "vrf",
        "context",
        "PROD-SRV-APP"
      ]
    filter = []

    printBuf = printPath(rootNode, path, filter)
    print('\n'.join(printBuf))  
    