import {isValidAddress} from "../util/commonUtil";

class TxOut {
    public address: string;
    public amount: number;

    constructor(address: string, amount: number) {
        this.address = address;
        this.amount = amount;
    }

    // toString() {
    //     return "TxOut {" +
    //         "\n\taddress: " + this.address +
    //         "\n\tamount: " + this.amount +
    //         "\n}";
    // }
}

const isValidTxOutStructure = (txOut: TxOut): boolean => {
    if (txOut == null) {
        console.log('txOut is null');
        return false;
    } else if (typeof txOut.address !== 'string') {
        console.log('invalid address type in txOut');
        return false;
    } else if (!isValidAddress(txOut.address)) {
        console.log('invalid TxOut address');
        return false;
    } else if (typeof txOut.amount !== 'number') {
        console.log('invalid amount type in txOut');
        return false;
    } else if (txOut.amount <= 0) {
        console.log('invalid txOut amount');
        return false;
    } else {
        return true;
    }
};

export {
    TxOut, isValidTxOutStructure
}