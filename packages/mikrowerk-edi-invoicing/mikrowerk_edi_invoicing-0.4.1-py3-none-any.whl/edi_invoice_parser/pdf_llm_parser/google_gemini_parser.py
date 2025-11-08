import json
import logging
import os

from google import genai
from google.genai import types

DEFAULT_LLM_MODEL = "gemini-2.5-flash-lite"

_logger = logging.getLogger(__name__)

DEFAULT_PROMPT = """
    Bitte analysiere das beigefügte Dokument und extrahiere alle relevanten Informationen als strukturiertes JSON.
    Verwende exakt das folgende JSON-Schema und beachte die Anweisungen.

    Wichtige Hinweise:
    - Gib NUR valides JSON zurück. Kein umgebender Text oder Markdown-Formatierung.
    - Bei fehlenden Werten verwende den JSON-Wert null.
    - Gib alle Beträge als Zahlen (float oder integer), nicht als Strings.
    - Formatiere alle Datumsangaben im Format YYYY-MM-DD.
    - Gib das land als "ISO 3166-2" Code an, wenn nicht angegeben nehme "DE" an.
    - Erkenne den Dokumententyp und klassifiziere ihn als: "Rechnung", "Gutschrift", "Auftrag", "Angebot", "Anfrage", "Auftragsbestätigung", "Bestellung"
    - Erkenne für eine Gutschrift auch Varianten wie Credit Note, Rechnungsgutschrift, Erstattung
    - Erkenne für eine Rechnung auch Varianten wie: "Rechnung","Proforma Rechnung","R-Nr.","Rechnung-Nr.","Rech.-Nr.","Invoice No.","Invoice Number","Kostenrechnung"
    - Erkenne für eine Auftragsbestätigung auch Varianten wie: "Bestätigung", "Vertrag","Order Acknowledgement", "Order Confirmation"
    - Erkenne für die Referenz auch Varianten wie: "Projektnummer", "Auftragsnummer", "Bestellnummer", "Referenznummer", "Kundenreferenz", "Reference"
    - Ist der Dokumententyp nicht erkennbar klassifiziere ihn als: "sonstiges"
    - Sind keine Positionen vorhanden erstelle eine zusammenfassung des Textes und die Summen oder Beträge, falls vorhanden
    - Ist der Dokumententyp ist nicht erkennbar erstelle eine Zusammenfassung des Textes
    - Erkenne auch Varianten wie: "MWST.", "VAT", "Ust.", etc. für die Umsatzsteuer.
    - Erkenne für die Währung Varianten wie: "EUR", "€", "$", "USD", "CHF" oder sonstige Währungsbezeichnung oder Symbol
    - Wenn keine Währung abgeben ist nimm "EUR" an
    - Erkenne für das fälligkeitsdatum auch Varianten wie:  "zahlbar bis", "fällig", "fällig bis", "zu liefern bis", "gültig bis"
    - Erkenne ob eine Rechnung bereits bezahlt ist, ja oder nein, und vermerke die Zahlungsmethode wie: "Paypal", "Kreditkarte", "Überweisung", "Barzahlung"
    - Eine Rechnung ist bezahlt "ja", wenn die Zahlungsmethode wie: "Paypal", "Kreditkarte" ist.
    - Ernenne für die Steuernummer des Absenders auch: "Tax Number", "VAT Number", "VAT ID", "MWST ID", "UST ID", "Ust-id"

    JSON-Schema:
    {
      "dokumenttyp": "string",
      "dokumentnummer": "string",
      "referenz": "string",
      "dokumentendatum": "YYYY-MM-DD",
      "fälligkeitsdatum": "YYYY-MM-DD",
      "absender": {
        "name": "string",
        "adresse": "string",
        "plz": "string",
        "ort": "string",
        "land": "string",
        "steuernummer": "string",
      },
      "empfänger": {
        "name": "string",
        "adresse": "string",
        "plz": "string",
        "ort": "string",
        "land": "string",
      },
      "positionen": [
        {
          "POS": "number",
          "Bezeichnung": "string",
          "Menge": "number",
          "Einheit": "string",
          "einzelpreis": "number",
          "Betrag": "number",
          "mwst_satz": "number"
        }
      ],
      "summen": {
        "nettobetrag": "number",
        "umsatzsteuer": "number",
        "rechnungsbetrag": "number"
        "währung": "string"
      },
      "zahlungshinweise": "string",
      "zahlungsmethode": "string"
      "bezahlt": "string",
      "weitere_info": "string",
      "bankverbindung": "string"
      "zusammenfassung": "string",
    }
    """


def analyze_document(pdf_binary: bytes, api_key, model: str, prompt) -> dict:
    """
    Analysiert eine PDF-Rechnung mit Gemini, extrahiert Informationen
    und gibt sie als Python-Dictionary zurück.
    """

    if not pdf_binary:
        _logger.error("Error no binaries supplied")
        raise ValueError("Error no binaries supplied")

    if api_key:
        if len(api_key) < 20:
            raise RuntimeError("Der API Key scheint ungültig oder zu kurz zu sein.")
    else:
        api_key = os.environ.get("GEMINI_API_KEY", None)
        if api_key is None:
            raise RuntimeError("Die Umgebungsvariable 'GEMINI_API_KEY' wurde nicht gefunden.")
        if len(api_key) < 20:
            raise RuntimeError("Der API Key scheint ungültig oder zu kurz zu sein.")

    api_key = api_key.strip()
    client = genai.Client(api_key=api_key)
    if not model:
        model = DEFAULT_LLM_MODEL
    if not prompt:
        prompt = DEFAULT_PROMPT

    _logger.info("\nSende Anfrage an die Gemini API...")
    # Sende die Anfrage mit dem Prompt und der hochgeladenen Datei
    _logger.info(f"use API-KEY: {api_key} length: {len(api_key)}")
    try:
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_bytes(
                    data=pdf_binary,
                    mime_type='application/pdf',
                ),
                prompt])
    except KeyError:
        raise UserWarning("Fehler: Die Umgebungsvariable GOOGLE_API_KEY wurde nicht gefunden.\n"
                          "Bitte setzen Sie den Schlüssel, z.B. mit 'export GOOGLE_API_KEY=\"DEIN_API_SCHLÜSSEL\"'")

    except Exception as e:
        raise UserWarning(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

    # Bereinige und parse die Antwort
    try:
        # Manchmal gibt das Modell die Antwort in einem Markdown-Codeblock zurück.
        # Dieser Code entfernt die Markierungen, um reines JSON zu erhalten.
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()

        # Parse den JSON-String in ein Python-Dictionary
        extracted_data = json.loads(cleaned_response)
        return extracted_data
    except json.JSONDecodeError:
        raise RuntimeError("Fehler beim Parsen der Modell-Antwort:", response.text)
    except Exception as e:
        raise RuntimeError(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
