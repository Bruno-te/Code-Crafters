# MoMo SMS Data Processing & Analytics Platform

## Project Overview
This enterprise-level fullstack application processes MoMo SMS data in XML format, cleans and categorizes the data, stores it in a relational database, and provides a frontend interface for data analysis and visualization.

## System Architecture
The system follows a modular ETL (Extract, Transform, Load) architecture:

```
XML Input → XML Parser → Data Cleaner → Categorizer → SQLite DB → Dashboard JSON → Frontend
    ↓           ↓           ↓           ↓           ↓           ↓           ↓
  Raw Data   Parsed     Cleaned    Categorized  Stored     Aggregated   Visualized
  XML File   Objects    Objects    Objects      Data       Analytics    Charts
```

**Key Components:**
- **XML Parser**: Extracts transaction data from MoMo SMS XML files
- **Data Cleaner**: Normalizes dates, amounts, phone numbers, and text
- **Categorizer**: Classifies transactions by type, amount range, time, and risk
- **Database**: SQLite storage with proper indexing and audit trails
- **Frontend**: Interactive dashboard with charts, tables, and filtering

## Scrum Board
**Project Management**: Our preferred tool is GitHub Projects

**Project Management**: Our preferred tool GitHub Projects
- **To Do**: Repository setup, architecture design, ETL development
- **In Progress**: Current sprint tasks
- **Done**: Completed features and milestones
  
## Features
- XML data parsing and validation
- Data cleaning and normalization
- Transaction categorization with risk assessment
- SQLite database storage with audit logging
- Interactive dashboard with charts and tables
- Real-time data filtering and search
- Report generation (daily, weekly, monthly, custom)
- Responsive design for mobile and desktop

## Tech Stack
- **Backend**: Python 3.8+ (ElementTree/lxml, dateutil)
- **Database**: SQLite with proper indexing
- **Frontend**: HTML5, CSS3, JavaScript (vanilla + Chart.js)
- **Testing**: Python unittest framework
- **Optional**: FastAPI for REST API

## Project Structure
```
├── README.md                         # Setup, run, overview
├── .env.example                      # Configuration template
├── requirements.txt                  # Python dependencies
├── .gitignore                        # Git ignore patterns
├── index.html                        # Dashboard entry point
├── web/                             # Frontend assets
│   ├── styles.css                    # Modern responsive styling
│   ├── chart_handler.js              # Dashboard functionality
│   └── assets/                       # Images/icons
├── data/                            # Data storage
│   ├── raw/                         # XML input files (git-ignored)
│   ├── processed/                   # Cleaned outputs
│   ├── db.sqlite3                   # SQLite database (git-ignored)
│   └── logs/                        # ETL logs (git-ignored)
├── etl/                             # Data processing pipeline
│   ├── __init__.py                  # Package initialization
│   ├── config.py                    # Configuration and paths
│   ├── parse_xml.py                 # XML parsing logic
│   ├── clean_normalize.py           # Data cleaning
│   ├── categorize.py                 # Transaction categorization
│   ├── load_db.py                   # Database operations
│   └── run.py                       # Main ETL runner
├── scripts/                         # Utility scripts
│   ├── run_etl.sh                   # ETL pipeline runner
│   └── serve_frontend.sh            # Frontend server
└── tests/                           # Unit tests
    ├── test_parse_xml.py            # XML parsing tests
    ├── test_clean_normalize.py      # Data cleaning tests
    └── test_categorize.py           # Categorization tests
```

## Quick Start

### Prerequisites
- Python 3.8+
- pip
- Modern web browser

### Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and configure settings (optional)
4. Place your `momo.xml` file in `data/raw/` (or use the sample created by the script)

### Running the Application
1. **Process Data**: Run the ETL pipeline
   ```bash
   ./scripts/run_etl.sh
   ```

2. **Start Frontend**: Serve the dashboard
   ```bash
   ./scripts/serve_frontend.sh
   ```

3. **Access Dashboard**: Open http://127.0.0.1:5500/ your browser

### Alternative: Manual ETL Run
```bash
python etl/run.py --xml data/raw/momo.xml
```

## Development Workflow
- Use Agile/Scrum practices for development
- Run tests before committing: `python -m unittest discover tests`
- Check logs in `data/logs/etl.log` for debugging
- Follow the established project structure

## Testing
Run the test suite:
```bash
python -m unittest discover tests
```

## Data Flow
1. **Input**: MoMo SMS XML files in `data/raw/`
2. **Processing**: ETL pipeline processes and categorizes data
3. **Storage**: Clean data stored in SQLite database
4. **Export**: Dashboard JSON generated for frontend
5. **Visualization**: Interactive charts and tables in web interface

## Configuration
Key configuration options in `etl/config.py`:
- File paths and directories
- Transaction categories and keywords
- Amount thresholds
- Phone number patterns
- Date formats

## Logging
- ETL logs: `data/logs/etl.log`
- Pipeline run logs: `data/logs/pipeline_run_*.json`
- Database audit trail: Built into SQLite

## Team Members
- ISHIMWE BRUNO(i.bruno@alustudent.com)
- MICHAELLA KAMIKAZI KARANGWA(m.kamikazi@alustudent.com)
- RACHEAL AKELLO(r.akello@alustudent.com)
**Team Name: Code Crafters**

## Contributing
1. Create a feature branch
2. Make your changes
3. Run tests: `python -m unittest discover tests`
4. Submit a pull request

## Troubleshooting
- **XML parsing errors**: Check XML format and structure
- **Database errors**: Verify file permissions and disk space
- **Frontend issues**: Check browser console and network tab
- **Performance issues**: Review database indexes and query optimization

## Future Enhancements
- REST API with FastAPI
- Real-time data streaming
- Advanced analytics and ML models
- User authentication and roles
- Data export to multiple formats
- Integration with external systems

---

**Built with ❤️ by Code Crafters for the MoMo SMS Analytics Platform**
