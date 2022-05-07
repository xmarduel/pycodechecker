#
import sys
#
import xml.dom.minidom
from xml.dom import Node
#
#
def getTextNodeValue(node):
    """
    """
    val = ""
    #
    for text__content_ in node.childNodes:
        if text__content_ and text__content_.nodeValue : val += text__content_.nodeValue
    return val

def replaceTextNode(doAction, doc, node, tag, old_val, new_val):
    '''
    '''
    if doAction :
        for textnode in node.childNodes:
            node.removeChild(textnode)
        #
        textnode = doc.createTextNode(new_val)
        node.appendChild(textnode)
     
def addNode(doc, node, tag, text):
    '''
    '''
    newnode  = doc.createElement(tag)
    textnode = doc.createTextNode(text)
    newnode.appendChild(textnode)
    textnode0 = doc.createTextNode('    ')
    textnode2 = doc.createTextNode('\n        ')
    
    node.appendChild(textnode0)
    node.appendChild(newnode)
    node.appendChild(textnode2)

def extractContent(parentNode, node):
    '''
    '''
    value = getTextNodeValue(node)
    #print "value =" , value
    #
    allChildNodes = node.childNodes
    while (allChildNodes):
	aChildNode = allChildNodes[0]
        #print "aNode = ", aNode
	node.removeChild(aChildNode)
        parentNode.insertBefore(aChildNode, node)
	allChildNodes = node.childNodes
				
    parentNode.removeChild(node)


def transform(filename, newfilename):
    '''
    '''
    try:
        doc  = xml.dom.minidom.parse(filename)
    except Exception as details:
        print("Error: %" % str(details))
        return
    #
    TD_fieldbody_Nodes = doc.getElementsByTagName('td')
    #
    for node in TD_fieldbody_Nodes:
        allAttrs = node.attributes
	if allAttrs:
	    attr = allAttrs.get("class", None)
	    if attr and attr.nodeValue == "field-body":
	        childNodes = node.childNodes
		for childNode in childNodes:
		    if childNode.nodeName == 'p':
		        paragraphNode = childNode
		        allParagraphAttrs = paragraphNode.attributes
	                if allParagraphAttrs:
	                    p_attr = allParagraphAttrs.get("class", None)
			    if p_attr and p_attr.nodeValue in [ "first", "last", "first last" ]:
				extractContent(node, paragraphNode)
		        else:  # paragraph without attribute
			    extractContent(node, paragraphNode)
    #
    res =  doc.toxml()
    ff = open(newfilename, "w")
    ff.write(res)
    ff.close()

    print("%s ...done" % newfilename)


if __name__ == '__main__':
    filename = sys.argv[1]
    newfilename = filename + ".mod"
    #
    transform(filename, newfilename)
