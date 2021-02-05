from src.Block import Block
from src.Blockchain import Blockchain
from time import time
import pprint

pp = pprint.PrettyPrinter(indent=4)

blockchain = Blockchain()
transactions = []

block = Block(transactions, time(), 0)
blockchain.addBlock(block)

block = Block(transactions, time(), 1)
blockchain.addBlock(block)

block = Block(transactions, time(), 2)
blockchain.addBlock(block)

blockchainJSON = blockchain.chainJSONencode()
blockchainDecoded = blockchain.chainJSONdecode(blockchainJSON)
print('Encoded blockchain:')
pp.pprint(blockchainJSON)
print('Length: %s', len(blockchain.chain))

print('\n\nDecoded blockchain:')
pp.pprint(blockchainDecoded)
print('Decoded blockchain length: %s', len(blockchainDecoded))
