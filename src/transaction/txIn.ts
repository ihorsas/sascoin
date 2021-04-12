import * as _ from "lodash";
import * as ecdsa from 'elliptic';
import {findUnspentTxOut, UnspentTxOut} from "./unspentTxOut";
import {Transaction} from "./transaction";

const ec = new ecdsa.ec('secp256k1');

class TxIn {
    public txOutId: string;
    public txOutIndex: number;
    public signature: string;

    // toString() {
    //     return "TxIn {" +
    //         "\n\ttxOutId: " + this.txOutId +
    //         "\n\ttxOutIndex: " + this.txOutIndex +
    //         "\n\tsignature: " + this.signature +
    //         "\n}";
    // }
}

const getTxInAmount = (txIn: TxIn, aUnspentTxOuts: UnspentTxOut[]): number => {
    return findUnspentTxOut(txIn.txOutId, txIn.txOutIndex, aUnspentTxOuts).amount;
};


const hasDuplicates = (txIns: TxIn[]): boolean => {
    const groups = _.countBy(txIns, (txIn: TxIn) => txIn.txOutId + txIn.txOutIndex);
    return _(groups)
        .map((value, key) => {
            if (value > 1) {
                console.log('duplicate txIn: ' + key);
                return true;
            } else {
                return false;
            }
        })
        .includes(true);
};

const hasTxIn = (txIn: TxIn, unspentTxOuts: UnspentTxOut[]): boolean => {
    const foundTxIn = unspentTxOuts.find((uTxO: UnspentTxOut) => {
        return uTxO.txOutId === txIn.txOutId && uTxO.txOutIndex === txIn.txOutIndex;
    });
    return foundTxIn !== undefined;
};


const validateTxIn = (txIn: TxIn, transaction: Transaction, aUnspentTxOuts: UnspentTxOut[]): boolean => {
    const referencedUTxOut: UnspentTxOut =
        aUnspentTxOuts.find((uTxO) => uTxO.txOutId === txIn.txOutId && uTxO.txOutIndex === txIn.txOutIndex);
    if (referencedUTxOut == null) {
        console.log('referenced txOut not found: ' + JSON.stringify(txIn));
        return false;
    }
    const address = referencedUTxOut.address;

    const key = ec.keyFromPublic(address, 'hex');
    const validSignature: boolean = key.verify(transaction.id, txIn.signature);
    if (!validSignature) {
        console.log('invalid txIn signature: %s txId: %s address: %s', txIn.signature, transaction.id, referencedUTxOut.address);
        return false;
    }
    return true;
};

const isValidTxInStructure = (txIn: TxIn): boolean => {
    if (txIn == null) {
        console.log('txIn is null');
        return false;
    } else if (typeof txIn.signature !== 'string') {
        console.log('invalid signature type in txIn');
        return false;
    } else if (typeof txIn.txOutId !== 'string') {
        console.log('invalid txOutId type in txIn');
        return false;
    } else if (typeof txIn.txOutIndex !== 'number') {
        console.log('invalid txOutIndex type in txIn');
        return false;
    } else {
        return true;
    }
};

export {
    TxIn, hasDuplicates, hasTxIn, validateTxIn, getTxInAmount, isValidTxInStructure
}