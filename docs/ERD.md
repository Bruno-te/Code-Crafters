## MoMo Analytics ERD

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

### Design Rationale (≈250 words)
The ERD models mobile money transactions extracted from SMS. Core transactional facts live in `TRANSACTIONS`: timestamp, amount, currency, status, and optional channel/location context captured during ETL. Each transaction links to a `sender` and a `receiver` in `USERS`, reflecting real-world flows between parties. Using separate `sender_id` and `receiver_id` (both FKs to `USERS`) avoids duplication and enables role-specific analytics (e.g., top senders vs receivers).

Categorization is normalized in `TRANSACTION_CATEGORIES` to support consistent grouping (payment, transfer, withdrawal, deposit) and future extensibility (subtypes). A transaction holds a single primary `category_id`, while nuanced labels (e.g., “utility”, “fee”, “reversal”) are handled via a many-to-many relationship between `TRANSACTIONS` and `TAGS`, resolved through the junction table `TRANSACTION_TAGS`. This pattern keeps the schema flexible for new analytical tags without schema changes and allows multi-label classification of the same transaction.

`SYSTEM_LOGS` captures ETL and processing events with severity and source, optionally referencing a specific `TRANSACTION` for traceability. This supports auditability and debugging across parsing, cleaning, categorization, and loading stages.

Primary keys are integer-based for compact indexes; `TRANSACTIONS.id` is BIGINT to accommodate high volumes. Monetary values use `DECIMAL(12,2)` to ensure precision. Uniqueness constraints on `USERS.phone`, `TAGS.name`, and `TRANSACTION_CATEGORIES.name` enforce data integrity. The `external_ref` on `TRANSACTIONS` prevents duplicate loads from the same SMS source. Temporal fields (`created_at`, `occurred_at`) enable partition-friendly queries and time-series analytics. Overall, this design balances normalization, integrity, and analytical flexibility aligned with the MoMo SMS ETL pipeline and dashboard needs.


