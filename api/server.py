"""
REST API server for MoMo SMS transaction management
Built with Python's http.server for the assignment requirements
"""
import json
import base64
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Any, Optional
import os
from pathlib import Path

# Import the transaction data
import sys
sys.path.append(str(Path(__file__).parent.parent))

from etl.parse_xml import MoMoXMLParser

class TransactionAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the Transaction API"""
    
    def __init__(self, *args, **kwargs):
        self.transactions = {}
        self.load_transactions()
        super().__init__(*args, **kwargs)
    
    def load_transactions(self):
        """Load transactions from JSON file"""
        try:
            json_path = Path("data/processed/transactions.json")
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    transactions_list = json.load(f)
                    # Convert list to dictionary with ID as key
                    for transaction in transactions_list:
                        self.transactions[transaction['id']] = transaction
                print(f"Loaded {len(self.transactions)} transactions")
            else:
                print("No transactions JSON file found, starting with empty dataset")
        except Exception as e:
            print(f"Error loading transactions: {e}")
            self.transactions = {}
    
    def save_transactions(self):
        """Save transactions to JSON file"""
        try:
            json_path = Path("data/processed/transactions.json")
            json_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert dictionary back to list
            transactions_list = list(self.transactions.values())
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(transactions_list, f, indent=4, ensure_ascii=False)
            print(f"Saved {len(transactions_list)} transactions")
        except Exception as e:
            print(f"Error saving transactions: {e}")
    
    def authenticate(self) -> bool:
        """Basic Authentication implementation"""
        auth_header = self.headers.get('Authorization', '')
        
        if not auth_header.startswith('Basic '):
            return False
        
        try:
            # Decode base64 credentials
            encoded_credentials = auth_header[6:]  # Remove 'Basic '
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':', 1)
            
            # Simple hardcoded credentials for demo
            # In production, this should be stored securely and hashed
            return username == 'admin' and password == 'password123'
        except:
            return False
    
    def send_unauthorized_response(self):
        """Send 401 Unauthorized response"""
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Transaction API"')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "error": "Unauthorized",
            "message": "Invalid credentials. Use Basic Auth with username: admin, password: password123"
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def send_json_response(self, data: Any, status_code: int = 200):
        """Send JSON response with specified status code"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
    
    def send_error_response(self, message: str, status_code: int = 400):
        """Send error response"""
        response = {"error": message}
        self.send_json_response(response, status_code)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        if not self.authenticate():
            self.send_unauthorized_response()
            return
        
        parsed_path = urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')
        
        if path_parts == ['transactions']:
            # GET /transactions - List all transactions
            self.get_all_transactions()
        elif path_parts == ['transactions', path_parts[1]] and len(path_parts) == 2:
            # GET /transactions/{id} - Get specific transaction
            transaction_id = path_parts[1]
            self.get_transaction_by_id(transaction_id)
        else:
            self.send_error_response("Invalid endpoint", 404)
    
    def do_POST(self):
        """Handle POST requests"""
        if not self.authenticate():
            self.send_unauthorized_response()
            return
        
        parsed_path = urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')
        
        if path_parts == ['transactions']:
            # POST /transactions - Create new transaction
            self.create_transaction()
        else:
            self.send_error_response("Invalid endpoint", 404)
    
    def do_PUT(self):
        """Handle PUT requests"""
        if not self.authenticate():
            self.send_unauthorized_response()
            return
        
        parsed_path = urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')
        
        if path_parts == ['transactions', path_parts[1]] and len(path_parts) == 2:
            # PUT /transactions/{id} - Update transaction
            transaction_id = path_parts[1]
            self.update_transaction(transaction_id)
        else:
            self.send_error_response("Invalid endpoint", 404)
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        if not self.authenticate():
            self.send_unauthorized_response()
            return
        
        parsed_path = urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')
        
        if path_parts == ['transactions', path_parts[1]] and len(path_parts) == 2:
            # DELETE /transactions/{id} - Delete transaction
            transaction_id = path_parts[1]
            self.delete_transaction(transaction_id)
        else:
            self.send_error_response("Invalid endpoint", 404)
    
    def get_all_transactions(self):
        """GET /transactions - List all transactions"""
        transactions_list = list(self.transactions.values())
        response = {
            "transactions": transactions_list,
            "count": len(transactions_list)
        }
        self.send_json_response(response)
    
    def get_transaction_by_id(self, transaction_id: str):
        """GET /transactions/{id} - Get specific transaction"""
        if transaction_id in self.transactions:
            self.send_json_response(self.transactions[transaction_id])
        else:
            self.send_error_response(f"Transaction with ID '{transaction_id}' not found", 404)
    
    def create_transaction(self):
        """POST /transactions - Create new transaction"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            transaction_data = json.loads(post_data.decode('utf-8'))
            
            # Validate required fields
            required_fields = ['amount', 'date', 'message']
            for field in required_fields:
                if field not in transaction_data:
                    self.send_error_response(f"Missing required field: {field}", 400)
                    return
            
            # Generate ID if not provided
            if 'id' not in transaction_data:
                transaction_data['id'] = f"TXN{uuid.uuid4().hex[:6].upper()}"
            
            # Check if ID already exists
            if transaction_data['id'] in self.transactions:
                self.send_error_response(f"Transaction with ID '{transaction_data['id']}' already exists", 409)
                return
            
            # Add to transactions
            self.transactions[transaction_data['id']] = transaction_data
            self.save_transactions()
            
            self.send_json_response(transaction_data, 201)
            
        except json.JSONDecodeError:
            self.send_error_response("Invalid JSON in request body", 400)
        except Exception as e:
            self.send_error_response(f"Error creating transaction: {str(e)}", 500)
    
    def update_transaction(self, transaction_id: str):
        """PUT /transactions/{id} - Update transaction"""
        if transaction_id not in self.transactions:
            self.send_error_response(f"Transaction with ID '{transaction_id}' not found", 404)
            return
        
        try:
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            update_data = json.loads(put_data.decode('utf-8'))
            
            # Update the transaction
            current_transaction = self.transactions[transaction_id]
            current_transaction.update(update_data)
            
            # Ensure ID doesn't change
            current_transaction['id'] = transaction_id
            
            self.save_transactions()
            self.send_json_response(current_transaction)
            
        except json.JSONDecodeError:
            self.send_error_response("Invalid JSON in request body", 400)
        except Exception as e:
            self.send_error_response(f"Error updating transaction: {str(e)}", 500)
    
    def delete_transaction(self, transaction_id: str):
        """DELETE /transactions/{id} - Delete transaction"""
        if transaction_id not in self.transactions:
            self.send_error_response(f"Transaction with ID '{transaction_id}' not found", 404)
            return
        
        deleted_transaction = self.transactions.pop(transaction_id)
        self.save_transactions()
        
        response = {
            "message": f"Transaction '{transaction_id}' deleted successfully",
            "deleted_transaction": deleted_transaction
        }
        self.send_json_response(response)

def run_server(port: int = 8000):
    """Run the API server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, TransactionAPIHandler)
    print(f"Transaction API server running on http://localhost:{port}")
    print("Authentication: username=admin, password=password123")
    print("Available endpoints:")
    print("  GET    /transactions           - List all transactions")
    print("  GET    /transactions/{id}      - Get specific transaction")
    print("  POST   /transactions           - Create new transaction")
    print("  PUT    /transactions/{id}      - Update transaction")
    print("  DELETE /transactions/{id}      - Delete transaction")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        httpd.server_close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='MoMo SMS Transaction API Server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run server on (default: 8000)')
    args = parser.parse_args()
    
    run_server(args.port)
