import * as ecdsa from 'elliptic';
const ec = new ecdsa.ec('secp256k1');

const toHexString = (byteArray): string => {
    return Array.from(byteArray, (byte: any) => {
        return ('0' + (byte & 0xFF).toString(16)).slice(-2);
    }).join('');
};

const getCurrentTimestamp = (): number => Math.round(new Date().getTime() / 1000);

// valid address is a valid ecdsa public key in the 04 + X-coordinate + Y-coordinate format
const isValidAddress = (address: string): boolean => {
    if (address.length !== 130) {
        console.log(address);
        console.log('invalid public key length');
        return false;
    } else if (address.match('^[a-fA-F0-9]+$') === null) {
        console.log('public key must contain only hex characters');
        return false;
    } else if (!address.startsWith('04')) {
        console.log('public key must start with 04');
        return false;
    }
    return true;
};

/**
 *
 * @param hash - hash of block in hex
 * @param difficulty - amount 0 with which hash should be started
 */
const hashMatchesDifficulty = (hash: string, difficulty: number): boolean => {
    const requiredPrefix: string = '0'.repeat(difficulty);
    return hash.startsWith(requiredPrefix);
};

export {
    toHexString, isValidAddress, getCurrentTimestamp, hashMatchesDifficulty
}