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
This is the link to our scrum board
https://app.clickup.com/90121048007/v/s/90125082789 

  
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
3. Copied `.env.example` to `.env` and configured settings
4. Placed `momo.xml` file in `data/raw/`

### Running the Application
1. **Process Data**: Runed the ETL pipeline
   ```bash
   ./scripts/run_etl.sh
   ```

2. **Start Frontend**: Served the dashboard
   ```bash
   ./scripts/serve_frontend.sh 8000 0.0.0.0
   ```

3. **Access Dashboard**: Open http://localhost:8000 in your browser
   - To allow others on my LAN: `http://my_LAN_IP:8000`
   - For a temporary public link: `npx localtunnel --port 8000`

### Alternative: Manual ETL Run
```bash
python etl/run.py --xml data/raw/momo.xml
```

## Development Workflow
- Used Agile/Scrum practices for development
- Runed tests before committing: `python -m unittest discover tests`
- Checked logs in `data/logs/etl.log` for debugging
- Followed the established project structure

## Testing
Runed the test suite:
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
1. Bruno:
   Created a feature branch and worked on backend 
   worked on SQL script in a /database folder
   and updated the README.md file
2. Racheal:
   Runed tests and worked on frontend.
   worked on json data modeling
3. Michaella:
   worked on System Architecture and will Submit a pull request 
   worked on ERD and documentation.

## Troubleshooting
- **XML parsing errors**: Checked XML format and structure
- **Database errors**: Verified file permissions and disk space
- **Frontend issues**: Checked browser console and network tab
  

## Documentation
### Database Design
- ERD: see `docs/ERD.md`
- MySQL schema and sample data: `database/database_setup.sql`
- JSON examples and mapping: `examples/json_examples.json`

### ERD (inline)
```mermaid
erDiagram
    USERS ||--o{ TRANSACTIONS : initiates
    USERS ||--o{ TRANSACTIONS : receives
    TRANSACTION_CATEGORIES ||--o{ TRANSACTIONS : categorizes
    TRANSACTIONS ||--o{ TRANSACTION_TAGS : has
    TAGS ||--o{ TRANSACTION_TAGS : labels
    SYSTEM_LOGS }o--|| TRANSACTIONS : references

    USERS {
        INT id PK
        VARCHAR phone UNIQUE
        VARCHAR full_name
        VARCHAR email
        DATETIME created_at
    }

    TRANSACTION_CATEGORIES {
        INT id PK
        VARCHAR name UNIQUE
        VARCHAR description
        DATETIME created_at
    }

    TRANSACTIONS {
        BIGINT id PK
        VARCHAR external_ref UNIQUE
        DATETIME occurred_at
        DECIMAL(12,2) amount
        VARCHAR currency
        ENUM status
        INT sender_id FK
        INT receiver_id FK
        INT category_id FK
        VARCHAR channel
        VARCHAR location
        TEXT message_excerpt
        DATETIME created_at
    }

    TAGS {
        INT id PK
        VARCHAR name UNIQUE
        VARCHAR description
        DATETIME created_at
    }

    TRANSACTION_TAGS {
        BIGINT transaction_id FK
        INT tag_id FK
        DATETIME created_at
        PK transaction_id, tag_id
    }

    SYSTEM_LOGS {
        BIGINT id PK
        VARCHAR level
        VARCHAR source
        TEXT message
        DATETIME created_at
        BIGINT transaction_id FK
    }
```

The editable Draw.io file: `docs/ERD.drawio`.
- **Performance issues**: Reviewied database indexes and query optimization

## Future Enhancements
- REST API with FastAPI
- Real-time data streaming
- Advanced analytics and ML models
- User authentication and roles
- Data export to multiple formats
- Integration with external systems

---

**Built with ❤️ by Code Crafters for the MoMo SMS Analytics Platform**
