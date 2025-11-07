import xml.etree.ElementTree as ET
import os
import re


def find_nodes_by_path(root, path, namespaces):
    """
    Find nodes in an XML tree using an absolute path, accounting for the root node.
    :param root: The root node of the XML tree.
    :param path: The absolute path to find nodes, starting from the root.
    :param namespaces: A dictionary mapping namespace prefixes to URIs.
    :return: A list of all nodes matching the path. Empty if no match is found.
    """
    def _find_recursive(node, parts, namespaces):
        # If there are no more parts, return the current node
        # This is the base case of the recursive function
        if not parts:
            return [node]

        # Get the next parts of the path
        # If there are no next parts, set next_parts to an empty list
        # This is the recursive case of the function
        next_parts = parts[1:] if len(parts) > 1 else []

        # Get the current part of the path
        part = parts[0]
        # If the part contains a namespace prefix, replace it with the corresponding URI
        if ':' in part:
            # Split the part into prefix and tag
            prefix, tag = part.split(':', 1)
            # Get the URI corresponding to the prefix
            uri = namespaces.get(prefix, '')
            # Replace the part with the full namespace URI and tag
            # Example: replace 'ubl:Invoice' with '{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice'
            # This is the format ElementTree uses for namespaces
            part = f"{{{uri}}}{tag}"

        # At the first level, compare part with the root's tag; check if the tag ends with the part
        # This check is made to account for the path starting with the root node
        if node == root:
            # If the root node's tag ends with the part, remove the first part from the list of parts
            if node.tag.endswith(part):
                # Update the part and next_parts based on the root node's tag
                part = parts[1]
                # If there are more than 2 parts, update next_parts accordingly
                next_parts = parts[2:] if len(parts) > 2 else []
                # Same as before, replace the part with the full namespace URI and tag if necessary
                if ':' in part:
                    prefix, tag = part.split(':', 1)
                    uri = namespaces.get(prefix, '')
                    part = f"{{{uri}}}{tag}"

        found_nodes = []
        # Recursively search for nodes matching the current part in the children of the current node
        for child in node:
            if child.tag.endswith(part):
                found_nodes.extend(_find_recursive(
                    child, next_parts, namespaces))
        return found_nodes

    # Normalize and split the path, removing the initial '/' if present
    parts = path[1:].split('/') if path.startswith('/') else path.split('/')

    # Start the recursive search from the root with the given path parts
    matched_nodes = _find_recursive(root, parts, namespaces)

    return matched_nodes


class XMLDataExtractorItemLists:
    def __init__(self, xml_tree, result_dict, namespaces=None):
        self.xml_tree = xml_tree
        self.result_dict = result_dict
        self.namespaces = namespaces if namespaces is not None else {}

    def extract_list_data(self, parent_path, columns):
        """
        Extract data from the XML tree for a list of items.
        :param parent_path: The path to the parent node of the list.
        :param columns: A list of tuples containing the path to the data and the corresponding column name.
            The column name is the field guid from WebCon that will be used in the body for the API request.
        :return: A list of dictionaries, where each dictionary contains the extracted data for an item in the list.
        """
        list_data = []
        # Try to find the parent node based on the parent_path
        child_row_nodes = find_nodes_by_path(
            self.xml_tree, parent_path, self.namespaces)
        # For each child node, extract the data based on the columns
        for row_node in child_row_nodes:
            row_data = {}
            # For each column, extract the data
            # The column_path is the path is a sub-path of the parent_path
            for column_path, column_name in columns:
                # If the column_path contains an '@', then it is an attribute
                if '@' in column_path:
                    # Split the path and attribute name by the '@' character which separates the path from the attribute name
                    element_path, attribute_name = column_path.rsplit('@', 1)
                    child = find_nodes_by_path(
                        row_node, element_path, self.namespaces)
                    # If the child list is not empty, then extract the attribute value
                    if len(child) > 0:
                        child = child[0]
                    # If the child list is empty, then the attribute value is None
                    else:
                        child = None
                    # Extract the attribute value
                    value = child.get(
                        attribute_name) if child is not None else None
                else:
                    # If the column_path does not contain an '@', then it is a sub-element
                    child = find_nodes_by_path(
                        row_node, column_path, self.namespaces)
                    # If the child list is not empty, then extract the text value
                    if len(child) > 0:
                        child = child[0]
                    else:
                        child = None
                    # Extract the text value only if the child list is not empty
                    # Otherwise, the value is None
                    # The strip() method is used to remove leading and trailing whitespaces
                    value = child.text.strip() if child is not None and child.text is not None else None
                row_data[column_name] = value
            list_data.append(row_data)

        return list_data

    def extract_all_lists(self):
        all_lists_data = {}
        # For each item list, extract the data
        for list_id, info in self.result_dict.items():
            parent_path, columns = info
            # Extract the data for the current list
            all_lists_data[list_id] = self.extract_list_data(
                parent_path, columns)
        return all_lists_data

