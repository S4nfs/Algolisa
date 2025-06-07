#
#
#
#        ____                                                                           
#     //   ) )  //                   //__//             /                              
#    //___/ /  //  ___      ___     / ___      ___     / __      ___     ( )   __    
#   / __  (   // //   ) ) //   ) ) //\ \     //   ) ) //   ) ) //   ) ) / / //   ) ) 
#  //    ) ) // //   / / //       //  \ \   //       //   / / //   / / / / //   / /  
# //____/ / // ((___/ / ((____   //    \ \ ((____   //   / / ((___( ( / / //   / /   
#
#   A simple project on how blockchain works
#   Blockchain is a decentralized digital ledger that securely records transactions across a network of computers. 
#   It ensures data integrity by linking blocks of information in a chronological chain, making the data resistant to tampering.
#   Blockchain is the foundational technology that enables the existence of cryptocurrencies


# Features:
# ✔️ Chain of Data
# ✔️ Mine blocks
# ✔️ Block Hashing
# ✔️ Analyze verify chain
# ✔️ Transactions
# Store chain to disk
# Node Network
# Share Data, Resolve conflicts
# Wallets

from functools import reduce

from collections import OrderedDict #OrderedDict is a class from collections that preserves the order of keys as they were added
from  hash_util import hash_block, hash_string_256
import json

MINING_REWARD = 10
genesis_block = {'previous_hash': '', 'index':0, 'transactions': [], 'proof':100} #the very first block
blockchain = [genesis_block]
open_transactions = [] #using Lists to hold each transactions details
owner = 'Sagar'
participants = {'Sagar'}

def load_data():
    try:
        with open('./secure_blockchain.txt', 'r') as f:
            file_content = f.readlines()
            global blockchain, open_transactions
            blockchain = json.loads(file_content[0][:-1])
            updated_blockchain = []
            for block in blockchain:
                updated_block = {'previous_hash': block['previous_hash'], 'index': block['index'], 'proof': block['proof'], 'transactions': [OrderedDict([('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in block['transactions']]}
                updated_blockchain.append(updated_block)
                blockchain = updated_blockchain

            open_transactions = json.loads(file_content[1])
            updated_transactions = []
            for tx in updated_transactions:
                updated_transactions =OrderedDict([('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])])
                updated_transactions.append(updated_transactions)
                open_transactions = updated_transactions

    except (IOError, IndexError):
        print('File not found! Starting with genesis block...')

load_data()

def save_data():
    with open('./secure_blockchain.txt', 'w') as f:
        f.write(json.dumps(blockchain))
        f.write('\n')
        f.write(json.dumps(open_transactions))

def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    print(guess_hash)
    return guess_hash[0:2] == '00'

def proof_of_work():
    last_block=blockchain[-1]
    last_hash = hash_block(last_block) 
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof +=1
    return proof

def get_balance(participant):
    tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender']== participant] for block in blockchain]
    open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0 )

    tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient']== participant] for block in blockchain]
    amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0 )

    return amount_received - amount_sent

def get_last_blockchain_value():
    """ Returns the last value of the current bockchain """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]

def verify_transaction(transaction):
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']
    

def add_transaction( recipient, sender=owner, amount = 1.0):
    """ Append new value and last blockchain value to the block
    
    Arguments:
        :sender: the sender of the coins
        :recipient: the receiver of the coins
        :amount: transaction amount
    """
    
    transaction = {'sender': sender, 'recipient': recipient, 'amount': amount} #using dictionary to store the transaction details
    transaction = OrderedDict([('sender', sender), ('recipient', recipient), ('amount', amount)])
    
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True
    return False

def mine_block():
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block) 
    proof = proof_of_work()
    print(hashed_block)
    # reward_transaction = {
    #     'sender': 'MINING',
    #     'recipient': owner,
    #     'amount': MINING_REWARD
    # }
    
    reward_transaction = OrderedDict([('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
    copied_transaction = open_transactions[:]
    copied_transaction.append(reward_transaction)
    print(hashed_block)

    block = {'previous_hash': hashed_block, 'index': len(blockchain), 'transactions': copied_transaction, 'proof': proof}
    blockchain.append(block)
    return True

def get_transaction_value():
    """
    Returns the input of the users (a new transaction amount) as a float
    """
    tx_recipient = input('Enter the recipient name: ')
    tx_amount = float(input('Your transaction amount: '))
    return (tx_recipient, tx_amount) # a tuple with parenthesis


def get_user_choice():
    """
    Returns the choice
    """
    user_input = input('Your choice: ')
    return user_input

def print_blockchain_elements():
    # Output the blockchain blocks
    for block in blockchain:
        print('Outputting Block')
        print(block)
    else:
        print('-' * 40)
        
def verify_chain():
    for (index, block) in enumerate(blockchain):    #enumerate return a tuple
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            print("proof of work is invalid")
            return False 
    return True

def verify_transactions():
    return all([verify_transactions(tx) for tx in open_transactions ])

waiting_for_input = True

while waiting_for_input:
        print("Please Choose")
        print('1: Add a new transaction value')
        print('2: Mine a new block')
        print('3: Output the blockchain blocks')
        print('4: Output participants')
        print('5: Check transaction validity')
        print('h: Manipulate the chain')
        print('q: Quit')
        user_choice = get_user_choice()

        if user_choice == '1':
            tx_data = get_transaction_value()
            recipient, amount = tx_data
            # Add transaction amount to the blockchain
            if add_transaction(recipient, amount=amount):
                print('Added transaction')
            else:
                print('Transaction Failed')
            print(open_transactions)
        elif user_choice == '2':
            if mine_block():
                open_transactions = []
                save_data()
        elif user_choice == '3':
            print_blockchain_elements()
        elif user_choice == '4':
            print (participants)
        elif user_choice == '5':
            if verify_transactions():
                print ("All transactions are valid")
            else:
                print("Invalid Transaction are there")
        elif user_choice == 'h':
            if len(blockchain) >= 1:
                blockchain[0] = 2
        elif user_choice == 'q':
            waiting_for_input = False
        else:
            print("Invalid Input")
        if not verify_chain():
            print('Invalid Blockchain!')
            break
        print('Balance of {}: {:6.2f}'.format('Sagar', get_balance('Sagar')))
else:
    print('User Left.. Bye!👋')
