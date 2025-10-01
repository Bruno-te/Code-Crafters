# Data Structures & Algorithms (DSA) Implementation

## Overview
This folder contains the implementation of search algorithms for the MoMo SMS Transaction API, demonstrating different approaches to data retrieval and their performance characteristics.

## Files

### `search_algorithms.py`
Main implementation file containing:

1. **Linear Search Algorithm**
   - Time Complexity: O(n)
   - Space Complexity: O(1)
   - Scans through each transaction sequentially

2. **Dictionary Lookup Algorithm**
   - Time Complexity: O(1) average case
   - Space Complexity: O(n)
   - Uses hash table for direct key access

3. **Binary Search Algorithm**
   - Time Complexity: O(log n)
   - Space Complexity: O(1)
   - Requires sorted data, divides search space in half

## Performance Comparison

The implementation includes a comprehensive performance testing framework that:

- Tests each algorithm with the same set of random transaction IDs
- Measures execution time for multiple searches
- Calculates performance improvements between algorithms
- Provides detailed analysis of time and space complexity

## Usage

```bash
# Run the performance comparison
cd dsa
python search_algorithms.py
```

## Expected Results

For a dataset with 50+ transactions and 20 search operations:

- **Linear Search**: ~0.001-0.005 seconds total
- **Dictionary Lookup**: ~0.0001-0.0005 seconds total  
- **Binary Search**: ~0.0005-0.002 seconds total

**Performance Improvement**: Dictionary lookup is typically 5-10x faster than linear search.

## Algorithm Analysis

### Why Dictionary Lookup is Faster

1. **Direct Access**: Hash tables provide O(1) average access time
2. **No Iteration**: No need to scan through elements
3. **Optimized Data Structure**: Built-in hash function for fast key lookup

### Alternative Data Structures

1. **B-Trees**: For disk-based storage with O(log n) access
2. **Trie**: For string-based keys with prefix matching
3. **Bloom Filters**: For existence checking with minimal memory
4. **Skip Lists**: For ordered data with O(log n) access and easy updates

## Integration with API

The search algorithms can be integrated into the API server for:

- **Caching**: Pre-build dictionary for frequently accessed transactions
- **Indexing**: Create multiple indexes for different search criteria
- **Pagination**: Use binary search for sorted pagination
- **Filtering**: Combine algorithms for complex queries

## Performance Results

Results are automatically saved to `performance_results.json` with detailed metrics including:

- Execution times for each algorithm
- Success rates for searches
- Performance improvement ratios
- Complexity analysis

## Future Enhancements

1. **Parallel Processing**: Implement multi-threaded search
2. **Memory Mapping**: For large datasets that don't fit in memory
3. **Caching Strategies**: LRU cache for frequently accessed items
4. **Index Optimization**: Composite indexes for multi-field searches
