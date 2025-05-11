import hashlib as hl
import json


def hash_string_256(string):
    return hl.sha256(string).hexdigest()
def hash_block(block):
    """
    Hashes a block and retuen a string representation of it.

    Arguments:
        :block: The block should be hashed
    """
    return hl.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest() #list comprehension output look like this: -0-[]-1-[{'sender': 'Sagar', 'recipient': 'Alex', 'amount': 56.0}] also sorting the dictionaries using sort_keys