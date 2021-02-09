from src.block import Block
from src.transaction import Transaction

from Crypto.PublicKey import RSA
from time import time
from urllib.parse import urlparse
import requests
from flask import request, flash


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.addTheFirstBlock()
        self.pendingTransactions = []
        self.difficulty = 3
        self.minerRewards = 2
        self.blockSize = 10
        self.nodes = set()

    def getLastBlock(self):
        return self.chain[-1]

    def addBlock(self, block):
        if (len(self.chain) > 0):
            block.prev = self.getLastBlock().hash
        else:
            block.prev = 'none'
        self.chain.append(block)

    def addTheFirstBlock(self):
        self.chain.append(Block([], time(), 1))

    def addTransaction(self, sender, receiver, amount, keyString, senderKey):
        keyByte = keyString.encode("ASCII")
        senderKeyByte = senderKey.encode("ASCII")
        key = RSA.import_key(keyByte)
        senderKey = RSA.import_key(senderKeyByte)

        if not sender or not receiver or not amount:
            flash("Transaction has empty sender, receiver or amount")
            return False
        transaction = Transaction(sender, receiver, amount)
        transaction.signTransaction(key, senderKey)
        if not transaction.isValidTransaction():
            return False
        self.pendingTransactions.append(transaction)
        return True

    def addTransaction(self, sender, receiver, amount):
        if not sender or not receiver or not amount:
            flash("Transaction has empty sender, receiver or amount")
            return False
        if amount <= 0:
            flash("Amount should be >= 0")
            return False
        transaction = Transaction(sender, receiver, amount)
        if not transaction.isValidTransaction():
            return False
        self.pendingTransactions.append(transaction)
        return True

    def minePendingTransactions(self, miner):

        lenPendingTransaction = len(self.pendingTransactions)
        if lenPendingTransaction < 1:
            flash("Not enough transactions to mine! (Must be non-nullable size of pending transactions)")
            return False
        else:
            for i in range(0, lenPendingTransaction, self.blockSize):

                # divide pending transactions by same blockSizes
                end = i + self.blockSize
                if i >= lenPendingTransaction:
                    end = lenPendingTransaction
                transactionSlice = self.pendingTransactions[i:end]

                # adding new block to chain
                newBlock = Block(transactionSlice, time(), len(self.chain))
                newBlock.prev = self.getLastBlock().hash
                newBlock.mineBlock(self.difficulty)
                self.chain.append(newBlock)
            payMiner = Transaction("Miner Rewards", miner, self.minerRewards)
            self.pendingTransactions = [payMiner]
            return True

    def generateKeys(self):
        key = RSA.generate(2048)
        private_key = key.export_key()
        file_out = open("private.pem", "wb")
        file_out.write(private_key)

        public_key = key.publickey().export_key()
        file_out = open("receiver.pem", "wb")
        file_out.write(public_key)

        print(public_key.decode('ASCII'))
        return key.publickey().export_key().decode('ASCII')

    def register_node(self, address):
        parsedUrl = urlparse(address)
        self.nodes.add(parsedUrl.netloc)

    # it's bad implementation
    # should be changed as soon as possible
    def resolveConflicts(self):
        neighbors = self.nodes
        newChain = None

        maxLength = len(self.chain)
        print(f'Going through nodes: {neighbors}')
        for node in neighbors:
            if node in request.url:
                continue
            print(f'Making request for node: {node}')
            response = requests.get(f'http://{node}/chain')
            print(f'Get response: {response}')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                print(f'Length: {length}')
                print(f'Chain: {chain}')
                if length > maxLength and self.isValidChain():
                    maxLength = length
                    newChain = chain

        print('Finished going through nodes')
        if newChain:
            print('Creating new chain from json')
            self.chain = self.chainJSONdecode(newChain)
            print(self.chain)
            return True

        return False

    # going through chain to verify if chain is not broken
    def isValidChain(self):
        print('Starting verifying valid chain')
        for i in range(1, len(self.chain)):
            b1 = self.chain[i - 1]
            b2 = self.chain[i]
            print(f'Last block: {b2}')
            print(f'Last block: {b2}')
            if not b2.areTransactionsValid():
                return False

            if b2.hash != b2.calculateHash():
                flash("Block hash was changed")
                return False

            if b2.prev != b1.hash:
                flash("hash of previous block was changed")
                return False
        return True

    def chainJSONencode(self):
        blockArrJSON = []
        for block in self.chain:
            print(f'current block: {block}')
            blockJSON = block.toJSON()
            blockArrJSON.append(blockJSON)
        return blockArrJSON

    @staticmethod
    def chainJSONdecode(chainJSON):
        chain = []
        for blockJSON in chainJSON:
            block = Block.fromJSON(blockJSON)
            chain.append(block)
        return chain
