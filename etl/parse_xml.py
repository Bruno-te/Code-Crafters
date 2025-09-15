"""
XML parsing module for MoMo SMS data
"""
import xml.etree.ElementTree as ET
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import re

from .config import XML_INPUT_PATH, ETL_LOG_PATH

# Configure logging
logging.basicConfig(
    filename=ETL_LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MoMoXMLParser:
    """Parser for MoMo SMS XML data"""
    
    def __init__(self, xml_path: Optional[Path] = None):
        self.xml_path = xml_path or XML_INPUT_PATH
        self.parsed_data = []
        self.errors = []
        
    def parse_file(self) -> List[Dict[str, Any]]:
        """Parse the XML file and extract transaction data"""
        try:
            logger.info(f"Starting XML parsing from {self.xml_path}")
            
            if not self.xml_path.exists():
                raise FileNotFoundError(f"XML file not found: {self.xml_path}")
            
            # Parse XML
            tree = ET.parse(self.xml_path)
            root = tree.getroot()
            
            # Extract transactions
            transactions = self._extract_transactions(root)
            
            logger.info(f"Successfully parsed {len(transactions)} transactions")
            self.parsed_data = transactions
            
            return transactions
            
        except ET.ParseError as e:
            error_msg = f"XML parsing error: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            raise
        except Exception as e:
            error_msg = f"Unexpected error during XML parsing: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            raise
    
    def _extract_transactions(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract transaction data from XML root element"""
        transactions = []
        
        # Common XML structures for MoMo SMS data
        # Adjust these selectors based on your actual XML structure
        transaction_elements = root.findall('.//transaction') or \
                             root.findall('.//sms') or \
                             root.findall('.//message') or \
                             root.findall('.//record')
        
        if not transaction_elements:
            # Try alternative paths
            transaction_elements = root.findall('.//*[contains(local-name(), "transaction")]') or \
                                 root.findall('.//*[contains(local-name(), "sms")]')
        
        logger.info(f"Found {len(transaction_elements)} transaction elements")
        
        for i, elem in enumerate(transaction_elements):
            try:
                transaction = self._parse_transaction_element(elem, i)
                if transaction:
                    # Filter out OTP/auth messages commonly found in MoMo SMS exports
                    message_lower = (transaction.get('message') or '').lower()
                    if self._is_otp_message(message_lower):
                        continue
                    transactions.append(transaction)
            except Exception as e:
                error_msg = f"Error parsing transaction {i}: {e}"
                logger.warning(error_msg)
                self.errors.append(error_msg)
                continue
        
        return transactions

    def _is_otp_message(self, message_lower: str) -> bool:
        """Detect OTP/verification messages to exclude from transactions."""
        if not message_lower:
            return False
        otp_keywords = [
            'one-time password', 'otp', 'does not recommend that you share',
            'verification code', 'do not share', 'be vigilant'
        ]
        return any(keyword in message_lower for keyword in otp_keywords)
    
    def _parse_transaction_element(self, elem: ET.Element, index: int) -> Optional[Dict[str, Any]]:
        """Parse individual transaction element"""
        try:
            # Extract common fields with fallbacks
            transaction = {
                'id': self._extract_text(elem, ['id', 'transaction_id', 'ref', 'reference']),
                'date': self._extract_text(elem, ['date', 'timestamp', 'time', 'created_at']),
                'amount': self._extract_amount(elem),
                'phone': self._extract_phone(elem),
                'message': self._extract_text(elem, ['message', 'text', 'content', 'body']),
                'status': self._extract_text(elem, ['status', 'state', 'result']),
                'sender': self._extract_text(elem, ['sender', 'from', 'source']),
                'recipient': self._extract_text(elem, ['recipient', 'to', 'destination']),
                'type': self._extract_text(elem, ['type', 'transaction_type', 'category']),
                'fee': self._extract_amount(elem, ['fee', 'charge', 'cost']),
                'balance': self._extract_amount(elem, ['balance', 'account_balance']),
                'raw_data': ET.tostring(elem, encoding='unicode')
            }
            
            # Generate ID if not present
            if not transaction['id']:
                transaction['id'] = f"TXN{index:06d}"
            
            # Validate required fields
            if not self._validate_transaction(transaction):
                logger.warning(f"Transaction {index} missing required fields: {transaction}")
                return None
            
            return transaction
            
        except Exception as e:
            logger.error(f"Error parsing transaction element {index}: {e}")
            return None
    
    def _extract_text(self, elem: ET.Element, field_names: List[str]) -> Optional[str]:
        """Extract text content from element using multiple possible field names"""
        for field_name in field_names:
            # Try direct child elements
            child = elem.find(field_name)
            if child is not None and child.text:
                return child.text.strip()
            
            # Try attributes
            if field_name in elem.attrib:
                return elem.attrib[field_name].strip()
            
            # Try case-insensitive search
            for child in elem:
                if child.tag.lower() == field_name.lower() and child.text:
                    return child.text.strip()
        
        return None
    
    def _extract_amount(self, elem: ET.Element, field_names: List[str] = None) -> Optional[float]:
        """Extract and parse amount values"""
        if field_names is None:
            field_names = ['amount', 'value', 'sum', 'total']
        
        amount_text = self._extract_text(elem, field_names)
        if not amount_text:
            return None
        
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[^\d.-]', '', amount_text)
            return float(cleaned)
        except ValueError:
            logger.warning(f"Could not parse amount: {amount_text}")
            return None
    
    def _extract_phone(self, elem: ET.Element) -> Optional[str]:
        """Extract and normalize phone number"""
        phone_text = self._extract_text(elem, ['phone', 'mobile', 'number', 'msisdn'])
        if not phone_text:
            return None
        
        # Normalize phone number
        phone = re.sub(r'[^\d+]', '', phone_text)
        
        # Ensure Ghana format
        if phone.startswith('0'):
            phone = '+233' + phone[1:]
        elif phone.startswith('233') and not phone.startswith('+233'):
            phone = '+' + phone
        
        return phone if phone else None
    
    def _validate_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Validate that transaction has required fields"""
        required_fields = ['date', 'amount']
        
        for field in required_fields:
            if not transaction.get(field):
                return False
        
        return True
    
    def get_errors(self) -> List[str]:
        """Get list of parsing errors"""
        return self.errors
    
    def get_summary(self) -> Dict[str, Any]:
        """Get parsing summary statistics"""
        return {
            'total_parsed': len(self.parsed_data),
            'total_errors': len(self.errors),
            'success_rate': (len(self.parsed_data) / (len(self.parsed_data) + len(self.errors))) * 100 if self.parsed_data or self.errors else 0
        }

def parse_momo_xml(xml_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Convenience function to parse MoMo XML data"""
    parser = MoMoXMLParser(xml_path)
    return parser.parse_file()

if __name__ == "__main__":
    # Test parsing
    try:
        transactions = parse_momo_xml()
        print(f"Parsed {len(transactions)} transactions")
        if transactions:
            print("Sample transaction:", transactions[0])
    except Exception as e:
        print(f"Error: {e}")
