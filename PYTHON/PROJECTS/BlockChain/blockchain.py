


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
blockchain = []
open_transactions = []
owner = 'Sagar'

def get_last_blockchain_value():
    """ Returns the last value of the current bockchain """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]

def add_transaction( recipient, sender=owner, amount = 1.0):
    """ Append new value and last blockchain value to the block
    
    Arguments:
        :sender: the sender of the coins
        :recipient: the receiver of the coins
        :amount: transaction amount
    """
    
    transaction = {'sender': sender, 'recipient': recipient, 'amount': amount} #dictionary to store the transaction details
    open_transactions.append(transaction)

def mine_block():
    pass

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
    is_valid = True
    for block_index in range(len(blockchain)):
        if block_index == 0:
            continue
        elif blockchain[block_index][0] == blockchain[block_index - 1]:
            is_valid = True
        else:
            is_valid  = False
            break
    return is_valid

# add_transaction(get_transaction_value())

waiting_for_input = True

while waiting_for_input:
        print("Please Choose")
        print('1: Add a new transaction value')
        print('2: output the blockchain blocks')
        print('h: Manipulate the chain')
        print('q: Quit')
        user_choice = get_user_choice()

        if user_choice == '1':
            tx_data = get_transaction_value()
            recipient, amount = tx_data
            add_transaction(recipient, amount=amount)
            print(open_transactions)
        elif user_choice == '2':
            print_blockchain_elements()
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
else:
    print('User Left.. Bye!👋')
