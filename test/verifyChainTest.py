from src.blockchain import Blockchain
from src.transaction import Transaction
import pprint

pp = pprint.PrettyPrinter(indent=4)

blockchain = Blockchain()
transaction = Transaction('Mykhailo Tsalan', 'Ihor Sas', 100)

blockchain.pendingTransactions.append(transaction)
blockchain.pendingTransactions.append(transaction)

blockchain.minePendingTransactions('Bohdan Klymenko')
blockchain.pendingTransactions.append(transaction)
blockchain.pendingTransactions.append(transaction)

blockchain.minePendingTransactions('Bohdan Klymenko')

assert blockchain.isValidChain() is True
