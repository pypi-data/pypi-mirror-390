class DeltaGuardAdapter:
    """
    A simple adapter class to standardize attaching SQLAlchemy database objects
    to Scrapy items for DeltaGuard extension consumption.
    """
    @staticmethod
    def attach(item, db_item):
        """
        Attaches the database object to the item under the key 'db_item'.

        Args:
            item (scrapy.Item or dict): The item being processed.
            db_item (object): The SQLAlchemy object fetched from the database.
        """
        if db_item:
            item['db_item'] = db_item
