from src.Block import Block
from src.Transaction import Transaction

from Crypto.PublicKey import RSA
from time import time


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.addTheFirstBlock()

        self.pendingTransactions = []
        self.difficulty = 3
        self.minerRewards = 2
        self.blockSize = 10

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
            print("Error: Transaction has empty sender, receiver or amount")
            return False

        transaction = Transaction(sender, receiver, amount)
        transaction.signTransaction(key, senderKey)

        if not transaction.isValidTransaction():
            return False

        self.pendingTransactions.append(transaction)
        return True

    def minePendingTransactions(self, miner):

        lenPendingTransaction = len(self.pendingTransactions)
        if lenPendingTransaction < 1:
            print("Not enough transactions to mine! (Must be non-nullable size of pending transactions)")
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
            print("Mining Transactions Succeeded!")
            payMiner = Transaction("Miner Rewards", miner, self.minerRewards)
            self.pendingTransactions = [payMiner]

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

    def chainJSONencode(self):
        blockArrJSON = []
        for block in self.chain:
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
