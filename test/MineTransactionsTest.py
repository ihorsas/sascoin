from src.Blockchain import Blockchain
from src.Transaction import Transaction
import pprint

pp = pprint.PrettyPrinter(indent=4)

blockchain = Blockchain()
transaction = Transaction('Mykhailo Tsalan', 'Ihor Sas', 100)

blockchain.pendingTransactions.append(transaction)

blockchain.minePendingTransactions('Bohdan Klymenko')

print('Chain after mining: ')
pp.pprint(blockchain.chainJSONencode())
print('Length of chain: ', len(blockchain.chain))

print('First pending transaction after mining:', blockchain.pendingTransactions[0])
