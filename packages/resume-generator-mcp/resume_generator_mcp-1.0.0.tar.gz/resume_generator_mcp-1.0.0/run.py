import zipfile
import xml.etree.ElementTree as ET
import shutil
import os

def replace_text_in_docx(docx_path, old_text, new_text):
    # Step 1: Extract the DOCX file
    with zipfile.ZipFile(docx_path, 'r') as zip_ref:
        extract_dir = docx_path.replace('.docx', '')
        zip_ref.extractall(extract_dir)

    # Step 2: Locate the document.xml file
    document_xml_path = os.path.join(extract_dir, 'word', 'document.xml')

    # Step 3: Parse the document.xml file
    tree = ET.parse(document_xml_path)
    root = tree.getroot()

    # Define namespaces to remove the 'w' prefix from tags in XML
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

    # Step 4: Replace old_text with new_text in document.xml
    for elem in root.findall('.//w:t', namespaces):
        if old_text in elem.text:
            elem.text = elem.text.replace(old_text, new_text)

    # Step 5: Write the changes back to document.xml
    tree.write(document_xml_path, xml_declaration=True, encoding='UTF-8')

    # Step 6: Rezip the folder back into a DOCX file
    new_docx_path = docx_path.replace('.docx', '_modified.docx')
    shutil.make_archive(extract_dir, 'zip', extract_dir)
    shutil.move(extract_dir + '.zip', new_docx_path)

    # Clean up extracted files
    #shutil.rmtree(extract_dir)

    return new_docx_path

# Example usage
docx_path = 'resume.docx'
new_docx = replace_text_in_docx(docx_path, 'Sravan', 'John')
print(f"Modified DOCX file saved as: {new_docx}")

