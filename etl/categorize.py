"""
Transaction categorization module for MoMo SMS data
"""
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from .config import TRANSACTION_CATEGORIES, AMOUNT_THRESHOLDS, ETL_LOG_PATH

# Configure logging
logging.basicConfig(
    filename=ETL_LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TransactionCategorizer:
    """Categorize transactions based on various criteria"""
    
    def __init__(self):
        self.categorized_data = []
        self.categorization_errors = []
        self.category_stats = defaultdict(int)
        
    def categorize_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Categorize a list of transactions"""
        logger.info(f"Starting categorization for {len(transactions)} transactions")
        
        categorized_transactions = []
        
        for i, transaction in enumerate(transactions):
            try:
                categorized = self._categorize_single_transaction(transaction, i)
                if categorized:
                    categorized_transactions.append(categorized)
                    # Update statistics
                    self.category_stats[categorized.get('category', 'unknown')] += 1
            except Exception as e:
                error_msg = f"Error categorizing transaction {i}: {e}"
                logger.warning(error_msg)
                self.categorization_errors.append(error_msg)
                continue
        
        logger.info(f"Successfully categorized {len(categorized_transactions)} transactions")
        self.categorized_data = categorized_transactions
        
        return categorized_transactions
    
    def _categorize_single_transaction(self, transaction: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
        """Categorize a single transaction"""
        try:
            categorized = transaction.copy()
            
            # Apply categorization rules
            categorized['category'] = self._determine_category(transaction)
            categorized['amount_range'] = self._categorize_amount_range(transaction.get('amount'))
            categorized['time_category'] = self._categorize_time(transaction.get('date'))
            categorized['risk_level'] = self._assess_risk_level(transaction)
            categorized['geographic_region'] = self._determine_geographic_region(transaction)
            
            # Add categorization metadata
            categorized['categorized_at'] = datetime.now().isoformat()
            categorized['categorization_version'] = '1.0'
            
            return categorized
            
        except Exception as e:
            logger.error(f"Error categorizing transaction {index}: {e}")
            return None
    
    def _determine_category(self, transaction: Dict[str, Any]) -> str:
        """Determine the primary category of a transaction"""
        # Check if type is already set
        if transaction.get('type') and transaction['type'] != 'unknown':
            return transaction['type']
        
        # Check message content for keywords
        message = transaction.get('message', '').lower()
        phone = transaction.get('phone', '')
        
        # Score each category based on message content
        category_scores = defaultdict(int)
        
        for category, keywords in TRANSACTION_CATEGORIES.items():
            for keyword in keywords:
                if keyword.lower() in message:
                    category_scores[category] += 1
        
        # Check phone number patterns (e.g., merchant codes)
        if self._is_merchant_phone(phone):
            category_scores['payment'] += 2
        
        # Check amount patterns
        amount = transaction.get('amount')
        if amount:
            if amount < 1000:
                category_scores['deposit'] += 1
            elif amount > 10000:
                category_scores['transfer'] += 1
        
        # Return category with highest score, default to 'unknown'
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        
        return 'unknown'
    
    def _categorize_amount_range(self, amount: Optional[float]) -> str:
        """Categorize transaction amount into ranges"""
        if amount is None:
            return 'unknown'
        
        if amount <= AMOUNT_THRESHOLDS['small']:
            return 'small'
        elif amount <= AMOUNT_THRESHOLDS['medium']:
            return 'medium'
        elif amount <= AMOUNT_THRESHOLDS['large']:
            return 'large'
        else:
            return 'very_large'
    
    def _categorize_time(self, date_str: Optional[str]) -> str:
        """Categorize transaction time"""
        if not date_str:
            return 'unknown'
        
        try:
            # Parse ISO date string
            if 'T' in date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                date_obj = datetime.fromisoformat(date_str)
            
            hour = date_obj.hour
            
            if 6 <= hour < 12:
                return 'morning'
            elif 12 <= hour < 17:
                return 'afternoon'
            elif 17 <= hour < 21:
                return 'evening'
            else:
                return 'night'
                
        except Exception as e:
            logger.warning(f"Error categorizing time for {date_str}: {e}")
            return 'unknown'
    
    def _assess_risk_level(self, transaction: Dict[str, Any]) -> str:
        """Assess the risk level of a transaction"""
        risk_score = 0
        
        # Amount-based risk
        amount = transaction.get('amount', 0)
        if amount > 50000:
            risk_score += 3
        elif amount > 10000:
            risk_score += 2
        elif amount > 5000:
            risk_score += 1
        
        # Time-based risk
        time_category = self._categorize_time(transaction.get('date'))
        if time_category == 'night':
            risk_score += 1
        
        # Status-based risk
        status = transaction.get('status', '').lower()
        if status in ['failed', 'pending']:
            risk_score += 1
        
        # Phone number risk
        phone = transaction.get('phone', '')
        if self._is_suspicious_phone(phone):
            risk_score += 2
        
        # Determine risk level
        if risk_score >= 4:
            return 'high'
        elif risk_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _determine_geographic_region(self, transaction: Dict[str, Any]) -> str:
        """Determine geographic region based on phone number"""
        phone = transaction.get('phone', '')
        
        if not phone:
            return 'unknown'
        
        # Ghana phone number patterns
        # This is a simplified version - in production you'd use a proper phone number library
        if phone.startswith('+233'):
            # Extract area code (first 2 digits after 233)
            area_code = phone[4:6]
            
            # Map area codes to regions (simplified)
            region_mapping = {
                '20': 'Greater Accra',
                '21': 'Greater Accra',
                '22': 'Greater Accra',
                '23': 'Greater Accra',
                '24': 'Greater Accra',
                '25': 'Greater Accra',
                '26': 'Greater Accra',
                '27': 'Greater Accra',
                '28': 'Greater Accra',
                '29': 'Greater Accra',
                '30': 'Ashanti',
                '31': 'Ashanti',
                '32': 'Ashanti',
                '33': 'Ashanti',
                '34': 'Ashanti',
                '35': 'Ashanti',
                '36': 'Ashanti',
                '37': 'Ashanti',
                '38': 'Ashanti',
                '39': 'Ashanti',
                '40': 'Western',
                '41': 'Western',
                '42': 'Western',
                '43': 'Western',
                '44': 'Western',
                '45': 'Western',
                '46': 'Western',
                '47': 'Western',
                '48': 'Western',
                '49': 'Western',
                '50': 'Central',
                '51': 'Central',
                '52': 'Central',
                '53': 'Central',
                '54': 'Central',
                '55': 'Central',
                '56': 'Central',
                '57': 'Central',
                '58': 'Central',
                '59': 'Central'
            }
            
            return region_mapping.get(area_code, 'Other')
        
        return 'unknown'
    
    def _is_merchant_phone(self, phone: str) -> bool:
        """Check if phone number belongs to a merchant"""
        if not phone:
            return False
        
        # Simple heuristic: check for common merchant patterns
        # In production, you'd have a database of merchant numbers
        merchant_patterns = [
            r'233\d{9}',  # Ghana numbers
            r'\+233\d{9}'
        ]
        
        for pattern in merchant_patterns:
            if re.match(pattern, phone):
                return True
        
        return False
    
    def _is_suspicious_phone(self, phone: str) -> bool:
        """Check if phone number is suspicious"""
        if not phone:
            return False
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'000000000',  # All zeros
            r'111111111',  # All ones
            r'123456789',  # Sequential
            r'987654321'   # Reverse sequential
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, phone):
                return True
        
        return False
    
    def get_categorization_errors(self) -> List[str]:
        """Get list of categorization errors"""
        return self.categorization_errors
    
    def get_category_statistics(self) -> Dict[str, int]:
        """Get statistics about categorized transactions"""
        return dict(self.category_stats)
    
    def get_categorization_summary(self) -> Dict[str, Any]:
        """Get categorization summary statistics"""
        return {
            'total_categorized': len(self.categorized_data),
            'total_errors': len(self.categorization_errors),
            'success_rate': (len(self.categorized_data) / (len(self.categorized_data) + len(self.categorization_errors))) * 100 if self.categorized_data or self.categorization_errors else 0,
            'category_distribution': dict(self.category_stats)
        }

def categorize_transactions(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convenience function to categorize transactions"""
    categorizer = TransactionCategorizer()
    return categorizer.categorize_transactions(transactions)

if __name__ == "__main__":
    # Test categorization
    sample_transactions = [
        {
            'id': 'TXN001',
            'date': '2024-01-15T14:30:00',
            'amount': 1500.0,
            'phone': '+233241234567',
            'message': 'Payment received for utility bill',
            'status': 'success'
        }
    ]
    
    try:
        categorized = categorize_transactions(sample_transactions)
        print(f"Categorized {len(categorized)} transactions")
        if categorized:
            print("Sample categorized transaction:", categorized[0])
    except Exception as e:
        print(f"Error: {e}")
