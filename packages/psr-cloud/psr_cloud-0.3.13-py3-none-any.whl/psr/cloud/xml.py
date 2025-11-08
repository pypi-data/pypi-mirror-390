# PSR Cloud. Copyright (C) PSR, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from typing import Any, Dict
from xml.etree import ElementTree as ET


def create_case_xml(parameters: Dict[str, Any]) -> str:
    root = ET.Element("ColecaoParametro")
    for name, value in parameters.items():
        if value is None:
            continue
        parameter = ET.SubElement(root, "Parametro", nome=name, tipo="System.String")
        parameter.text = str(value)
    ET.indent(root, "  ")
    return ET.tostring(root, encoding="unicode", method="xml")


def create_desktop_xml(parameters: Dict[str, Any]) -> str:
    node = ET.Element("Repositorio")
    case_node = ET.SubElement(node, "CasoOperacao")
    for key, value in parameters.items():
        if value is None:
            continue
        case_node.set(key, str(value))
    ET.indent(node, "  ")
    return ET.tostring(node, encoding="unicode", method="xml", xml_declaration=False)
