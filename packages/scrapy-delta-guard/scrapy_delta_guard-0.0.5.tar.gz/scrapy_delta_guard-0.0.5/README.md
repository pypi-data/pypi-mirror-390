# 🛡️ Scrapy DeltaGuard

**Scrapy DeltaGuard** is a powerful and easy-to-integrate Scrapy extension that monitors changes (deltas) between the data you scrape and the data already present in your database.

It helps maintain data integrity by monitoring data drift, reduces noisy or incorrect updates, and can automatically trigger alerts (e.g., to Slack or Jira) or stop a spider when significant changes occur.

## 🚀 Why use DeltaGuard?

Large-scale web scraping projects commonly face issues that corrupt data quality:
-   **Silent layout changes** on target websites that break selectors.
-   **Inconsistent formatting** for data like phone numbers (`123-456` vs `123456`).
-   **Transient incorrect data** appearing in sponsored or related content blocks.

DeltaGuard helps you:
-   Detect **real content changes**, not just formatting noise.
-   Avoid cascading bad data writes by automatically halting crawls if too many fields drift.
-   Integrate seamlessly without rewriting your existing item pipeline logic.
-   Notify downstream systems (Jira, Slack, etc.) when data quality issues are found.

---

## Installation

```bash
pip install scrapy-delta-guard
```

---

## ⚙️ Quick Start Guide

Follow these three steps to get `DeltaGuard` running in your project.

### 1. Configure Your Database Session for Detached Object Handling

To avoid SQLAlchemy’s `DetachedInstanceError` during delta checking, configure your
SQLAlchemy session with:

```python
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine, expire_on_commit=False)
```

This retains loaded database objects on commit, allowing access during Scrapy’s async pipeline.

### 2. Configure `settings.py`

Enable the extension and define field monitoring with flexible thresholds and options.

```python
EXTENSIONS = {
    'deltaguard.extension.DeltaGuard': 500,
}

DELTA_GUARD_ENABLED = True

DELTA_GUARD_BATCH_SIZE = 50

DELTA_GUARD_DEFAULT_THRESHOLD = '5%'

DELTA_GUARD_FIELDS_CONFIG = [
    {'name': 'email'},  # simple shorthand for same db/spider field
    {'name': 'phone_number', 'threshold': 10},  # 10% threshold
    {
        'name': 'years_experience',
        'db_var': 'years_exp',  # different db attribute
        'spider_var': 'years_exp_spider',  # different spider field
        'threshold': '15%'
    },
]

DELTA_GUARD_DB_NONE_IS_DELTA = True
DELTA_GUARD_SPIDER_NONE_IS_DELTA = False

DELTA_GUARD_STOP_SPIDER_ON_HIGH_DELTA = True

DELTA_GUARD_JIRA_FUNC = 'my_project.utils.create_jira_ticket'

DELTA_GUARD_SLACK_WEBHOOK = 'https://hooks.slack.com/services/your/webhook/url'

LOG_LEVEL = 'DEBUG'
```

### 3. Update Your Scrapy Item

Ensure your Scrapy `Item` class includes the `db_item` field to avoid `KeyError`:

```python
import scrapy

class YourItem(scrapy.Item):
    # ... your existing fields ...
    db_item = scrapy.Field()
```

### 4. Attach DB Items Using the Adapter in Your Pipelines

```python
from deltaguard.adapter import DeltaGuardAdapter

class YourPipeline:
    def process_item(self, item, spider):
        db_item = self.session.query(YourModel).filter_by(email=item.get('email')).first()
        DeltaGuardAdapter.attach(item, db_item)
        return item
```

---

## How Does `DeltaGuard` Work?

- The extension compares the fields in `DELTA_GUARD_FIELDS_CONFIG` between the scraped item and its corresponding database record.
- Differences are accumulated in batch sized groups defined by `DELTA_GUARD_BATCH_SIZE`.
- If deltas for any specific field exceed their configured percentage threshold during a batch, alerts are sent.
- Optionally, the spider is stopped immediately to prevent cascading bad data writes.

---

## Configuration Reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `DELTA_GUARD_ENABLED` | `bool` | `False` | Enables or disables the extension globally. |
| `DELTA_GUARD_FIELDS_CONFIG` | `list[dict]` | `[]` | Fields to monitor with optional threshold, `db_var`, and `spider_var`. |
| `DELTA_GUARD_BATCH_SIZE` | `int` | `50` | Number of items processed per batch evaluation. |
| `DELTA_GUARD_DEFAULT_THRESHOLD` | `str` or `float` | `5%` | Default batch delta threshold (percentage) if none specified per field. |
| `DELTA_GUARD_DB_NONE_IS_DELTA` | `bool` | `False` | Treats a `None` in DB as delta if spider has a value. |
| `DELTA_GUARD_SPIDER_NONE_IS_DELTA` | `bool` | `False` | Treats a `None` in spider as delta if DB has a value. |
| `DELTA_GUARD_STOP_SPIDER_ON_HIGH_DELTA` | `bool` | `True` | Stops the spider when any field delta threshold is exceeded. |
| `DELTA_GUARD_JIRA_FUNC` | `str` | `None` | Dotted path to alert function (e.g., JIRA ticket creator). |
| `DELTA_GUARD_SLACK_WEBHOOK` | `str` | `None` | Slack Incoming Webhook URL for notifications. |

---

## Advanced Field Configuration

The `DELTA_GUARD_FIELDS_CONFIG` allows flexible definitions.

```python
DELTA_GUARD_FIELDS_CONFIG = [
    {'name': 'email'},                 # Simple shorthand
    {'name': 'phone_number', 'db_var': 'phone', 'spider_var': 'contact_phone'},  # Custom fields
    {'name': 'salary', 'threshold': 15},  # 15% threshold as integer
    {'name': 'location', 'threshold': '25%'},  # 25% threshold as string
]
```

---

## License

MIT License