# Step 1 - Extract the template data


class XMLTemplateParser:
    def __init__(self, xml_tree, namespaces):
        self.xml_tree = xml_tree
        self.namespaces = namespaces

    def parse_template(self):
        template_data = {}

        def traverse(node, path='', isParentList=False, parentListID=""):
            # Skip nodes that are not Element (e.g., comments or processing instructions)
            if not isinstance(node.tag, str):
                return

            # Handling namespace and local name
            ns_uri = None
            node_tag = node.tag
            if node.tag.startswith('{'):
                ns_uri, node_tag = node.tag[1:].split("}", 1)
                namespace_prefix = None
                for prefix, uri in self.namespaces.items():
                    if uri == ns_uri:
                        namespace_prefix = prefix
                        break
                current_path = f"{path}/{namespace_prefix}:{node_tag}" if namespace_prefix else f"{path}/{node_tag}"
            else:
                current_path = f"{path}/{node_tag}"

            node_list_id = node.attrib.get("itemList", "")
            node_is_list = node_list_id != ""

            if node_is_list and isParentList:
                print(
                    "Template incorrectly configured. You cannot have nested lists in template configuration!")
                raise Exception(
                    "Template incorrectly configured. You cannot have nested lists in template configuration!")

            for attr_name, attr_value in node.attrib.items():
                if attr_name == "itemList":
                    continue

                # Handling attributes with potential namespaces
                attr_ns_uri = None
                attr_localname = attr_name
                if attr_name[0] == "{":
                    attr_ns_uri, attr_localname = attr_name[1:].split("}", 1)
                    attr_namespace_prefix = None
                    for prefix, uri in self.namespaces.items():
                        if uri == attr_ns_uri:
                            attr_namespace_prefix = prefix
                            break
                    full_attr_name = f"{attr_namespace_prefix}:{attr_localname}" if attr_namespace_prefix else attr_localname
                else:
                    full_attr_name = attr_localname

                if node_is_list:
                    template_data[f"{current_path}@{full_attr_name}"] = (
                        attr_value, node_list_id)
                elif isParentList:
                    template_data[f"{current_path}@{full_attr_name}"] = (
                        attr_value, parentListID)
                else:
                    template_data[f"{current_path}@{full_attr_name}"] = (
                        attr_value, "")

            if node.text and node.text.strip():
                if node_is_list:
                    template_data[current_path] = (
                        node.text.strip(), node_list_id)
                elif isParentList:
                    template_data[current_path] = (
                        node.text.strip(), parentListID)
                else:
                    template_data[current_path] = (node.text.strip(), "")

            for child in node:
                if node_is_list:
                    traverse(child, current_path, True, node_list_id)
                elif isParentList:
                    traverse(child, current_path, True, parentListID)
                else:
                    traverse(child, current_path, False, "")

        traverse(self.xml_tree.getroot())
        return template_data

# Step 2 - Extract the data from the XML file with form fields values


