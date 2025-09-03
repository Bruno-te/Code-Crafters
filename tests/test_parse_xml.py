"""
Unit tests for XML parsing module
"""
import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from etl.parse_xml import MoMoXMLParser, parse_momo_xml

class TestMoMoXMLParser(unittest.TestCase):
    """Test cases for MoMoXMLParser class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.xml_path = Path(self.temp_dir) / "test_momo.xml"
        
        # Sample XML content
        self.sample_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<momo_transactions>
    <transaction>
        <id>TXN001</id>
        <date>2024-01-15 14:30:00</date>
        <amount>1500.00</amount>
        <phone>+233241234567</phone>
        <message>Payment received for utility bill</message>
        <status>success</status>
        <type>payment</type>
    </transaction>
    <transaction>
        <id>TXN002</id>
        <date>2024-01-15 15:45:00</date>
        <amount>2500.00</amount>
        <phone>+233251234567</phone>
        <message>Money transfer completed</message>
        <status>success</status>
        <type>transfer</type>
    </transaction>
</momo_transactions>'''
        
        # Write sample XML to temp file
        with open(self.xml_path, 'w') as f:
            f.write(self.sample_xml)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_parser_initialization(self):
        """Test parser initialization"""
        parser = MoMoXMLParser(self.xml_path)
        self.assertEqual(parser.xml_path, self.xml_path)
        self.assertEqual(parser.parsed_data, [])
        self.assertEqual(parser.errors, [])
    
    def test_parse_file_success(self):
        """Test successful XML parsing"""
        parser = MoMoXMLParser(self.xml_path)
        transactions = parser.parse_file()
        
        self.assertEqual(len(transactions), 2)
        self.assertEqual(len(parser.errors), 0)
        
        # Check first transaction
        first_txn = transactions[0]
        self.assertEqual(first_txn['id'], 'TXN001')
        self.assertEqual(first_txn['date'], '2024-01-15 14:30:00')
        self.assertEqual(first_txn['amount'], 1500.0)
        self.assertEqual(first_txn['phone'], '+233241234567')
        self.assertEqual(first_txn['message'], 'Payment received for utility bill')
        self.assertEqual(first_txn['status'], 'success')
        self.assertEqual(first_txn['type'], 'payment')
    
    def test_parse_file_not_found(self):
        """Test parsing non-existent file"""
        parser = MoMoXMLParser(Path("nonexistent.xml"))
        
        with self.assertRaises(FileNotFoundError):
            parser.parse_file()
    
    def test_parse_file_invalid_xml(self):
        """Test parsing invalid XML"""
        invalid_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<momo_transactions>
    <transaction>
        <id>TXN001</id>
        <date>2024-01-15 14:30:00</date>
        <amount>1500.00</amount>
        <phone>+233241234567</phone>
        <message>Payment received for utility bill</message>
        <status>success</status>
        <type>payment</type>
    <transaction>
        <id>TXN002</id>
        <date>2024-01-15 15:45:00</date>
        <amount>2500.00</amount>
        <phone>+233251234567</phone>
        <message>Money transfer completed</message>
        <status>success</status>
        <type>transfer</type>
    </transaction>
</momo_transactions>'''
        
        invalid_xml_path = Path(self.temp_dir) / "invalid.xml"
        with open(invalid_xml_path, 'w') as f:
            f.write(invalid_xml)
        
        parser = MoMoXMLParser(invalid_xml_path)
        
        with self.assertRaises(Exception):
            parser.parse_file()
    
    def test_extract_text_from_element(self):
        """Test text extraction from XML elements"""
        parser = MoMoXMLParser()
        
        # Test with direct child element
        from xml.etree.ElementTree import Element, SubElement
        root = Element('transaction')
        id_elem = SubElement(root, 'id')
        id_elem.text = 'TXN001'
        
        result = parser._extract_text(root, ['id'])
        self.assertEqual(result, 'TXN001')
        
        # Test with attribute
        root.set('transaction_id', 'TXN002')
        result = parser._extract_text(root, ['transaction_id'])
        self.assertEqual(result, 'TXN002')
        
        # Test with case-insensitive search
        result = parser._extract_text(root, ['ID'])
        self.assertEqual(result, 'TXN001')
    
    def test_extract_amount(self):
        """Test amount extraction and parsing"""
        parser = MoMoXMLParser()
        
        from xml.etree.ElementTree import Element, SubElement
        
        # Test with clean amount
        root = Element('transaction')
        amount_elem = SubElement(root, 'amount')
        amount_elem.text = '1500.00'
        
        result = parser._extract_amount(root)
        self.assertEqual(result, 1500.0)
        
        # Test with currency symbols
        amount_elem.text = '$1,500.00'
        result = parser._extract_amount(root)
        self.assertEqual(result, 1500.0)
        
        # Test with negative amount
        amount_elem.text = '-500.00'
        result = parser._extract_amount(root)
        self.assertEqual(result, -500.0)
    
    def test_extract_phone(self):
        """Test phone number extraction and normalization"""
        parser = MoMoXMLParser()
        
        from xml.etree.ElementTree import Element, SubElement
        
        # Test with Ghana format
        root = Element('transaction')
        phone_elem = SubElement(root, 'phone')
        
        # Test various formats
        test_cases = [
            ('+233241234567', '+233241234567'),  # Already correct
            ('233241234567', '+233241234567'),   # Missing +
            ('0241234567', '+233241234567'),    # Local format
            ('241234567', '+233241234567'),     # 9 digits
        ]
        
        for input_phone, expected in test_cases:
            phone_elem.text = input_phone
            result = parser._extract_phone(root)
            self.assertEqual(result, expected)
    
    def test_validate_transaction(self):
        """Test transaction validation"""
        parser = MoMoXMLParser()
        
        # Valid transaction
        valid_txn = {
            'id': 'TXN001',
            'date': '2024-01-15 14:30:00',
            'amount': 1500.0
        }
        self.assertTrue(parser._validate_transaction(valid_txn))
        
        # Invalid transaction - missing date
        invalid_txn1 = {
            'id': 'TXN001',
            'amount': 1500.0
        }
        self.assertFalse(parser._validate_transaction(invalid_txn1))
        
        # Invalid transaction - missing amount
        invalid_txn2 = {
            'id': 'TXN001',
            'date': '2024-01-15 14:30:00'
        }
        self.assertFalse(parser._validate_transaction(invalid_txn2))
    
    def test_get_summary(self):
        """Test summary statistics"""
        parser = MoMoXMLParser()
        parser.parsed_data = [{'id': 'TXN001'}, {'id': 'TXN002'}]
        parser.errors = ['Error 1']
        
        summary = parser.get_summary()
        self.assertEqual(summary['total_parsed'], 2)
        self.assertEqual(summary['total_errors'], 1)
        self.assertEqual(summary['success_rate'], 66.66666666666666)

class TestParseMoMoXML(unittest.TestCase):
    """Test cases for convenience function"""
    
    def test_parse_momo_xml_function(self):
        """Test the convenience function"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<momo_transactions>
    <transaction>
        <id>TXN001</id>
        <date>2024-01-15 14:30:00</date>
        <amount>1500.00</amount>
    </transaction>
</momo_transactions>''')
            temp_path = Path(f.name)
        
        try:
            transactions = parse_momo_xml(temp_path)
            self.assertEqual(len(transactions), 1)
            self.assertEqual(transactions[0]['id'], 'TXN001')
        finally:
            temp_path.unlink()

if __name__ == '__main__':
    unittest.main()
