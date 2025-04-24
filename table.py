from bplustree import BPlusTree

class Table:
    def __init__(self, name, schema = {}, order=8, search_key=None):
        self.name = name
        self.schema = schema
        self.order = order
        self.search_key = search_key
        self.data = BPlusTree(order=order)

    def validate_record(self, record):
        if not isinstance(record, dict):
            raise TypeError("Record must be a dictionary.")

        for field, value in record.items():
            if not isinstance(value, self.schema[field]):
                raise TypeError(f"Field {field} expects {self.schema[field]}, got {type(value)}")
        

    def insert(self, record):
        self.validate_record(record)
        key = record[self.search_key]
        if self.data.search(key):
            print(f"Duplicate key '{key}' detected.")
            return
        self.data.insert(key, record)
        print('data inserted successfully')

    def get(self, record_id):
        return self.data.search(record_id)

    def get_all(self):
        return self.data.get_all()

    def update(self, record_id, new_record):
        self.validate_record(new_record)
        if record_id != new_record[self.search_key]:
            print("Search key cannot be modified during update.")
            return
        if not self.data.search(record_id):
            print(f"No record found with key '{record_id}' to update.")
            return
        self.data.update(record_id, new_record)

    def delete(self, record_id):
        if not self.data.search(record_id):
            print(f"No record found with key '{record_id}' to delete.")
            return
        self.data.delete(record_id)

    def range_query(self, start_value, end_value):
        return self.data.range_query(start_value, end_value)