class XMLDataProcessorFormFields:
    def __init__(self, data_xml_tree, template_keys, namespaces):
        """
        Initialize the XMLDataProcessorFormFields object.
        :param data_xml_tree: The XML tree containing the data.
        :param template_keys: A dictionary containing the template keys and their corresponding paths in the XML tree.
        The keys in the dictionary are the paths in the XML tree, and the values are tuples containing the key name and an empty string.
        The first element of the tuple is the form filed guid from WebCon that will be used in the body for the API request.
        The second element of the tuple is empty string and does not have any use for now.
        :param namespaces: A dictionary containing the namespace prefixes and their corresponding URIs.
        """
        self.data_xml_tree = data_xml_tree
        self.template_keys = template_keys
        self.namespaces = namespaces

    def apply_template(self):
        """
        Extract data from the XML tree based on the template keys.
        :return: A dictionary containing the extracted data.
        """
        # Initialize an empty dictionary to store the extracted data
        # The keys are the form field guids from WebCon, and the values are the extracted data
        # This dictionary will be used to construct the body for the API request with the form fields values
        extracted_data = {}
        # For each path in the template keys, extract the data from the XML tree
        for path, (key, _) in self.template_keys.items():
            # If the path contains an '@', then it is an attribute
            if "@" in path:
                # Split the path and attribute name by the '@' character which separates the path from the attribute name
                element_path, attribute_name = path.rsplit('@', 1)
                # Find the node in the XML tree based on the element_path
                node = find_nodes_by_path(
                    self.data_xml_tree, element_path, self.namespaces)
                # If the node list is not empty, then extract the attribute value
                if len(node) > 0:
                    node = node[0]
                else:
                    node = None
                # Extract the attribute value
                if node is not None:
                    # Access the attribute directly
                    attr_value = node.get(attribute_name)
                    if attr_value:
                        # Store the attribute value in the extracted data dictionary
                        extracted_data[key] = attr_value
            else:
                # Adjusted for ET: find the first node that matches the path
                node = find_nodes_by_path(
                    self.data_xml_tree, path, self.namespaces)
                # Same as before, extract the text value only if the node list is not empty
                if len(node) > 0:
                    node = node[0]
                else:
                    node = None
                # Extract the text value
                if node is not None:
                    # Access the text directly
                    # The strip() method is used to remove leading and trailing whitespaces
                    value = node.text.strip() if node.text else None
                    # Store the text value in the extracted data dictionary
                    extracted_data[key] = value

        return extracted_data

# Main Class for XML Processing


class XMLProcessor:
    def __init__(self, template_xml_path, xml_string_file_data=None, namespaces=None):
        self.template_xml_path = template_xml_path
        self.xml_string_file_data = xml_string_file_data  # optional for template-only mode
        self.namespaces = namespaces or {}

    def _parse_template(self):
        tree = ET.parse(self.template_xml_path)
        parser = XMLTemplateParser(tree, self.namespaces)
        return parser.parse_template()  # path -> (field_guid, list_id)

    @staticmethod
    def _split_template(template_map):
        # Separate into scalars and list-bound entries
        scalars = dict(template_map)  # will delete list-bound entries in-place
        removed = {}  # list_id -> [(full_path, field_guid), ...]
        for path, (guid, list_id) in list(template_map.items()):
            if list_id != "":
                removed.setdefault(list_id, []).append((path, guid))
                if path in scalars:
                    del scalars[path]
        # Build item_lists_dict: list_id -> (base_path, [(rel_path, guid), ...])
        item_lists_dict = {}
        for list_id, pairs in removed.items():
            paths = [p for p, _ in pairs]
            common_prefix = os.path.commonprefix(paths)
            common_base_path = common_prefix.rsplit('/', 1)[0] if '/' in common_prefix else common_prefix
            rel_cols = [(p.replace(common_base_path, '', 1), guid) for p, guid in pairs]
            item_lists_dict[list_id] = (common_base_path, rel_cols)
        return scalars, item_lists_dict, removed

    def compile_template(self, keep_original=False):
        """
        Template-only mode: returns (template_form_fields_data, item_lists_dict)
        Optionally also returns original template map when keep_original=True.
        """
        template_map = self._parse_template()
        scalars, item_lists_dict, _ = self._split_template(template_map)
        if keep_original:
            return scalars, item_lists_dict, template_map
        return scalars, item_lists_dict, None

    def process_xml(self):
        """
        Full mode (backward compatible): extract scalar fields and lists from the data XML.
        """
        if self.xml_string_file_data is None:
            raise ValueError("xml_string_file_data is required for full processing mode")
        # Compile template to get scalar paths and list configuration
        template_form_fields_data, item_lists_dict, _ = self.compile_template()
        # Parse data XML string into a root Element
        data_root = ET.fromstring(self.xml_string_file_data)
        # Scalars
        data_processor = XMLDataProcessorFormFields(
            data_root, template_form_fields_data, self.namespaces
        )
        form_fields_data = data_processor.apply_template()
        # Lists
        extractor = XMLDataExtractorItemLists(
            data_root, item_lists_dict, self.namespaces
        )
        all_lists_data = extractor.extract_all_lists()
        return all_lists_data, form_fields_data



