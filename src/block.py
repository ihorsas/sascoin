import hashlib
import json

class Block(object):
    def __init__(self, transactions, time, index):
        self.index = index
        self.transactions = transactions
        self.time = time
        self.nonce = 0 # Times of mining until hash starting to difficulty
        self.prev = ''  # Hash of Previous Block
        self.hash = self.calculateHash()  # Hash of Block

    def calculateHash(self):
        hashTransactions = ''
        for transaction in self.transactions:
            hashTransactions += transaction.hash
        hashString = str(self.time) + hashTransactions + self.prev + str(self.index) + str(self.nonce)
        hashEncoded = json.dumps(hashString, sort_keys=True).encode()
        return hashlib.sha256(hashEncoded).hexdigest()

    def mineBlock(self, difficulty):
        arr = range(0, difficulty)

        # compute until the beginning of the hash = 0123..difficulty
        arrStr = map(str, arr)
        hashPuzzle = ''.join(arrStr)
        # print(len(hashPuzzle))
        while self.hash[0:difficulty] != hashPuzzle:
            self.nonce += 1
            self.hash = self.calculateHash()
            # print(f'Nonce:{self.nonce}')
            # print(f'Hash Attempt:{self.hash}')
            # print(f'Acceptable hash:{hashPuzzle}...\n')
            # time.sleep(1)

        print(len(hashPuzzle))
        print(self.hash[0:difficulty])
        print("Block Mined!")
        return True

    def areTransactionsValid(self):
        print('Verifying transactions')
        for i in range(0, len(self.transactions)):
            if not self.transactions[i].isValidTransaction():
                return False
            return True

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=5)

    @staticmethod
    def fromJSON(jsonObject):
        return json.loads(jsonObject)