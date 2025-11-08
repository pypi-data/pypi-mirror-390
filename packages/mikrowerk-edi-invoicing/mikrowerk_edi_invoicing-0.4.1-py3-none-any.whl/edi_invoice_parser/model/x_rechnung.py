from datetime import datetime
from dataclasses import dataclass, asdict
from decimal import Decimal

__all__ = ['XRechnung', "XRechnungCurrency", "XRechnungTradeParty", "XRechnungTradeAddress", "XRechnungTradeContact",
           "XRechnungPaymentMeans", "XRechnungBankAccount", "XRechnungAppliedTradeTax", "XRechnungTradeLine",
           "XRechnungFinancialCard"]


@dataclass
class XRechnungCurrency:
    amount: Decimal
    currency_code: str

    @staticmethod
    def from_currency_tuple(currency_tuple: tuple) -> 'XRechnungCurrency':
        return XRechnungCurrency(*currency_tuple)


@dataclass
class XRechnungTradeAddress:
    post_code: str = None  # 'Post-Code'
    city_name: str = None  # 'City'
    country_id: str = None  # 'Country ID
    country_subdivision_id: str = None  # 'Country Subdivision ID'
    address_line_1: str = None  # 'Address Line 1'
    address_line_2: str = None  # 'Address Line 2'
    address_line_3: str = None  # 'Address Line 3'


@dataclass
class XRechnungTradeContact:
    name: str = None  # 'Person Name'
    department_name: str = None  # 'Department Name'
    telephone: str = None  # 'Telephone Number'
    fax: str = None  # 'Fax'
    email: str = None  # 'Email'


@dataclass
class XRechnungTradeParty:
    global_id: int = 0  # 'Global ID'
    global_id_schema: str = None  # 'Global Schema'
    id: str = None  # 'id'
    name: str = None  # 'Name'
    description: str = None  # 'Description'
    postal_address: XRechnungTradeAddress = None
    email: str = None  # 'Email'
    trade_contact: XRechnungTradeContact = None
    vat_registration_number: str = None  # 'VAT Registration Number'
    fiscal_registration_number: str = None  # 'Fiscal Registration Number'
    legal_registration_number: str = None


# @dataclass
# class XRechnungSpecifiedTradeSettlementPaymentMeans:
#     name: str = None  # 'Name'
#     type_code: str = None  # 'Type Code'
#     information: str = None  # 'Information'
#     iban: str = None  # 'IBAN'
#     bicid: str = None  # 'BICID'
#     account_name: str = None  # 'Account Name'


@dataclass
class XRechnungAppliedTradeTax:
    name: str = None  # 'Name'
    type_code: str = None
    category_code: str = None
    applicable_percent: float = 0.0
    basis_amount: float = 0.0  # 'Basis Amount'
    calculated_amount: float = 0.0  # 'Calculated Tax Amount'


@dataclass
class XRechnungTradeLine:
    name: str = None  # 'Name')
    description: str = None
    line_id: str = None  # 'Line ID')
    global_product_id: str = None  # 'Global Product ID')
    global_product_scheme_id: str = None  # 'Global Product Scheme ID')
    seller_assigned_id: str = None  # 'Seller Assigned ID')
    buyer_assigned_id: str = None  # 'Buyer Assigned ID')
    price_unit: float = 0.0  # 'Net Price')
    quantity_billed: float = 0.0  # 'Billed Quantity')
    quantity_unit_code: str = None  # 'Quantity Code')
    total_amount_net: float = 0.0  # 'Total Amount Net')
    price_unit_gross: float = 0.0
    total_allowance_charge: float = 0.0
    trade_tax: any = None
    note: str = None
    lot_number_id: str = None
    expiry_date: datetime = None


@dataclass
class XRechnungFinancialCard:
    id: str | None = None
    cardholder_name: str | None = None


@dataclass
class XRechnungBankAccount:
    iban: str | None = None
    bic: str | None = None


@dataclass
class XRechnungPaymentMeans:
    id: str = None
    type_code: str = None
    information: str = None
    financial_card: XRechnungFinancialCard = None
    payee_account: XRechnungBankAccount = None


