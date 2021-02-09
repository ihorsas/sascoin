import hashlib
import json
from flask import flash

from Crypto.Signature import *
from time import time


class Transaction(object):
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.time = time()
        self.hash = self.calculateHash()

    # TODO: need to be rewritten
    def signTransaction(self, key, senderKey):
        if self.hash != self.calculateHash():
            flash("Transaction tampered error")
            return False

        if str(key.publickey().export_key()) != str(senderKey.publickey().export_key()):
            flash("Transaction attempt to be signed from another wallet")
            return False

        self.signature = pkcs1_15.new(key)
        print("made signature!")
        return True

    def calculateHash(self):
        hashString = self.sender + self.receiver + str(self.amount) + str(self.time)
        hashEncoded = json.dumps(hashString, sort_keys=True).encode()
        return hashlib.sha256(hashEncoded).hexdigest()

    def isValidTransaction(self):
        if self.hash != self.calculateHash():
            flash("Transaction hash has been changed")
            return False
        if self.sender == self.receiver:
            flash("Sender value is the same as receiver")
            return False

        # Skip for nit
        # if not self.signature or len(self.signature) == 0:
        #     print("Error: No Signature!")
        #     return False
        return True

    # needs work!

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=5)

    @staticmethod
    def fromJSON(jsonObject):
        return json.loads(jsonObject)

    def __str__(self) -> str:
        return f'Sender: {self.sender}\n' \
               f'Receiver: {self.receiver}\n' \
               f'Amount: {self.amount}\n' \
               f'Time: {self.time}\n' \
               f'Hash: {self.hash}'
