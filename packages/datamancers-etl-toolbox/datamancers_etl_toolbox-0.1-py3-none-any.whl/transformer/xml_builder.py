import xml.etree.ElementTree as ET
from xml.dom import minidom


def create_xml():
    """
    Create an XML structure matching the template.xml format
    """
    # Create the root element
    root = ET.Element("S5Data")
    
    # Create FirmaList element
    firma_list = ET.SubElement(root, "FirmaList")
    
    # Create Firma element with ID attribute
    firma = ET.SubElement(firma_list, "Firma")
    firma.set("ID", "a2420335-e332-43fc-b8ef-656d377f5d47")
    
    # Create Sleva element and its children
    sleva_parent = ET.SubElement(firma, "Sleva")
    
    # Add Sleva value element
    sleva = ET.SubElement(sleva_parent, "Sleva")
    sleva.text = "20.00"
    
    # Add VlastniSleva element
    vlastni_sleva = ET.SubElement(sleva_parent, "VlastniSleva")
    vlastni_sleva.text = "True"
    
    # Convert to string with proper formatting
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    
    # Remove extra blank lines that minidom sometimes adds
    pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
    
    return pretty_xml


def save_xml_to_file(xml_content, file_path):
    """
    Save XML content to a file
    
    Args:
        xml_content (str): The XML content to save
        file_path (str): The path where to save the XML file
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(xml_content)


if __name__ == "__main__":
    # Create the XML
    xml_content = create_xml()
    
    # Print the XML
    print(xml_content)
    
    # Save to file
    save_xml_to_file(xml_content, "output.xml") 