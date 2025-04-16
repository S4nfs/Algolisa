


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

MINING_REWARD = 10
genesis_block = {'previous_hash': '', 'index':0, 'transactions': []} #the very first block
blockchain = [genesis_block]
open_transactions = [] #using Lists to hold each transactions details
owner = 'Sagar'
participants = {'Sagar'}

def hash_block(block):
    return '-'.join([str(block[key]) for key in block])#list comprehension output look like this: -0-[]-1-[{'sender': 'Sagar', 'recipient': 'Alex', 'amount': 56.0}]  

def get_balance(participant):
    tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender']== participant] for block in blockchain]
    open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = 0
    for tx in tx_sender:
        if len(tx) > 0:
            amount_sent += tx[0]

    tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient']== participant] for block in blockchain]
    amount_received = 0
    for tx in tx_recipient:
        if len(tx) > 0:
            amount_received += tx[0]

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
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        return True
    return False

def mine_block():
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block) 
    reward_transaction = {
        'sender': 'MINING',
        'recipient': owner,
        'amount': MINING_REWARD
    } 
    copied_transaction
    open_transactions.append(reward_transaction)
    print(hashed_block)

    block = {'previous_hash': hashed_block, 'index': len(blockchain), 'transactions': open_transactions}
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
    return True

# add_transaction(get_transaction_value())

waiting_for_input = True

while waiting_for_input:
        print("Please Choose")
        print('1: Add a new transaction value')
        print('2: Mine a new block')
        print('3: output the blockchain blocks')
        print('3: output participants')
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
        elif user_choice == '3':
            print_blockchain_elements()
        elif user_choice == '4':
            print (participants)
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
        print(get_balance('Sagar'))
else:
    print('User Left.. Bye!👋')
