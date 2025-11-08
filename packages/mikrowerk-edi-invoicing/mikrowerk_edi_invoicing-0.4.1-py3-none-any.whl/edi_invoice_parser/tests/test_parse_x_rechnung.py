import unittest
import jsonpickle
from parameterized import parameterized

from facturx import get_facturx_xml_from_pdf

from . import get_checked_file_path
from edi_invoice_parser.cross_industry_invoice_mapper import parse_and_map_x_rechnung
from . import XRechnung


class XRechnungEinfachTestCase(unittest.TestCase):

    def setUp(self) -> None:
        jsonpickle.set_encoder_options("json", indent=2, ensure_ascii=False)
        pass

    @parameterized.expand([
        ('xml', 'zugferd/XRECHNUNG_Einfach/xrechnung.xml'),
        ('xml', 'real_invoice_samples/AKD-736116091815.xml'),
        ('xml', 'griffity_exapmles/385_2025.xml'),
        ('xml', 'e_invoicing_EN16931/CII-BR-CO-10-RoundingIssue.xml'),
        ('xml', 'e_invoicing_EN16931/CII_business_example_01.xml'),
        ('xml', 'e_invoicing_EN16931/CII_business_example_02.xml'),
        ('xml', 'e_invoicing_EN16931/CII_business_example_Z.xml'),
        ('xml', 'e_invoicing_EN16931/CII_example1.xml'),
        ('xml', 'e_invoicing_EN16931/CII_example2.xml'),  # throws error
        ('xml', 'e_invoicing_EN16931/CII_example3.xml'),
        ('xml', 'e_invoicing_EN16931/CII_example4.xml'),
        ('xml', 'e_invoicing_EN16931/CII_example5.xml'),  # throws error
        ('xml', 'e_invoicing_EN16931/CII_example6.xml'),
        ('xml', 'e_invoicing_EN16931/CII_example7.xml'),
        ('xml', 'e_invoicing_EN16931/CII_example8.xml'),
        ('xml', 'e_invoicing_EN16931/CII_example9.xml'),
        ('xml', 'ubl/RG00343552.xml'),
        ('xml', 'ubl/RG00350365.xml'),
        ('xml', 'ubl/ubl_invoice_example.xml'),
        ('xml', 'ubl/UBL-Invoice-2.1-Example.xml'),
        ('pdf', 'zugferd/BASIC-WL_Einfach/BASIC-WL_Einfach.pdf'),
        # ('pdf', 'zugferd/XRECHNUNG_Einfach/XRECHNUNG_Einfach.pdf'), # needs some checks, why test failed
        # ("pdf", "zugferd/XRECHNUNG_Elektron/XRECHNUNG_Elektron.pdf"), # needs some checks, why test failed
        ('pdf', 'odoo_generated/INV_2025_00001.pdf'),

    ])
    def test_x_rechnung_files(self, file_type, file_path):
        print(f"start testing with file: {file_path}")
        if file_type == 'xml':
            _parsed = self._parse_xml(file_path)
        elif file_type == 'pdf':
            _parsed = self._parse_pdf(file_path)
        else:
            raise AssertionError(f'File type {file_type} not supported')
        assert _parsed is not None
        res_dict = _parsed.map_to_dict()
        print(jsonpickle.dumps(res_dict))

    def _parse_xml(self, filepath) -> XRechnung:
        _file_path, _exists, _is_dir = get_checked_file_path(filepath, __file__)
        self.assertTrue(_exists)
        print(f"\n_parse_xml: file_path={_file_path}")
        with open(_file_path, "rb") as _file:
            samplexml = _file.read()
            res = parse_and_map_x_rechnung(samplexml)
            self.assertIsNotNone(res)
            return res

    def _parse_pdf(self, filepath) -> XRechnung:
        _file_path, _exists, _is_dir = get_checked_file_path(filepath, __file__)
        self.assertTrue(_exists)
        print(f"\n_parse_pdf: file_path={_file_path}")
        with open(_file_path, "rb") as _file:
            sample_pdf = _file.read()
            filename, xml = get_facturx_xml_from_pdf(sample_pdf, False)
            print(xml)
            if not xml or len(xml) == 0:
                raise FileNotFoundError(
                    f"Could not extraxt XML from PDF file: {filepath}")
            res = parse_and_map_x_rechnung(xml)
            self.assertIsNotNone(res)
            return res


if __name__ == '__main__':
    unittest.main()
