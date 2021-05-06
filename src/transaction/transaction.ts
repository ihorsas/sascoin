import * as CryptoJS from "crypto-js";
import * as _ from "lodash";
import * as ecdsa from 'elliptic';
import config from '../config';
import {findUnspentTxOut, UnspentTxOut, updateUnspentTxOuts} from "./unspentTxOut";
import {toHexString} from "../util/commonUtil";
import {getTxInAmount, hasDuplicates, isValidTxInStructure, TxIn, validateTxIn} from "./txIn";
import {isValidTxOutStructure, TxOut} from "./txOut";
import {getPublicKey} from "../wallet/wallet";

const ec = new ecdsa.ec('secp256k1');

class Transaction {

    public id: string;

    public txIns: TxIn[];
    public txOuts: TxOut[];

    // toString() {
    //     return "Transaction {" +
    //         "\n\ttxIns: " + this.txIns +
    //         "\n\ttxOuts: " + this.txOuts +
    //         "\n}";
    // }
}

const getTransactionId = (transaction: Transaction): string => {
    const txInContent: string = transaction.txIns
        .map((txIn: TxIn) => txIn.txOutId + txIn.txOutIndex)
        .reduce((a, b) => a + b, '');

    const txOutContent: string = transaction.txOuts
        .map((txOut: TxOut) => txOut.address + txOut.amount)
        .reduce((a, b) => a + b, '');

    return CryptoJS.SHA256(txInContent + txOutContent).toString();
};

const getCoinbaseTransaction = (address: string, blockIndex: number): Transaction => {
    const t = new Transaction();
    const txIn: TxIn = new TxIn();
    txIn.signature = '';
    txIn.txOutId = '';
    txIn.txOutIndex = blockIndex;

    t.txIns = [txIn];
    t.txOuts = [new TxOut(address, config.COINBASE_AMOUNT)];
    t.id = getTransactionId(t);
    return t;
};


const signTxIn = (transaction: Transaction, txInIndex: number,
                  privateKey: string, aUnspentTxOuts: UnspentTxOut[]): string => {
    const txIn: TxIn = transaction.txIns[txInIndex];

    const dataToSign = transaction.id;
    const referencedUnspentTxOut: UnspentTxOut = findUnspentTxOut(txIn.txOutId, txIn.txOutIndex, aUnspentTxOuts);
    if (referencedUnspentTxOut == null) {
        console.log('could not find referenced txOut');
        throw Error();
    }
    const referencedAddress = referencedUnspentTxOut.address;

    if (getPublicKey(privateKey) !== referencedAddress) {
        console.log('trying to sign an input with private' +
            ' key that does not match the address that is referenced in txIn');
        throw Error();
    }
    const key = ec.keyFromPrivate(privateKey, 'hex');
    const signature: string = toHexString(key.sign(dataToSign).toDER());

    return signature;
};

const processTransactions = (aTransactions: Transaction[], aUnspentTxOuts: UnspentTxOut[], blockIndex: number) => {
    console.log('\nprocess transactions: ' + aTransactions +
        "\n with unspend transactions out: " + aUnspentTxOuts +
        "\n with blockIndex" + blockIndex);
    if (!validateTransactions(aTransactions, aUnspentTxOuts, blockIndex)) {
        console.log('invalid block transactions');
        return null;
    }
    return updateUnspentTxOuts(aTransactions, aUnspentTxOuts);
};

const validateTransaction = (transaction: Transaction, aUnspentTxOuts: UnspentTxOut[]): boolean => {
    if (!isValidTransactionStructure(transaction)) {
        return false;
    }

    if (getTransactionId(transaction) !== transaction.id) {
        console.log('invalid tx id: ' + transaction.id);
        return false;
    }
    const hasValidTxIns: boolean = transaction.txIns
        .map((txIn) => validateTxIn(txIn, transaction, aUnspentTxOuts))
        .reduce((a, b) => a && b, true);

    if (!hasValidTxIns) {
        console.log('some of the txIns are invalid in tx: ' + transaction.id);
        return false;
    }

    const totalTxInValues: number = transaction.txIns
        .map((txIn) => getTxInAmount(txIn, aUnspentTxOuts))
        .reduce((a, b) => (a + b), 0);

    const totalTxOutValues: number = transaction.txOuts
        .map((txOut) => txOut.amount)
        .reduce((a, b) => (a + b), 0);

    if (totalTxOutValues !== totalTxInValues) {
        console.log('totalTxOutValues !== totalTxInValues in tx: ' + transaction.id);
        return false;
    }

    return true;
};

const validateTransactions = (aTransactions: Transaction[], aUnspentTxOuts: UnspentTxOut[], blockIndex: number): boolean => {
    const coinbaseTx = aTransactions[0];
    if (!validateCoinbaseTx(coinbaseTx, blockIndex)) {
        console.log('invalid coinbase transaction: ' + JSON.stringify(coinbaseTx));
        return false;
    }

    // check for duplicate txIns. Each txIn can be included only once
    const txIns: TxIn[] = _(aTransactions)
        .map((tx) => tx.txIns)
        .flatten()
        .value();

    if (hasDuplicates(txIns)) {
        return false;
    }

    // all but coinbase transactions
    const normalTransactions: Transaction[] = aTransactions.slice(1);
    return normalTransactions.map((tx) => validateTransaction(tx, aUnspentTxOuts))
        .reduce((a, b) => (a && b), true);

};

const validateCoinbaseTx = (transaction: Transaction, blockIndex: number): boolean => {
    if (transaction == null) {
        console.log('the first transaction in the block must be coinbase transaction');
        return false;
    }
    if (getTransactionId(transaction) !== transaction.id) {
        console.log('invalid coinbase tx id: ' + transaction.id);
        console.log('should be: ' + getTransactionId(transaction));
        return false;
    }
    if (transaction.txIns.length !== 1) {
        console.log('one txIn must be specified in the coinbase transaction');
        return;
    }
    if (transaction.txIns[0].txOutIndex !== blockIndex) {
        console.log('the txIn signature in coinbase tx must be the block height');
        return false;
    }
    if (transaction.txOuts.length !== 1) {
        console.log('invalid number of txOuts in coinbase transaction');
        return false;
    }
    if (transaction.txOuts[0].amount !== config.COINBASE_AMOUNT) {
        console.log('invalid coinbase amount in coinbase transaction');
        return false;
    }
    return true;
};

const isValidTransactionStructure = (transaction: Transaction) => {
    if (typeof transaction.id !== 'string') {
        console.log('transactionId missing');
        return false;
    }
    if (!(transaction.txIns instanceof Array)) {
        console.log('invalid txIns type in transaction');
        return false;
    }
    if (!transaction.txIns
        .map(isValidTxInStructure)
        .reduce((a, b) => (a && b), true)) {
        return false;
    }

    if (!(transaction.txOuts instanceof Array)) {
        console.log('invalid txIns type in transaction');
        return false;
    }

    if (!transaction.txOuts
        .map(isValidTxOutStructure)
        .reduce((a, b) => (a && b), true)) {
        return false;
    }
    return true;
};

export {
    processTransactions, signTxIn, getTransactionId, validateTransaction, getCoinbaseTransaction, Transaction
}