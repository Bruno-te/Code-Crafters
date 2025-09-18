"""
Data cleaning and normalization module for MoMo SMS transactions
"""
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from dateutil import parser as date_parser
import unicodedata

from .config import DATE_FORMATS, PHONE_PATTERNS, ETL_LOG_PATH, COUNTRY_DIAL_CODE

# Configure logging
logging.basicConfig(
    filename=ETL_LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataCleaner:
    """Clean and normalize transaction data"""
    
    def __init__(self):
        self.cleaned_data = []
        self.cleaning_errors = []
        
    def clean_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and normalize a list of transactions"""
        logger.info(f"Starting data cleaning for {len(transactions)} transactions")
        
        cleaned_transactions = []
        
        for i, transaction in enumerate(transactions):
            try:
                cleaned = self._clean_single_transaction(transaction, i)
                if cleaned:
                    cleaned_transactions.append(cleaned)
            except Exception as e:
                error_msg = f"Error cleaning transaction {i}: {e}"
                logger.warning(error_msg)
                self.cleaning_errors.append(error_msg)
                continue
        
        logger.info(f"Successfully cleaned {len(cleaned_transactions)} transactions")
        self.cleaned_data = cleaned_transactions
        
        return cleaned_transactions
    
    def _clean_single_transaction(self, transaction: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
        """Clean and normalize a single transaction"""
        try:
            cleaned = transaction.copy()
            
            # Clean and normalize each field
            cleaned['date'] = self._normalize_date(cleaned.get('date'))
            cleaned['amount'] = self._normalize_amount(cleaned.get('amount'))
            cleaned['phone'] = self._normalize_phone(cleaned.get('phone'))
            cleaned['message'] = self._normalize_message(cleaned.get('message'))
            cleaned['status'] = self._normalize_status(cleaned.get('status'))
            cleaned['type'] = self._normalize_type(cleaned.get('type'))
            cleaned['sender'] = self._normalize_sender(cleaned.get('sender'))
            cleaned['recipient'] = self._normalize_recipient(cleaned.get('recipient'))
            cleaned['fee'] = self._normalize_amount(cleaned.get('fee'))
            cleaned['balance'] = self._normalize_amount(cleaned.get('balance'))
            
            # Add metadata
            cleaned['cleaned_at'] = datetime.now().isoformat()
            cleaned['cleaning_version'] = '1.0'
            
            # Validate cleaned transaction
            if not self._validate_cleaned_transaction(cleaned):
                logger.warning(f"Transaction {index} failed validation after cleaning")
                return None
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Error cleaning transaction {index}: {e}")
            return None
    
    def _normalize_date(self, date_value: Any) -> Optional[str]:
        """Normalize date values to ISO format"""
        if not date_value:
            return None
        
        try:
            # Convert to string if needed
            if isinstance(date_value, (int, float)):
                # Handle Unix timestamp
                if date_value > 1e10:  # Likely milliseconds
                    date_value = date_value / 1000
                return datetime.fromtimestamp(date_value).isoformat()
            
            date_str = str(date_value).strip()
            
            # Try parsing with dateutil first (most flexible)
            try:
                parsed_date = date_parser.parse(date_str)
                return parsed_date.isoformat()
            except:
                pass
            
            # Try specific formats
            for date_format in DATE_FORMATS:
                try:
                    parsed_date = datetime.strptime(date_str, date_format)
                    return parsed_date.isoformat()
                except:
                    continue
            
            # Try common patterns
            patterns = [
                r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
                r'(\d{1,2})/(\d{1,2})/(\d{4})',  # DD/MM/YYYY
                r'(\d{1,2})-(\d{1,2})-(\d{4})',  # DD-MM-YYYY
            ]
            
            for pattern in patterns:
                match = re.match(pattern, date_str)
                if match:
                    if len(match.group(1)) == 4:  # YYYY-MM-DD
                        year, month, day = match.groups()
                    else:  # DD/MM/YYYY or DD-MM-YYYY
                        day, month, year = match.groups()
                    
                    try:
                        parsed_date = datetime(int(year), int(month), int(day))
                        return parsed_date.isoformat()
                    except:
                        continue
            
            logger.warning(f"Could not parse date: {date_value}")
            return None
            
        except Exception as e:
            logger.warning(f"Error normalizing date {date_value}: {e}")
            return None
    
    def _normalize_amount(self, amount_value: Any) -> Optional[float]:
        """Normalize amount values"""
        if amount_value is None:
            return None
        
        try:
            # Convert to float if needed
            if isinstance(amount_value, (int, float)):
                return float(amount_value)
            
            amount_str = str(amount_value).strip()
            
            # Remove currency symbols, commas, and spaces
            cleaned = re.sub(r'[^\d.-]', '', amount_str)
            
            # Handle negative amounts
            if cleaned.startswith('-'):
                return -float(cleaned[1:])
            
            return float(cleaned)
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error normalizing amount {amount_value}: {e}")
            return None
    
    def _normalize_phone(self, phone_value: Any) -> Optional[str]:
        """Normalize phone numbers using configured country dial code"""
        if not phone_value:
            return None
        
        try:
            phone_str = str(phone_value).strip()
            
            # Remove all non-digit characters except +
            cleaned = re.sub(r'[^\d+]', '', phone_str)
            
            # Normalize to configured country format
            if cleaned.startswith(COUNTRY_DIAL_CODE):
                return cleaned
            elif cleaned.startswith(COUNTRY_DIAL_CODE.lstrip('+')):
                return '+' + cleaned
            elif cleaned.startswith('0'):
                return COUNTRY_DIAL_CODE + cleaned[1:]
            elif len(cleaned) == 9:
                return COUNTRY_DIAL_CODE + cleaned
            elif len(cleaned) == 10 and cleaned.startswith('0'):
                return COUNTRY_DIAL_CODE + cleaned[1:]
            else:
                logger.warning(f"Unrecognized phone format: {phone_value}")
                return None
                
        except Exception as e:
            logger.warning(f"Error normalizing phone {phone_value}: {e}")
            return None
    
    def _normalize_message(self, message_value: Any) -> Optional[str]:
        """Normalize message text"""
        if not message_value:
            return None
        
        try:
            message_str = str(message_value).strip()
            
            # Remove extra whitespace
            message_str = re.sub(r'\s+', ' ', message_str)
            
            # Normalize unicode characters
            message_str = unicodedata.normalize('NFKC', message_str)
            
            # Remove control characters
            message_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', message_str)
            
            return message_str if message_str else None
            
        except Exception as e:
            logger.warning(f"Error normalizing message {message_value}: {e}")
            return None
    
    def _normalize_status(self, status_value: Any) -> Optional[str]:
        """Normalize transaction status"""
        if not status_value:
            return 'unknown'
        
        try:
            status_str = str(status_value).strip().lower()
            
            # Map common status values
            status_mapping = {
                'success': 'success',
                'completed': 'success',
                'done': 'success',
                'ok': 'success',
                'pending': 'pending',
                'processing': 'pending',
                'in_progress': 'pending',
                'failed': 'failed',
                'error': 'failed',
                'declined': 'failed',
                'rejected': 'failed',
                'cancelled': 'cancelled',
                'canceled': 'cancelled'
            }
            
            return status_mapping.get(status_str, status_str)
            
        except Exception as e:
            logger.warning(f"Error normalizing status {status_value}: {e}")
            return 'unknown'
    
    def _normalize_type(self, type_value: Any) -> Optional[str]:
        """Normalize transaction type"""
        if not type_value:
            return 'unknown'
        
        try:
            type_str = str(type_value).strip().lower()
            
            # Map common type values
            type_mapping = {
                'payment': 'payment',
                'pay': 'payment',
                'bill': 'payment',
                'utility': 'payment',
                'transfer': 'transfer',
                'send': 'transfer',
                'money': 'transfer',
                'withdrawal': 'withdrawal',
                'withdraw': 'withdrawal',
                'cashout': 'withdrawal',
                'deposit': 'deposit',
                'topup': 'deposit',
                'recharge': 'deposit'
            }
            
            return type_mapping.get(type_str, type_str)
            
        except Exception as e:
            logger.warning(f"Error normalizing type {type_value}: {e}")
            return 'unknown'
    
    def _normalize_sender(self, sender_value: Any) -> Optional[str]:
        """Normalize sender information"""
        if not sender_value:
            return None
        
        try:
            sender_str = str(sender_value).strip()
            
            # Remove extra whitespace
            sender_str = re.sub(r'\s+', ' ', sender_str)
            
            # Normalize unicode
            sender_str = unicodedata.normalize('NFKC', sender_str)
            
            return sender_str if sender_str else None
            
        except Exception as e:
            logger.warning(f"Error normalizing sender {sender_value}: {e}")
            return None
    
    def _normalize_recipient(self, recipient_value: Any) -> Optional[str]:
        """Normalize recipient information"""
        if not recipient_value:
            return None
        
        try:
            recipient_str = str(recipient_value).strip()
            
            # Remove extra whitespace
            recipient_str = re.sub(r'\s+', ' ', recipient_str)
            
            # Normalize unicode
            recipient_str = unicodedata.normalize('NFKC', recipient_str)
            
            return recipient_str if recipient_str else None
            
        except Exception as e:
            logger.warning(f"Error normalizing recipient {recipient_value}: {e}")
            return None
    
    def _validate_cleaned_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Validate cleaned transaction has required fields"""
        required_fields = ['date', 'amount']
        
        for field in required_fields:
            if not transaction.get(field):
                return False
        
        return True
    
    def get_cleaning_errors(self) -> List[str]:
        """Get list of cleaning errors"""
        return self.cleaning_errors
    
    def get_cleaning_summary(self) -> Dict[str, Any]:
        """Get cleaning summary statistics"""
        return {
            'total_cleaned': len(self.cleaned_data),
            'total_errors': len(self.cleaning_errors),
            'success_rate': (len(self.cleaned_data) / (len(self.cleaned_data) + len(self.cleaning_errors))) * 100 if self.cleaned_data or self.cleaning_errors else 0
        }

def clean_transactions(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convenience function to clean transactions"""
    cleaner = DataCleaner()
    return cleaner.clean_transactions(transactions)

if __name__ == "__main__":
    # Test cleaning
    sample_transactions = [
        {
            'id': 'TXN001',
            'date': '2024-01-15 14:30:00',
            'amount': '1,500.00',
            'phone': '0241234567',
            'message': 'Payment received',
            'status': 'SUCCESS'
        }
    ]
    
    try:
        cleaned = clean_transactions(sample_transactions)
        print(f"Cleaned {len(cleaned)} transactions")
        if cleaned:
            print("Sample cleaned transaction:", cleaned[0])
    except Exception as e:
        print(f"Error: {e}")
