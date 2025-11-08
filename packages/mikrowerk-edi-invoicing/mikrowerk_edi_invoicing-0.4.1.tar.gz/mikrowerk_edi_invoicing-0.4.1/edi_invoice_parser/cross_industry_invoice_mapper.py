"""
This implements a mapper from a drafthorse parsed x-rechnung-xml to the internal XRechnung object
"""
from lxml import etree

from .model.x_rechnung import XRechnung
from .cii_dom_parser import XRechnungCIIXMLParser
from .ubl_sax_parser.xml_ubl_sax_parser import XRechnungUblXMLParser


def parse_and_map_x_rechnung(_xml: bytes) -> XRechnung:
    """

    Args:
        _xml: bytes with xml file

    Returns: XRechnung

    """
    _parser = None
    tree = etree.fromstring(_xml)
    if tree.tag == '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}CrossIndustryInvoice':
        _parser = XRechnungCIIXMLParser()
    elif tree.tag == '{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice':
        _parser = XRechnungUblXMLParser()
    if _parser is None:
        raise ValueError(f'xml format not supported: "{tree.tag}"')
    return _parser.parse_and_map_x_rechnung(_xml)