def update_xml_namespaces(xml_string, namespaces_dict=None):
    """
    Update namespaces in the root element of an XML string based on the type of document (Invoice or CreditNote).

    Args:
        xml_string (str): The original XML string.
        namespaces_dict (dict): A dictionary containing namespace dictionaries for 'Invoice' and 'CreditNote'.

    Returns:
        str: Updated XML string with namespaces adjusted based on the document type.
    """

    full_namespaces_dict = {
        'Invoice': {
            'xmlns': "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
            'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
            'xmlns:qdt': "urn:oasis:names:specification:ubl:schema:xsd:QualifiedDataTypes-2",
            'xmlns:udt': "urn:oasis:names:specification:ubl:schema:xsd:UnqualifiedDataTypes-2",
            'xmlns:cac': "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            'xmlns:cbc': "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            'xmlns:cec': "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
            'xmlns:ccts': "urn:un:unece:uncefact:documentation:2",
        },
        'CreditNote': {
            'xmlns': "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2",
            'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
            'xmlns:qdt': "urn:oasis:names:specification:ubl:schema:xsd:QualifiedDataTypes-2",
            'xmlns:udt': "urn:oasis:names:specification:ubl:schema:xsd:UnqualifiedDataTypes-2",
            'xmlns:cac': "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            'xmlns:cbc': "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            'xmlns:cec': "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
            'xmlns:ccts': "urn:un:unece:uncefact:documentation:2",
        }
    }
    if namespaces_dict is None:
        namespaces_dict = full_namespaces_dict

    # Parse the original XML string into an Element
    root = ET.fromstring(xml_string)

    # Determine the document type from the root tag
    document_type = root.tag
    if '}' in document_type:
        document_type = document_type.split('}', 1)[1]

    # Get the full namespace dictionary for the document type
    namespaces_dict = full_namespaces_dict[document_type]

    start_tag = f'<{document_type}'
    end_tag = '>'

    # Find the start and end of the root element's opening tag
    start_pos = xml_string.find(start_tag)
    if start_pos == -1:
        start_tag = f'<ubl:{document_type}'
        start_pos = xml_string.find(start_tag)
        if start_pos == -1:
            print(f"Document type tag not found in XML string: {document_type}")
            raise ValueError("Document type tag not found in XML string.")

    end_pos = xml_string.find(end_tag, start_pos)
    if end_pos == -1:
        print(f"Closing '>' of the root tag not found.")
        raise ValueError("Closing '>' of the root tag not found.")

    # Extract the whole root tag
    root_tag_full = xml_string[start_pos:end_pos + 1]
    
    updated_root = update_namespaces_from_node(root_tag_full, namespaces_dict)
    new_xml = xml_string.replace(root_tag_full, updated_root)

    # Check if the final string contains special invisible characters and remove them like &#xD;
    new_xml = new_xml.replace('&#xD;', '')

    return new_xml


def update_namespaces_from_node(node_string, namespace_replacements):
    """
    Extracts and optionally updates namespaces from the provided XML node string.

    Args:
        node_string (str): The XML node string containing namespace declarations.
        namespace_replacements (dict): Dictionary of namespaces with potential replacements.

    Returns:
        str: XML node string with updated namespaces.
    """
    # Regex to find any attribute that follows the pattern [name]="[URI]"
    namespace_pattern = re.compile(
        r'(\s(?P<attribute>[a-zA-Z0-9_:]+)="(?P<uri>[^"]+)")')
    
    # A list with all the attributes that match the pattern
    found_attributes = []

    # Function to replace namespaces in the match with those from the dictionary
    def replace_namespace(match):
        attribute = match.group('attribute')  # Attribute name (e.g., xmlns, xsi:schemaLocation)
        # Add the attribute to the list of found attributes
        found_attributes.append(attribute)
        uri = match.group('uri')
        # Check if the attribute is in the replacements dictionary and replace URI if present
        if attribute in namespace_replacements:
            return f' {attribute}="{namespace_replacements[attribute]}"'
        else:
            # Handle the specific case for URIs containing "../../"
            if '../../' in uri:
                # Remove spaces and split the URI, then take the first part before "../../"
                uri = uri.split("../../")[0].strip()
            return f' {attribute}="{uri}"'

    # Replace found namespaces in the node string with potential replacements from the dictionary
    updated_node_string = namespace_pattern.sub(replace_namespace, node_string)

    # Check if there are any missing attributes from the dictionary and add them
    for attribute, uri in namespace_replacements.items():
        if attribute not in found_attributes:
            # Add the missing attribute to the end of the node string with newline and indentation
            updated_node_string = updated_node_string.rstrip('>') + f'\n            {attribute}="{uri}">'

    return updated_node_string