@dataclass
class XRechnung:
    """
    Model an EDI invoice for mapping CII or UBL Invoices
    """
    name: str = None  # 'Name'
    doc_id: str = None  # 'Document ID'
    doc_type_code: str = None  # 'Subject Code'
    issued_date_time: datetime = None  # 'Date'
    delivered_date_time: datetime = None  # 'Delivered Date'
    languages: str = None  # 'Languages'
    notes: str = None  # 'Notes'
    buyer_reference: str = None  # 'Buyer Reference'
    order_reference: str = None
    dispatch_reference: str = None
    sales_order_reference: str = None
    seller: XRechnungTradeParty = None
    payee: XRechnungTradeParty = None
    buyer: XRechnungTradeParty = None
    invoicee: XRechnungTradeParty = None
    currency_code: str = None  # 'Currency Code'
    payment_means: XRechnungPaymentMeans = None
    payment_terms: str = None  # 'Payment Terms'
    line_total_amount: Decimal = None  # 'Line Total Amount'
    charge_total_amount: Decimal = None  # 'Charge Total Amount'
    allowance_total_amount: Decimal = None  # 'Allowance Total Amount'
    tax_basis_total_amount: XRechnungCurrency = None
    tax_total_amount: [XRechnungCurrency] = None  # 'Tax Grand Total Amount'
    grand_total_amount: XRechnungCurrency = None  # 'Grand Total Amount'
    total_prepaid_amount: Decimal = None  # 'Total Prepaid Amount'
    due_payable_amount: Decimal = None  # 'Due Payable Amount'
    trade_line_items: [XRechnungTradeLine] = None
    applicable_trade_taxes: [XRechnungAppliedTradeTax] = None

    def map_to_dict(self) -> dict:
        """
        maps a XRechnung to a dict suited for generation odoo entities
        Note: this is not a 1:1 mapping of the XRechnung model, some adjustments and simplifications made
        :param self: XRechnung.XRechnung
        :return: dict
        """

        _dict = asdict(self)
        _dict.update({
            'line_total_amount': float(self.line_total_amount) if self.line_total_amount is not None else 0,
            'charge_total_amount': float(self.charge_total_amount) if self.charge_total_amount else 0,
            'allowance_total_amount': float(self.allowance_total_amount) if self.allowance_total_amount else 0,
            'tax_basis_total_amount': float(
                self.tax_basis_total_amount.amount) if self.tax_basis_total_amount else 0,
            'tax_total_amount': self.sum_x_rechnung_currency(self.tax_total_amount) if self.tax_total_amount else 0,
            'grand_total_amount': float(self.grand_total_amount.amount) if self.grand_total_amount else 0,
            'total_prepaid_amount': float(self.total_prepaid_amount) if self.total_prepaid_amount else 0.0,
            'due_payable_amount': float(self.due_payable_amount) if self.due_payable_amount else 0.0,
            'seller': self.map_trade_party(self.seller) if self.seller else None,
            'payee': self.map_trade_party(self.payee) if self.payee else None,
            'buyer': self.map_trade_party(self.buyer) if self.buyer else None,
            'invoicee': self.map_trade_party(self.invoicee) if self.invoicee else None,
            'payment_means': self.map_payment_means(self.payment_means) if self.payment_means else None,
            'trade_line_items': self.map_tradeline_items_to_dict(self.trade_line_items),
            'applicable_trade_taxes': self.map_trade_taxes_to_dict(self.applicable_trade_taxes),
        })
        return _dict

    @classmethod
    def map_tradeline_to_dict(cls, x_trade_line: XRechnungTradeLine) -> dict:
        _dict = asdict(x_trade_line)
        _dict.update(
            {'trade_tax': asdict(x_trade_line.trade_tax) if x_trade_line.trade_tax is not None else None,
             'price_unit': float(x_trade_line.price_unit),
             'quantity_billed': float(x_trade_line.quantity_billed),
             'total_amount_net': float(x_trade_line.total_amount_net),
             })
        return _dict

    @classmethod
    def map_tradeline_items_to_dict(cls, tradeline_items: list) -> list:
        res = []
        if tradeline_items:
            for tradeline_item in tradeline_items:
                res.append(cls.map_tradeline_to_dict(tradeline_item))
        return res

    @classmethod
    def map_trade_taxes_to_dict(cls, trade_taxes: list) -> list:
        res = []
        if trade_taxes:
            for tax in trade_taxes:
                res.append(asdict(tax))
        return res

    @classmethod
    def map_trade_party(cls, trade_party: XRechnungTradeParty) -> dict:
        _dict = asdict(trade_party)
        _dict.update({
            'postal_address': cls.map_trade_address(trade_party.postal_address),
            'trade_contact': cls.map_trade_contact(trade_party.trade_contact, trade_party)
        })
        return _dict

    @classmethod
    def map_trade_address(cls, trade_address: XRechnungTradeAddress) -> dict | None:
        if trade_address is None:
            return None
        _dict = asdict(trade_address)
        return _dict

    @classmethod
    def map_trade_contact(cls, trade_contact: XRechnungTradeContact, trade_party: XRechnungTradeParty) -> dict | None:
        if trade_contact is None:
            return None
        _dict = asdict(trade_contact)
        if _dict.get('name', None) is None or _dict.get('name', None) == '':
            _dict.update({'name': trade_party.name})
        return _dict

    @classmethod
    def map_payment_means(cls, payment_means: XRechnungPaymentMeans) -> dict:
        _dict = {
            'type_code': payment_means.type_code,
            'information': payment_means.information,
            'financial_card': cls.map_financial_card(
                payment_means.financial_card) if payment_means.financial_card else None,
            'bank_account': cls.map_bank_account(payment_means.payee_account) if payment_means.payee_account else None,
        }
        return _dict

    @classmethod
    def map_financial_card(cls, card: XRechnungFinancialCard) -> dict:
        _dict = {
            'card_number': card.id,
            'card_holder_name': card.cardholder_name
        }
        return _dict

    @classmethod
    def map_bank_account(cls, bank: XRechnungBankAccount) -> dict:
        _dict = {
            'iban': bank.iban,
            'bic': bank.bic
        }
        return _dict

    @classmethod
    def sum_x_rechnung_currency(cls, x_currencies: [XRechnungCurrency]) -> float:
        res = 0.0
        if x_currencies:
            for x_currency in x_currencies:
                res += float(x_currency.amount)
        return res
