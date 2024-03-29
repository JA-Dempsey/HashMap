# Name: Andrew Dempsey
# OSU Email: dempsjam@oregonstate.edu
# Course: CS261 - Data Structures
# Assignment: Assignemnt 6 - Part 2
# Due Date: 8/9/2022
# Description: Implementation of a HashMap using
#              open address clash resolution.


from a6_include import (DynamicArray, HashEntry,
                        hash_function_1, hash_function_2)


class HashMap:
    def __init__(self, capacity: int, function) -> None:
        """
        Initialize new HashMap that uses
        quadratic probing for collision resolution
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        self._buckets = DynamicArray()

        # capacity must be a prime number
        self._capacity = self._next_prime(capacity)
        for _ in range(self._capacity):
            self._buckets.append(None)

        self._hash_function = function
        self._size = 0

    def __str__(self) -> str:
        """
        Override string method to provide more readable output
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        out = ''
        for i in range(self._buckets.length()):
            out += str(i) + ': ' + str(self._buckets[i]) + '\n'
        return out

    def _next_prime(self, capacity: int) -> int:
        """
        Increment from given number to find the closest prime number
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity % 2 == 0:
            capacity += 1

        while not self._is_prime(capacity):
            capacity += 2

        return capacity

    @staticmethod
    def _is_prime(capacity: int) -> bool:
        """
        Determine if given integer is a prime number and return boolean
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity == 2 or capacity == 3:
            return True

        if capacity == 1 or capacity % 2 == 0:
            return False

        factor = 3
        while factor ** 2 <= capacity:
            if capacity % factor == 0:
                return False
            factor += 2

        return True

    def get_size(self) -> int:
        """
        Return size of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._size

    def get_capacity(self) -> int:
        """
        Return capacity of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._capacity

    # ------------------------------------------------------------------ #
    def valid_put(self, entry: HashEntry or None) -> bool:
        """
        Helper method that determines if the given entry is a
        valid location for a put. If the location is valid
        it returns True, otherwise, it returns False.
        Will reset tombstone in preparation for a put if
        a tombstone is found.
        """
        if entry is None:
            return True
        else:
            if entry.is_tombstone:
                entry.is_tombstone = False
                return True
            else:
                return False

    def _next_index(self, start_index: int, quad_factor: int) -> (int, int):
        """
        Finds the next hash index to use given the current
        index and the current quadratic factor value. Returns
        a tuple (hash_index, quad_factor).
        """

        hash_index = (start_index + (quad_factor * quad_factor)) % self._capacity
        quad_factor += 1

        return hash_index, quad_factor

    def put(self, key: str, value: object) -> None:
        """
        Method that updates or adds a key/value pair in the
        hash map. Given key already exists, the value is updated.
        Otherwise, a proper position is found and then the key/value
        pair is added to the hash map. Resized when the current load
        factor is more than 0.5.
        """
        # remember, if the load factor is greater than or equal to 0.5,
        # resize the table before putting the new key/value pair
        if self.table_load() > 0.5:
            self.resize_table(self._capacity * 2)

        start_index = self._hash_function(key) % self.get_capacity()
        entry = self._buckets.get_at_index(start_index)
        hash_index = start_index

        j = 1  # Quadratic factor

        # Find a valid entry location
        is_valid_put = self.valid_put(entry)
        while not is_valid_put:
            # If key already in hash, update value
            if entry.key == key and not entry.is_tombstone:
                entry.value = value
                return

            # Quadratic probing
            hash_index, j = self._next_index(start_index, j)
            entry = self._buckets.get_at_index(hash_index)
            is_valid_put = self.valid_put(entry)

        self._buckets.set_at_index(hash_index, HashEntry(key, value))
        self._size += 1

    def table_load(self) -> float:
        """
        Method that returns the current hash table load
        factor.
        """
        return self.get_size() / self.get_capacity()

    def empty_buckets(self) -> int:
        """
        Method that returns the number of empty buckets
        in the hash table.
        """
        empty_count = 0
        for index in range(self._capacity):
            entry = self._buckets.get_at_index(index)
            if entry is None or entry.is_tombstone:
                empty_count += 1

        return empty_count

    def resize_table(self, new_capacity: int) -> None:
        """
        Method that changes the capacity of the internal hash table.
        Then rehashes the current key/value pairs for the new capacity
        values.
        """
        # remember to rehash non-deleted entries into new table
        if new_capacity < self._size:
            return

        # Ensure new_capacity is prime
        if self._is_prime(new_capacity):
            self._capacity = new_capacity
        else:
            self._capacity = self._next_prime(new_capacity)

        old_buckets = self._buckets

        # Reset buckets with new capacity
        self._buckets = DynamicArray()
        self._size = 0
        for _ in range(self._capacity):
            self._buckets.append(None)

        # Rehash old values
        for index in range(old_buckets.length()):
            entry = old_buckets.get_at_index(index)

            if entry is not None and not entry.is_tombstone:
                self.put(entry.key, entry.value)


    def get(self, key: str) -> object:
        """
        Method that returns the associated value with the
        given key.
        """
        start_index = self._hash_function(key) % self.get_capacity()
        entry = self._buckets.get_at_index(start_index)
        hash_index = start_index

        j = 1  # Quadratic factor
        while entry is not None:

            if entry.key == key and not entry.is_tombstone:
                return entry.value

            hash_index, j = self._next_index(start_index, j)
            entry = self._buckets.get_at_index(hash_index)

        return None

    def contains_key(self, key: str) -> bool:
        """
        Method that determines if a value associated with
        the given key is found. If a key/value is found,
        it returns True, otherwise, it returns False.
        """
        start_index = self._hash_function(key) % self.get_capacity()
        entry = self._buckets.get_at_index(start_index)

        j = 1  # Quadratic factor
        while entry is not None:

            if entry.key == key and not entry.is_tombstone:
                return True

            hash_index, j = self._next_index(start_index, j)
            entry = self._buckets.get_at_index(hash_index)

        return False

    def remove(self, key: str) -> None:
        """
        Method that removes the given entry associated with the
        given key.
        """
        start_index = self._hash_function(key) % self.get_capacity()
        entry = self._buckets.get_at_index(start_index)

        j = 1  # Quadratic factor
        while entry is not None:

            if entry.key == key and not entry.is_tombstone:
                entry.is_tombstone = True
                self._size -= 1
                return

            hash_index, j = self._next_index(start_index, j)
            entry = self._buckets.get_at_index(hash_index)

    def clear(self) -> None:
        """
        Method that clears the contents of the hash map.
        """
        self._buckets = DynamicArray()
        for _ in range(self._capacity):
            self._buckets.append(None)

        self._size = 0

    def get_keys_and_values(self) -> DynamicArray:
        """
        Method that returns a dynamic array where each index
        contains a tuple of a key/value pair stored in the hash
        map. Order not guaranteed.
        """
        tuple_output = DynamicArray()

        for index in range(self._capacity):
            entry = self._buckets.get_at_index(index)

            if entry is not None and not entry.is_tombstone:
                tuple_output.append((entry.key, entry.value))

        return tuple_output



