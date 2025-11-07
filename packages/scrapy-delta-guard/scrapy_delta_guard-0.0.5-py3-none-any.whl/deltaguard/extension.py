import logging
from collections import defaultdict
from importlib import import_module
from scrapy import signals
from scrapy.exceptions import NotConfigured

logger = logging.getLogger(__name__)

class DeltaGuard:
    """
    A Scrapy extension to monitor data drift by comparing scraped items to
    database records, with configurable thresholds and alerting.
    """
    def __init__(self, crawler):
        self.stats = crawler.stats
        self.settings = crawler.settings
        self.crawler = crawler

        # Core settings
        self.batch_size = self.settings.getint("DELTA_GUARD_BATCH_SIZE", 50)
        self.default_threshold = self.settings.get("DELTA_GUARD_DEFAULT_THRESHOLD", 5)
        self.stop_on_high_delta = self.settings.getbool("DELTA_GUARD_STOP_SPIDER_ON_HIGH_DELTA", True)

        # Alerting settings
        self.jira_func_path = self.settings.get("DELTA_GUARD_JIRA_FUNC")
        self.slack_webhook = self.settings.get("DELTA_GUARD_SLACK_WEBHOOK")

        # Configurable None handling
        self.db_none_is_delta = self.settings.getbool('DELTA_GUARD_DB_NONE_IS_DELTA', False)
        self.spider_none_is_delta = self.settings.getbool('DELTA_GUARD_SPIDER_NONE_IS_DELTA', False)

        # Parse the field configurations
        self.raw_fields_config = self.settings.getlist("DELTA_GUARD_FIELDS_CONFIG")
        self.fields_config = [fc for fc in (self._parse_field_config(fc) for fc in self.raw_fields_config) if fc is not None]

        # Internal state
        self.delta_batch = []
        self.item_count = 0
        self.alert_triggered = False # Suppresses duplicate alerts
        self._load_alert_functions()

    def _parse_field_config(self, field_conf):
        """
        Normalizes a field config dict, defaulting 'db_var' and 'spider_var'
        to 'name', and converting various threshold formats to a float percentage.
        """
        name = field_conf.get('name')
        if not name:
            logger.warning(f"DeltaGuard: Skipping invalid field config (missing 'name'): {field_conf}")
            return None

        threshold = field_conf.get('threshold', self.default_threshold)
        threshold_val = self.default_threshold

        try:
            if isinstance(threshold, str) and '%' in threshold:
                threshold_val = float(threshold.strip().replace('%', ''))
            else:
                threshold_val = float(threshold)
        except (ValueError, TypeError):
            logger.warning(f"DeltaGuard: Invalid threshold format '{threshold}' for field '{name}'. Using default.")
            threshold_val = self.default_threshold
            if isinstance(threshold_val, str): # Handle if default is also string
                 threshold_val = float(threshold_val.strip().replace('%', ''))

        if threshold_val > 1:
            threshold_val /= 100.0

        return {
            'name': name,
            'db_var': field_conf.get('db_var', name),
            'spider_var': field_conf.get('spider_var', name),
            'threshold': threshold_val,
        }

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool("DELTA_GUARD_ENABLED"):
            raise NotConfigured("DeltaGuard is not enabled.")
        ext = cls(crawler)
        # NEW: Initialize the flag on the spider instance
        setattr(crawler.spider, 'delta_guard_high_delta', False)
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        logger.info("DeltaGuard extension enabled and configured ✅.")
        return ext

    def item_scraped(self, item, response, spider):
        db_item = item.get('db_item')
        if not db_item: return

        self.item_count += 1
        item_deltas = self._compare_fields(item, db_item)
        if item_deltas:
            self.delta_batch.append(item_deltas)

        if self.item_count >= self.batch_size:
            self._process_batch(spider)

    def _compare_fields(self, item, db_item):
        deltas = []
        for field_conf in self.fields_config:
            db_var, spider_var = field_conf["db_var"], field_conf["spider_var"]
            old_value = self._get_db_item_value(db_item, db_var)
            new_value = item.get(spider_var)

            if old_value is None and new_value is None: continue
            if old_value is None and new_value is not None and not self.db_none_is_delta: continue
            if new_value is None and old_value is not None and not self.spider_none_is_delta: continue

            if str(old_value) != str(new_value):
                deltas.append({"field": field_conf["name"]})
                self.stats.inc_value(f'deltaguard/delta_detected/{field_conf["name"]}')
        return deltas

    def _process_batch(self, spider):
        if not self.delta_batch:
            self._reset_batch()
            return

        fields_summary = defaultdict(int)
        for item_deltas in self.delta_batch:
            for delta in item_deltas:
                fields_summary[delta['field']] += 1
        
        details = ', '.join([f"{field} ({count})" for field, count in fields_summary.items()])
        logger.info(f"DeltaGuard: Batch processed. Delta summary: {details}.")

        for field_conf in self.fields_config:
            field_name = field_conf['name']
            threshold_percent = field_conf['threshold']
            threshold_count = int(self.batch_size * threshold_percent)
            if threshold_count == 0 and threshold_percent > 0: threshold_count = 1
            
            delta_count = fields_summary.get(field_name, 0)
            
            if delta_count >= threshold_count:
                if self.alert_triggered:
                    break # Alerts already sent, no need to check other fields
                
                self.alert_triggered = True
                logger.warning(
                    f"DeltaGuard: HIGH DELTA on field '{field_name}'. "
                    f"Found {delta_count} deltas ({delta_count/self.batch_size:.0%}), meeting/exceeding threshold of {threshold_percent:.0%}."
                )
                self._trigger_alerts(spider, field_name, delta_count, threshold_percent)
                
                if self.stop_on_high_delta:
                    # NEW: Set the spider flag instead of an abrupt stop
                    setattr(spider, 'delta_guard_high_delta', True)
                    logger.warning(f"DeltaGuard: Flag 'delta_guard_high_delta' set on spider. Commits should now be skipped in pipelines.")
                    logger.warning(f"DeltaGuard: Gracefully stopping spider due to high delta rate on '{field_name}'.")
                    self.stats.set_value('finish_reason', f'deltaguard_shutdown_{field_name}')
                    self.crawler.engine.close_spider(spider, reason=f'deltaguard_shutdown_{field_name}')
                break
        self._reset_batch()

    def _reset_batch(self):
        self.item_count = 0
        self.delta_batch.clear()

    def spider_closed(self, spider, reason):
        if self.item_count > 0: self._process_batch(spider)

    def _load_alert_functions(self):
        self.jira_func = None
        if self.jira_func_path:
            try:
                module_path, func_name = self.jira_func_path.rsplit('.', 1)
                module = import_module(module_path)
                self.jira_func = getattr(module, func_name)
            except (ImportError, AttributeError) as e:
                logger.error(f"DeltaGuard: Could not load Jira function from '{self.jira_func_path}': {e}")

    def _trigger_alerts(self, spider, field, count, threshold_percent):
        # NEW: Improved alert message with percentages
        delta_percentage = count / self.batch_size
        alert_message = (
            f":alert: **DeltaGuard Alert** for Spider: `{spider.name}`\n\n"
            f"**High delta rate detected for field: `{field}`**\n"
            f"Found `{count}` changed items ({delta_percentage:.0%}), meeting/exceeding the threshold of {threshold_percent:.0%}."
        )

        if self.slack_webhook:
            try:
                import requests
                requests.post(self.slack_webhook, json={"text": alert_message}, headers={"Content-Type": "application/json"})
                self.stats.inc_value('deltaguard/alerts_sent/slack')
            except Exception as e:
                logger.error(f"DeltaGuard: Failed to send Slack notification: {e}")

        if self.jira_func:
            try:
                summary = f"High Delta Rate on '{field}' in Spider: {spider.name}"
                # NEW: Pass the entire spider object to the Jira function
                self.jira_func(spider, summary, alert_message)
                self.stats.inc_value('deltaguard/alerts_sent/jira')
            except Exception as e:
                logger.error(f"DeltaGuard: Failed to execute Jira function: {e}")

    def _get_db_item_value(self, db_item, key):
        if isinstance(db_item, dict):
            return db_item.get(key, None)
        return getattr(db_item, key, None)

    def _get_db_item_id(self, db_item):
        return self._get_db_item_value(db_item, 'id') or 'N/A'
