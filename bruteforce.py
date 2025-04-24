class BruteForceDB :
    def __init__(self):
        self.data = []

    def insert(self, key):
        self.data.append(key)

    def search(self, key):
        return key in self.data

    def delete (self, key):
        if key in self.data:
            self.data.remove(key)
    
    def update(self, key, new_value):

        for i, (k, v) in enumerate(self.data):
            if k == key:
                self.data[i] = (k, new_value)
                return True
        return False

    def range_query(self, start, end):
        return [k for k in self.data if start <= k <= end]