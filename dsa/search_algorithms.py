#!/usr/bin/env python3
"""
Data Structures & Algorithms Implementation for MoMo SMS Transaction Search
Demonstrates Linear Search vs Dictionary Lookup performance comparison
"""
import json
import time
import random
try:
    from typing import List, Dict, Any, Optional
except ImportError:
    # Fallback for older Python versions
    List = list
    Dict = dict
    Any = object
    Optional = object
from pathlib import Path

class TransactionSearch:
    """Search algorithms for transaction data"""
    
    def __init__(self, transactions_data: List[Dict[str, Any]]):
        self.transactions_list = transactions_data
        self.transactions_dict = {txn['id']: txn for txn in transactions_data}
        print(f"Initialized with {len(self.transactions_list)} transactions")
    
    def linear_search(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Linear Search Algorithm
        Time Complexity: O(n) - scans through entire list
        Space Complexity: O(1) - no additional space needed
        """
        for transaction in self.transactions_list:
            if transaction['id'] == transaction_id:
                return transaction
        return None
    
    def dictionary_lookup(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Dictionary Lookup Algorithm
        Time Complexity: O(1) average case - direct key access
        Space Complexity: O(n) - requires additional dictionary storage
        """
        return self.transactions_dict.get(transaction_id)
    
    def binary_search(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Binary Search Algorithm (requires sorted data)
        Time Complexity: O(log n) - divides search space in half each iteration
        Space Complexity: O(1) - iterative implementation
        """
        # Sort transactions by ID for binary search
        sorted_transactions = sorted(self.transactions_list, key=lambda x: x['id'])
        
        left, right = 0, len(sorted_transactions) - 1
        
        while left <= right:
            mid = (left + right) // 2
            mid_id = sorted_transactions[mid]['id']
            
            if mid_id == transaction_id:
                return sorted_transactions[mid]
            elif mid_id < transaction_id:
                left = mid + 1
            else:
                right = mid - 1
        
        return None
    
    def performance_test(self, num_searches: int = 20) -> Dict[str, Any]:
        """
        Compare performance of different search algorithms
        """
        if len(self.transactions_list) == 0:
            return {"error": "No transactions available for testing"}
        
        # Generate random transaction IDs for testing
        available_ids = [txn['id'] for txn in self.transactions_list]
        test_ids = random.sample(available_ids, min(num_searches, len(available_ids)))
        
        results = {
            "total_transactions": len(self.transactions_list),
            "searches_performed": len(test_ids),
            "algorithms": {}
        }
        
        # Test Linear Search
        start_time = time.time()
        linear_results = []
        for txn_id in test_ids:
            result = self.linear_search(txn_id)
            linear_results.append(result is not None)
        linear_time = time.time() - start_time
        
        results["algorithms"]["linear_search"] = {
            "total_time": round(linear_time, 6),
            "average_time": round(linear_time / len(test_ids), 6),
            "successful_searches": sum(linear_results),
            "time_complexity": "O(n)",
            "space_complexity": "O(1)"
        }
        
        # Test Dictionary Lookup
        start_time = time.time()
        dict_results = []
        for txn_id in test_ids:
            result = self.dictionary_lookup(txn_id)
            dict_results.append(result is not None)
        dict_time = time.time() - start_time
        
        results["algorithms"]["dictionary_lookup"] = {
            "total_time": round(dict_time, 6),
            "average_time": round(dict_time / len(test_ids), 6),
            "successful_searches": sum(dict_results),
            "time_complexity": "O(1)",
            "space_complexity": "O(n)"
        }
        
        # Test Binary Search
        start_time = time.time()
        binary_results = []
        for txn_id in test_ids:
            result = self.binary_search(txn_id)
            binary_results.append(result is not None)
        binary_time = time.time() - start_time
        
        results["algorithms"]["binary_search"] = {
            "total_time": round(binary_time, 6),
            "average_time": round(binary_time / len(test_ids), 6),
            "successful_searches": sum(binary_results),
            "time_complexity": "O(log n)",
            "space_complexity": "O(1)"
        }
        
        # Calculate performance improvements
        if linear_time > 0:
            dict_speedup = round(linear_time / dict_time, 2) if dict_time > 0 else float('inf')
            binary_speedup = round(linear_time / binary_time, 2) if binary_time > 0 else float('inf')
            
            results["performance_improvement"] = {
                "dictionary_vs_linear": f"{dict_speedup}x faster",
                "binary_vs_linear": f"{binary_speedup}x faster",
                "dictionary_vs_binary": f"{round(binary_time / dict_time, 2)}x faster" if dict_time > 0 else "N/A"
            }
        
        return results

def load_transaction_data() -> List[Dict[str, Any]]:
    """Load transaction data from JSON file"""
    try:
        # Try API data first
        api_data_path = Path("api/data/processed/transactions.json")
        if api_data_path.exists():
            with open(api_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Try ETL processed data
        etl_data_path = Path("data/processed/dashboard.json")
        if etl_data_path.exists():
            with open(etl_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Extract transactions from dashboard data
                if 'transactions' in data:
                    return data['transactions']
        
        # Fallback to sample data
        return generate_sample_data()
        
    except Exception as e:
        print(f"Error loading transaction data: {e}")
        return generate_sample_data()

def generate_sample_data() -> List[Dict[str, Any]]:
    """Generate sample transaction data for testing"""
    sample_transactions = []
    for i in range(50):
        transaction = {
            "id": f"TXN{i:06d}",
            "date": f"2024-01-{(i % 28) + 1:02d}T{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00Z",
            "amount": round(random.uniform(10, 1000), 2),
            "currency": "RWF",
            "sender": f"+250788{random.randint(100000, 999999)}",
            "recipient": f"+250788{random.randint(100000, 999999)}",
            "message": f"Sample transaction {i}",
            "type": random.choice(["credit", "debit"]),
            "status": random.choice(["success", "pending", "failed"]),
            "fee": round(random.uniform(0, 10), 2),
            "balance": round(random.uniform(1000, 50000), 2)
        }
        sample_transactions.append(transaction)
    
    return sample_transactions

def print_performance_results(results: Dict[str, Any]):
    """Print formatted performance results"""
    print("\n" + "="*80)
    print("DATA STRUCTURES & ALGORITHMS PERFORMANCE COMPARISON")
    print("="*80)
    
    print(f"Dataset: {results['total_transactions']} transactions")
    print(f"Searches performed: {results['searches_performed']}")
    print()
    
    for algo_name, metrics in results['algorithms'].items():
        print(f"{algo_name.upper().replace('_', ' ')}:")
        print(f"  Total time: {metrics['total_time']} seconds")
        print(f"  Average time per search: {metrics['average_time']} seconds")
        print(f"  Successful searches: {metrics['successful_searches']}/{results['searches_performed']}")
        print(f"  Time complexity: {metrics['time_complexity']}")
        print(f"  Space complexity: {metrics['space_complexity']}")
        print()
    
    if 'performance_improvement' in results:
        print("PERFORMANCE IMPROVEMENTS:")
        for comparison, improvement in results['performance_improvement'].items():
            print(f"  {comparison.replace('_', ' ').title()}: {improvement}")
        print()
    
    print("ALGORITHM ANALYSIS:")
    print("1. LINEAR SEARCH:")
    print("   - Scans through each element sequentially")
    print("   - Simple to implement and understand")
    print("   - No additional memory overhead")
    print("   - Performance degrades linearly with dataset size")
    print()
    
    print("2. DICTIONARY LOOKUP:")
    print("   - Uses hash table for O(1) average access time")
    print("   - Requires additional memory for hash table")
    print("   - Best for frequent lookups by key")
    print("   - Performance remains constant regardless of dataset size")
    print()
    
    print("3. BINARY SEARCH:")
    print("   - Requires sorted data")
    print("   - Divides search space in half each iteration")
    print("   - Good balance between time and space complexity")
    print("   - Performance scales logarithmically with dataset size")
    print()
    
    print("RECOMMENDATIONS:")
    print("- For small datasets (< 100 items): Linear search is acceptable")
    print("- For frequent lookups by ID: Dictionary lookup is optimal")
    print("- For sorted data with infrequent lookups: Binary search is efficient")
    print("- For production APIs: Dictionary lookup with proper indexing")

def main():
    """Main function to run DSA performance tests"""
    print("Loading transaction data...")
    transactions = load_transaction_data()
    
    if not transactions:
        print("No transaction data available. Exiting.")
        return
    
    print(f"Loaded {len(transactions)} transactions")
    
    # Initialize search algorithms
    searcher = TransactionSearch(transactions)
    
    # Run performance comparison
    print("Running performance tests...")
    results = searcher.performance_test(num_searches=20)
    
    # Print results
    print_performance_results(results)
    
    # Save results to file
    results_file = Path("dsa/performance_results.json")
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {results_file}")

if __name__ == "__main__":
    main()
