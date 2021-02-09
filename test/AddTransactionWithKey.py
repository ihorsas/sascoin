from src.blockchain import Blockchain
import pprint


pp = pprint.PrettyPrinter(indent=4)

blockchain = Blockchain()

key = blockchain.generateKeys()

print(key + '\n')

isTransactionAdded = blockchain.addTransaction('Mykhailo Tsalan', 'Ihor Sas', 100, key, key)

assert isTransactionAdded is True