# ------------------- BASIC TESTING ---------------------------------------- #

if __name__ == "__main__":

    print("\nPDF - put example 1")
    print("-------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('str' + str(i), i * 100)
        if i % 25 == 24:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - put example 2")
    print("-------------------")
    m = HashMap(41, hash_function_2)
    for i in range(50):
        m.put('str' + str(i // 3), i * 100)
        if i % 10 == 9:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - table_load example 1")
    print("--------------------------")
    m = HashMap(101, hash_function_1)
    print(round(m.table_load(), 2))
    m.put('key1', 10)
    print(round(m.table_load(), 2))
    m.put('key2', 20)
    print(round(m.table_load(), 2))
    m.put('key1', 30)
    print(round(m.table_load(), 2))

    print("\nPDF - table_load example 2")
    print("--------------------------")
    m = HashMap(53, hash_function_1)
    for i in range(50):
        m.put('key' + str(i), i * 100)
        if i % 10 == 0:
            print(round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - empty_buckets example 1")
    print("-----------------------------")
    m = HashMap(101, hash_function_1)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key1', 10)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key2', 20)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key1', 30)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key4', 40)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())

    print("\nPDF - empty_buckets example 2")
    print("-----------------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('key' + str(i), i * 100)
        if i % 30 == 0:
            print(m.empty_buckets(), m.get_size(), m.get_capacity())

    print("\nPDF - resize example 1")
    print("----------------------")
    m = HashMap(23, hash_function_1)
    m.put('key1', 10)
    print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))
    m.resize_table(30)
    print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))

    print("\nPDF - resize example 2")
    print("----------------------")
    m = HashMap(79, hash_function_2)
    keys = [i for i in range(1, 1000, 13)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())

    for capacity in range(111, 1000, 117):
        m.resize_table(capacity)

        if m.table_load() > 0.5:
            print(f"Check that the load factor is acceptable after the call to resize_table().\n"
                  f"Your load factor is {round(m.table_load(), 2)} and should be less than or equal to 0.5")

        m.put('some key', 'some value')
        result = m.contains_key('some key')
        m.remove('some key')

        for key in keys:
            # all inserted keys must be present
            result &= m.contains_key(str(key))
            # NOT inserted keys must be absent
            result &= not m.contains_key(str(key + 1))
        print(capacity, result, m.get_size(), m.get_capacity(), round(m.table_load(), 2))

    print("\nPDF - get example 1")
    print("-------------------")
    m = HashMap(31, hash_function_1)
    print(m.get('key'))
    m.put('key1', 10)
    print(m.get('key1'))

    print("\nPDF - get example 2")
    print("-------------------")
    m = HashMap(151, hash_function_2)
    for i in range(200, 300, 7):
        m.put(str(i), i * 10)
    print(m.get_size(), m.get_capacity())
    for i in range(200, 300, 21):
        print(i, m.get(str(i)), m.get(str(i)) == i * 10)
        print(i + 1, m.get(str(i + 1)), m.get(str(i + 1)) == (i + 1) * 10)

    print("\nPDF - contains_key example 1")
    print("----------------------------")
    m = HashMap(11, hash_function_1)
    print(m.contains_key('key1'))
    m.put('key1', 10)
    m.put('key2', 20)
    m.put('key3', 30)
    print(m.contains_key('key1'))
    print(m.contains_key('key4'))
    print(m.contains_key('key2'))
    print(m.contains_key('key3'))
    m.remove('key3')
    print(m.contains_key('key3'))

    print("\nPDF - contains_key example 2")
    print("----------------------------")
    m = HashMap(79, hash_function_2)
    keys = [i for i in range(1, 1000, 20)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())
    result = True
    for key in keys:
        # all inserted keys must be present
        result &= m.contains_key(str(key))
        # NOT inserted keys must be absent
        result &= not m.contains_key(str(key + 1))
    print(result)

    print("\nPDF - remove example 1")
    print("----------------------")
    m = HashMap(53, hash_function_1)
    print(m.get('key1'))
    m.put('key1', 10)
    print(m.get('key1'))
    m.remove('key1')
    print(m.get('key1'))
    m.remove('key4')

    print("\nPDF - clear example 1")
    print("---------------------")
    m = HashMap(101, hash_function_1)
    print(m.get_size(), m.get_capacity())
    m.put('key1', 10)
    m.put('key2', 20)
    m.put('key1', 30)
    print(m.get_size(), m.get_capacity())
    m.clear()
    print(m.get_size(), m.get_capacity())

    print("\nPDF - clear example 2")
    print("---------------------")
    m = HashMap(53, hash_function_1)
    print(m.get_size(), m.get_capacity())
    m.put('key1', 10)
    print(m.get_size(), m.get_capacity())
    m.put('key2', 20)
    print(m.get_size(), m.get_capacity())
    m.resize_table(100)
    print(m.get_size(), m.get_capacity())
    m.clear()
    print(m.get_size(), m.get_capacity())

    print("\nPDF - get_keys_and_values example 1")
    print("------------------------")
    m = HashMap(11, hash_function_2)
    for i in range(1, 6):
        m.put(str(i), str(i * 10))
    print(m.get_keys_and_values())

    m.resize_table(2)
    print(m.get_keys_and_values())

    m.put('20', '200')
    m.remove('1')
    m.resize_table(12)
    print(m.get_keys_and_values())
