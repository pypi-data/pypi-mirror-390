import xml.etree.cElementTree as ET


def xml2dict(xmlstr):
    xml_tree = ET.fromstring(xmlstr)
    xmldict = {k.tag: k.text for k in xml_tree}
    return xmldict
