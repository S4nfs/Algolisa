


#        ____                                                                           
#     //   ) )  //                   //__//             /                              
#    //___/ /  //  ___      ___     / ___      ___     / __      ___     ( )   __    
#   / __  (   // //   ) ) //   ) ) //\ \     //   ) ) //   ) ) //   ) ) / / //   ) ) 
#  //    ) ) // //   / / //       //  \ \   //       //   / / //   / / / / //   / /  
# //____/ / // ((___/ / ((____   //    \ \ ((____   //   / / ((___( ( / / //   / /   

blockchain = []


def get_last_blockchain_value():
    """ Returns the last value of the current bockchain """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]

def add_transaction(transaction_amt, last_transaction = [1]):
    """ Append new value and last blockchain value to the block
    
    Arguments:
        :transaction_amt: the amount that shoul be added
        :last_transaction: the last blockchain transaction (default [1])
    """
    if last_transaction == None:
        last_transaction = [1]

    blockchain.append([last_transaction, transaction_amt])

def get_transaction_value():
    """
    Returns the input of the users (a new transaction amount) as a float
    """
    return float(input('Your transaction amount:'))


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
            tx_amount = get_transaction_value()
            add_transaction(tx_amount, get_last_blockchain_value())
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
