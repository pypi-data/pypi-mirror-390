import unittest
import os
import pathlib
from parameterized import parameterized
import json

from . import get_checked_file_path
from edi_invoice_parser.parse_plain_pdf_file import analyze_document


class TestPlainPdfInvoiceParser(unittest.TestCase):
    @parameterized.expand([
        ('pdf', 'plain_pdf_invoices/25313 - Rechnung Konzepthausevent - 16-09-2025.pdf'),
        ('pdf', 'plain_pdf_invoices/57856 - 2509-7377.pdf'),
        ('pdf', 'plain_pdf_invoices/Bestätigung griffty GmbH VA 150919 SCCON_25.pdf'),
        # ('pdf', 'plain_pdf_invoices/Invoice INV-1013.pdf'),
        # ('pdf', 'plain_pdf_invoices/LGM-2509-784_Griffity_GmbH_10_09_2025_Rechnung.pdf'),
        # ('pdf', 'plain_pdf_invoices/Order GO-0741243.pdf'),
        # ('pdf', 'plain_pdf_invoices/Rechnung 30250628.pdf'),
        # ('pdf', 'plain_pdf_invoices/Rechnung-202511899-11267.pdf'),
        # ('pdf', 'plain_pdf_invoices/TS Rechnung TS2025-10586.pdf'),
        # ('pdf', 'plain_pdf_invoices/Verkaufsrechnung 01-137334.pdf'),
    ])
    def test_parse_pdf_invoice(self, file_type, file_path):
        _file_path, _exists, _is_dir = get_checked_file_path(file_path, __file__)
        self.assertEqual(file_type, 'pdf', "Only 'pdf' filetype is supported")
        self.assertTrue(_exists, f"file does not exist: {_file_path}")
        self.test_api_key_is_available()
        api_key = os.environ.get("GEMINI_API_KEY")

        filepath = pathlib.Path(_file_path)
        binary = filepath.read_bytes()
        invoice_data = analyze_document(binary, api_key=api_key)
        self.assertIsNotNone(invoice_data, "No result retrieved")
        print("\n------------------------------------------------------------")
        print(f"\nDokument Date: {file_path}")
        print("\n--- Extrahierte Dokumentdaten ---")
        # Beispielhafter Zugriff auf einzelne Daten
        print(f"\nDokumenttyp: {invoice_data.get('dokumenttyp', None)}")
        print(f"\ndokumentnummer: {invoice_data.get('dokumentnummer', None)}")
        print(f"\nAbsender: {invoice_data.get('absender', {}).get('name', None)}")
        print(f"\nEmpfänger: {invoice_data.get('empfänger', {}).get('name', None)}")
        print(f"Fälligkeitsdatum: {invoice_data.get('fälligkeitsdatum', None)}")
        print(f"Gesamtbetrag: {invoice_data.get('summen', {}).get('rechnungsbetrag', 'None')} €")
        print("\n------------------------------------------------------------")
        # Gib das Dictionary als formatierten JSON-String aus
        print(json.dumps(invoice_data, indent=2, ensure_ascii=False))

        _out_file_path = _file_path.replace('.pdf', '.json')
        with open(_out_file_path, "w") as f:
            f.write(json.dumps(invoice_data, indent=2, ensure_ascii=False))
            print(f"written result json to {_out_file_path}")
        print("\n---------------------------------")

    def test_api_key_is_available(self):
        """
        Prüft, ob die Umgebungsvariable 'PROD_API_KEY' gesetzt ist.

        WICHTIG: Gib niemals den Inhalt des Keys in Logs aus!
        Prüfe nur, ob er existiert oder valide aussieht (z.B. Länge).
        """

        # Hier liest Python die Umgebungsvariable
        api_key = os.environ.get("GEMINI_API_KEY")

        assert api_key is not None, "Die Umgebungsvariable 'GEMINI_API_KEY' wurde nicht gefunden."
        assert len(api_key) > 20, "Der API Key scheint ungültig oder zu kurz zu sein."


if __name__ == '__main__':
    unittest.main()
