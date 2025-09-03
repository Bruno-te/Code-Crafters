"""
Database loading module for MoMo SMS transactions
"""
import logging
import sqlite3
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import sqlite3

from .config import DATABASE_PATH, ETL_LOG_PATH

# Configure logging
logging.basicConfig(
    filename=ETL_LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseLoader:
    """Load processed transactions into SQLite database"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DATABASE_PATH
        self.connection = None
        self.loaded_count = 0
        self.load_errors = []
        
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def connect(self):
        """Establish database connection"""
        try:
            # Ensure database directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            
            # Enable foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
            
            logger.info(f"Connected to database: {self.db_path}")
            
        except Exception as e:
            error_msg = f"Error connecting to database: {e}"
            logger.error(error_msg)
            raise
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id TEXT PRIMARY KEY,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    phone TEXT,
                    message TEXT,
                    status TEXT,
                    type TEXT,
                    category TEXT,
                    sender TEXT,
                    recipient TEXT,
                    fee REAL,
                    balance REAL,
                    amount_range TEXT,
                    time_category TEXT,
                    risk_level TEXT,
                    geographic_region TEXT,
                    raw_data TEXT,
                    cleaned_at TEXT,
                    cleaning_version TEXT,
                    categorized_at TEXT,
                    categorization_version TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_phone ON transactions(phone)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_amount ON transactions(amount)")
            
            # Analytics table for aggregated data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value TEXT NOT NULL,
                    date TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(metric_name, date)
                )
            """)
            
            # Audit log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    record_id TEXT,
                    details TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.connection.commit()
            logger.info("Database tables created successfully")
            
        except Exception as e:
            error_msg = f"Error creating tables: {e}"
            logger.error(error_msg)
            self.connection.rollback()
            raise
    
    def load_transactions(self, transactions: List[Dict[str, Any]]) -> int:
        """Load transactions into database"""
        try:
            logger.info(f"Starting to load {len(transactions)} transactions")
            
            cursor = self.connection.cursor()
            loaded_count = 0
            
            for transaction in transactions:
                try:
                    # Prepare data for insertion
                    data = self._prepare_transaction_data(transaction)
                    
                    # Insert or update transaction
                    cursor.execute("""
                        INSERT OR REPLACE INTO transactions (
                            id, date, amount, phone, message, status, type, category,
                            sender, recipient, fee, balance, amount_range, time_category,
                            risk_level, geographic_region, raw_data, cleaned_at,
                            cleaning_version, categorized_at, categorization_version
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        data['id'], data['date'], data['amount'], data['phone'],
                        data['message'], data['status'], data['type'], data['category'],
                        data['sender'], data['recipient'], data['fee'], data['balance'],
                        data['amount_range'], data['time_category'], data['risk_level'],
                        data['geographic_region'], data['raw_data'], data['cleaned_at'],
                        data['cleaning_version'], data['categorized_at'], data['categorization_version']
                    ))
                    
                    loaded_count += 1
                    
                    # Log audit trail
                    cursor.execute("""
                        INSERT INTO audit_log (action, table_name, record_id, details)
                        VALUES (?, ?, ?, ?)
                    """, (
                        'INSERT' if data.get('is_new') else 'UPDATE',
                        'transactions',
                        data['id'],
                        json.dumps(data)
                    ))
                    
                except Exception as e:
                    error_msg = f"Error loading transaction {transaction.get('id', 'unknown')}: {e}"
                    logger.warning(error_msg)
                    self.load_errors.append(error_msg)
                    continue
            
            self.connection.commit()
            self.loaded_count = loaded_count
            
            logger.info(f"Successfully loaded {loaded_count} transactions")
            return loaded_count
            
        except Exception as e:
            error_msg = f"Error during transaction loading: {e}"
            logger.error(error_msg)
            self.connection.rollback()
            raise
    
    def _prepare_transaction_data(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare transaction data for database insertion"""
        data = {
            'id': transaction.get('id', ''),
            'date': transaction.get('date', ''),
            'amount': transaction.get('amount', 0.0),
            'phone': transaction.get('phone'),
            'message': transaction.get('message'),
            'status': transaction.get('status', 'unknown'),
            'type': transaction.get('type'),
            'category': transaction.get('category', 'unknown'),
            'sender': transaction.get('sender'),
            'recipient': transaction.get('recipient'),
            'fee': transaction.get('fee'),
            'balance': transaction.get('balance'),
            'amount_range': transaction.get('amount_range'),
            'time_category': transaction.get('time_category'),
            'risk_level': transaction.get('risk_level'),
            'geographic_region': transaction.get('geographic_region'),
            'raw_data': transaction.get('raw_data'),
            'cleaned_at': transaction.get('cleaned_at'),
            'cleaning_version': transaction.get('cleaning_version'),
            'categorized_at': transaction.get('categorized_at'),
            'categorization_version': transaction.get('categorization_version')
        }
        
        # Check if transaction already exists
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM transactions WHERE id = ?", (data['id'],))
        existing = cursor.fetchone()
        data['is_new'] = existing is None
        
        return data
    
    def update_analytics(self):
        """Update analytics table with aggregated data"""
        try:
            cursor = self.connection.cursor()
            
            # Get current date
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # Calculate various metrics
            metrics = self._calculate_metrics()
            
            for metric_name, metric_value in metrics.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO analytics (metric_name, metric_value, date)
                    VALUES (?, ?, ?)
                """, (metric_name, str(metric_value), current_date))
            
            self.connection.commit()
            logger.info("Analytics updated successfully")
            
        except Exception as e:
            error_msg = f"Error updating analytics: {e}"
            logger.error(error_msg)
            self.connection.rollback()
            raise
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate analytics metrics from transactions"""
        cursor = self.connection.cursor()
        metrics = {}
        
        try:
            # Total transactions
            cursor.execute("SELECT COUNT(*) FROM transactions")
            metrics['total_transactions'] = cursor.fetchone()[0]
            
            # Total amount
            cursor.execute("SELECT SUM(amount) FROM transactions")
            metrics['total_amount'] = cursor.fetchone()[0] or 0
            
            # Success rate
            cursor.execute("SELECT COUNT(*) FROM transactions WHERE status = 'success'")
            success_count = cursor.fetchone()[0]
            if metrics['total_transactions'] > 0:
                metrics['success_rate'] = (success_count / metrics['total_transactions']) * 100
            else:
                metrics['success_rate'] = 0
            
            # Category distribution
            cursor.execute("""
                SELECT category, COUNT(*) as count, SUM(amount) as total_amount
                FROM transactions 
                GROUP BY category
            """)
            category_data = cursor.fetchall()
            metrics['category_distribution'] = [
                {'category': row[0], 'count': row[1], 'amount': row[2]}
                for row in category_data
            ]
            
            # Amount range distribution
            cursor.execute("""
                SELECT amount_range, COUNT(*) as count
                FROM transactions 
                GROUP BY amount_range
            """)
            amount_data = cursor.fetchall()
            metrics['amount_distribution'] = [
                {'range': row[0], 'count': row[1]}
                for row in amount_data
            ]
            
            # Geographic distribution
            cursor.execute("""
                SELECT geographic_region, COUNT(*) as count
                FROM transactions 
                GROUP BY geographic_region
            """)
            geo_data = cursor.fetchall()
            metrics['geographic_distribution'] = [
                {'region': row[0], 'count': row[1]}
                for row in geo_data
            ]
            
        except Exception as e:
            logger.warning(f"Error calculating metrics: {e}")
        
        return metrics
    
    def export_dashboard_json(self, output_path: Optional[Path] = None) -> bool:
        """Export data for dashboard as JSON"""
        try:
            if output_path is None:
                from .config import DASHBOARD_JSON_PATH
                output_path = DASHBOARD_JSON_PATH
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Get analytics data
            metrics = self._calculate_metrics()
            
            # Get sample transactions for table display
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT id, date, amount, category, status, phone
                FROM transactions 
                ORDER BY date DESC 
                LIMIT 100
            """)
            transactions = [
                {
                    'id': row[0],
                    'date': row[1],
                    'amount': row[2],
                    'category': row[3],
                    'status': row[4],
                    'phone': row[5]
                }
                for row in cursor.fetchall()
            ]
            
            # Prepare dashboard data
            dashboard_data = {
                'summary': {
                    'totalTransactions': metrics.get('total_transactions', 0),
                    'totalAmount': metrics.get('total_amount', 0),
                    'successRate': round(metrics.get('success_rate', 0), 1),
                    'activeUsers': len(set(t['phone'] for t in transactions if t['phone']))
                },
                'transactions': transactions,
                'analytics': {
                    'categoryDistribution': metrics.get('category_distribution', []),
                    'amountDistribution': metrics.get('amount_distribution', []),
                    'geographicData': metrics.get('geographic_distribution', [])
                },
                'exported_at': datetime.now().isoformat(),
                'export_version': '1.0'
            }
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Dashboard JSON exported to {output_path}")
            return True
            
        except Exception as e:
            error_msg = f"Error exporting dashboard JSON: {e}"
            logger.error(error_msg)
            return False
    
    def get_loading_errors(self) -> List[str]:
        """Get list of loading errors"""
        return self.load_errors
    
    def get_loading_summary(self) -> Dict[str, Any]:
        """Get loading summary statistics"""
        return {
            'total_loaded': self.loaded_count,
            'total_errors': len(self.load_errors),
            'success_rate': (self.loaded_count / (self.loaded_count + len(self.load_errors))) * 100 if self.loaded_count or self.load_errors else 0
        }

def load_transactions_to_db(transactions: List[Dict[str, Any]], db_path: Optional[Path] = None) -> int:
    """Convenience function to load transactions to database"""
    with DatabaseLoader(db_path) as loader:
        loader.create_tables()
        return loader.load_transactions(transactions)

if __name__ == "__main__":
    # Test database loading
    sample_transactions = [
        {
            'id': 'TXN001',
            'date': '2024-01-15T14:30:00',
            'amount': 1500.0,
            'phone': '+233241234567',
            'message': 'Payment received',
            'status': 'success',
            'category': 'payment'
        }
    ]
    
    try:
        loaded_count = load_transactions_to_db(sample_transactions)
        print(f"Loaded {loaded_count} transactions to database")
    except Exception as e:
        print(f"Error: {e}")
