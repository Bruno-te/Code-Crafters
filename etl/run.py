#!/usr/bin/env python3
"""
Main ETL runner for MoMo SMS data processing
"""
import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from etl.parse_xml import MoMoXMLParser
from etl.clean_normalize import DataCleaner
from etl.categorize import TransactionCategorizer
from etl.load_db import DatabaseLoader
from etl.config import ETL_LOG_PATH, XML_INPUT_PATH, DASHBOARD_JSON_PATH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(ETL_LOG_PATH),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MoMoETLRunner:
    """Main ETL pipeline runner"""
    
    def __init__(self, xml_path: Path = None, db_path: Path = None):
        self.xml_path = xml_path or XML_INPUT_PATH
        self.db_path = db_path
        self.pipeline_stats = {
            'start_time': None,
            'end_time': None,
            'xml_parsing': {},
            'cleaning': {},
            'categorization': {},
            'database_loading': {},
            'total_processed': 0,
            'total_errors': 0
        }
    
    def run_pipeline(self) -> bool:
        """Run the complete ETL pipeline"""
        try:
            logger.info("=" * 60)
            logger.info("Starting MoMo SMS ETL Pipeline")
            logger.info("=" * 60)
            
            self.pipeline_stats['start_time'] = datetime.now().isoformat()
            
            # Step 1: Parse XML
            logger.info("Step 1: Parsing XML data...")
            transactions = self._parse_xml()
            if not transactions:
                logger.error("No transactions parsed from XML. Pipeline failed.")
                return False
            
            # Step 2: Clean and normalize data
            logger.info("Step 2: Cleaning and normalizing data...")
            cleaned_transactions = self._clean_data(transactions)
            if not cleaned_transactions:
                logger.error("No transactions cleaned. Pipeline failed.")
                return False
            
            # Step 3: Categorize transactions
            logger.info("Step 3: Categorizing transactions...")
            categorized_transactions = self._categorize_data(cleaned_transactions)
            if not categorized_transactions:
                logger.error("No transactions categorized. Pipeline failed.")
                return False
            
            # Step 4: Load to database
            logger.info("Step 4: Loading data to database...")
            success = self._load_to_database(categorized_transactions)
            if not success:
                logger.error("Failed to load data to database. Pipeline failed.")
                return False
            
            # Step 5: Export dashboard JSON
            logger.info("Step 5: Exporting dashboard data...")
            self._export_dashboard_data()
            
            # Pipeline completed successfully
            self.pipeline_stats['end_time'] = datetime.now().isoformat()
            self._print_pipeline_summary()
            
            logger.info("=" * 60)
            logger.info("ETL Pipeline completed successfully!")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Pipeline failed with error: {e}")
            self.pipeline_stats['end_time'] = datetime.now().isoformat()
            return False
    
    def _parse_xml(self) -> list:
        """Parse XML data"""
        try:
            parser = MoMoXMLParser(self.xml_path)
            transactions = parser.parse_file()
            
            # Update stats
            self.pipeline_stats['xml_parsing'] = {
                'total_parsed': len(transactions),
                'errors': len(parser.get_errors()),
                'success_rate': parser.get_summary()['success_rate']
            }
            
            logger.info(f"XML parsing completed: {len(transactions)} transactions parsed")
            return transactions
            
        except Exception as e:
            logger.error(f"XML parsing failed: {e}")
            self.pipeline_stats['xml_parsing'] = {'error': str(e)}
            raise
    
    def _clean_data(self, transactions: list) -> list:
        """Clean and normalize data"""
        try:
            cleaner = DataCleaner()
            cleaned_transactions = cleaner.clean_transactions(transactions)
            
            # Update stats
            self.pipeline_stats['cleaning'] = {
                'total_cleaned': len(cleaned_transactions),
                'errors': len(cleaner.get_cleaning_errors()),
                'success_rate': cleaner.get_cleaning_summary()['success_rate']
            }
            
            logger.info(f"Data cleaning completed: {len(cleaned_transactions)} transactions cleaned")
            return cleaned_transactions
            
        except Exception as e:
            logger.error(f"Data cleaning failed: {e}")
            self.pipeline_stats['cleaning'] = {'error': str(e)}
            raise
    
    def _categorize_data(self, transactions: list) -> list:
        """Categorize transactions"""
        try:
            categorizer = TransactionCategorizer()
            categorized_transactions = categorizer.categorize_transactions(transactions)
            
            # Update stats
            self.pipeline_stats['categorization'] = {
                'total_categorized': len(categorized_transactions),
                'errors': len(categorizer.get_categorization_errors()),
                'success_rate': categorizer.get_categorization_summary()['success_rate'],
                'category_distribution': categorizer.get_category_statistics()
            }
            
            logger.info(f"Categorization completed: {len(categorized_transactions)} transactions categorized")
            return categorized_transactions
            
        except Exception as e:
            logger.error(f"Categorization failed: {e}")
            self.pipeline_stats['categorization'] = {'error': str(e)}
            raise
    
    def _load_to_database(self, transactions: list) -> bool:
        """Load data to database"""
        try:
            with DatabaseLoader(self.db_path) as loader:
                loader.create_tables()
                loaded_count = loader.load_transactions(transactions)
                loader.update_analytics()
                
                # Update stats
                self.pipeline_stats['database_loading'] = {
                    'total_loaded': loaded_count,
                    'errors': len(loader.get_loading_errors()),
                    'success_rate': loader.get_loading_summary()['success_rate']
                }
                
                self.pipeline_stats['total_processed'] = loaded_count
                
                logger.info(f"Database loading completed: {loaded_count} transactions loaded")
                return True
                
        except Exception as e:
            logger.error(f"Database loading failed: {e}")
            self.pipeline_stats['database_loading'] = {'error': str(e)}
            return False
    
    def _export_dashboard_data(self):
        """Export dashboard data as JSON"""
        try:
            with DatabaseLoader(self.db_path) as loader:
                success = loader.export_dashboard_json()
                if success:
                    logger.info(f"Dashboard data exported to {DASHBOARD_JSON_PATH}")
                else:
                    logger.warning("Failed to export dashboard data")
                    
        except Exception as e:
            logger.error(f"Dashboard export failed: {e}")
    
    def _print_pipeline_summary(self):
        """Print pipeline summary"""
        print("\n" + "=" * 60)
        print("ETL PIPELINE SUMMARY")
        print("=" * 60)
        
        start_time = datetime.fromisoformat(self.pipeline_stats['start_time'])
        end_time = datetime.fromisoformat(self.pipeline_stats['end_time'])
        duration = end_time - start_time
        
        print(f"Pipeline Duration: {duration}")
        print(f"Total Transactions Processed: {self.pipeline_stats['total_processed']}")
        print()
        
        # XML Parsing
        xml_stats = self.pipeline_stats['xml_parsing']
        if 'error' not in xml_stats:
            print(f"XML Parsing: {xml_stats['total_parsed']} parsed, "
                  f"{xml_stats['errors']} errors, "
                  f"{xml_stats['success_rate']:.1f}% success rate")
        else:
            print(f"XML Parsing: FAILED - {xml_stats['error']}")
        
        # Cleaning
        cleaning_stats = self.pipeline_stats['cleaning']
        if 'error' not in cleaning_stats:
            print(f"Data Cleaning: {cleaning_stats['total_cleaned']} cleaned, "
                  f"{cleaning_stats['errors']} errors, "
                  f"{cleaning_stats['success_rate']:.1f}% success rate")
        else:
            print(f"Data Cleaning: FAILED - {cleaning_stats['error']}")
        
        # Categorization
        cat_stats = self.pipeline_stats['categorization']
        if 'error' not in cat_stats:
            print(f"Categorization: {cat_stats['total_categorized']} categorized, "
                  f"{cat_stats['errors']} errors, "
                  f"{cat_stats['success_rate']:.1f}% success rate")
            
            if 'category_distribution' in cat_stats:
                print("Category Distribution:")
                for category, count in cat_stats['category_distribution'].items():
                    print(f"  {category}: {count}")
        else:
            print(f"Categorization: FAILED - {cat_stats['error']}")
        
        # Database Loading
        db_stats = self.pipeline_stats['database_loading']
        if 'error' not in db_stats:
            print(f"Database Loading: {db_stats['total_loaded']} loaded, "
                  f"{db_stats['errors']} errors, "
                  f"{db_stats['success_rate']:.1f}% success rate")
        else:
            print(f"Database Loading: FAILED - {db_stats['error']}")
        
        print("=" * 60)
    
    def save_pipeline_log(self, output_path: Path = None):
        """Save pipeline log to file"""
        if output_path is None:
            output_path = ETL_LOG_PATH.parent / f"pipeline_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(output_path, 'w') as f:
                json.dump(self.pipeline_stats, f, indent=2, default=str)
            logger.info(f"Pipeline log saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save pipeline log: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='MoMo SMS ETL Pipeline')
    parser.add_argument('--xml', type=Path, help='Path to XML input file')
    parser.add_argument('--db', type=Path, help='Path to SQLite database')
    parser.add_argument('--export-json', action='store_true', help='Export dashboard JSON')
    parser.add_argument('--log', type=Path, help='Path to save pipeline log')
    
    args = parser.parse_args()
    
    try:
        # Initialize runner
        runner = MoMoETLRunner(
            xml_path=args.xml,
            db_path=args.db
        )
        
        # Run pipeline
        success = runner.run_pipeline()
        
        # Save log if requested
        if args.log:
            runner.save_pipeline_log(args.log)
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
