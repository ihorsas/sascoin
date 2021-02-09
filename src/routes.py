from flask import Flask, jsonify, request, get_flashed_messages, flash
from src.blockchain import Blockchain
import random

from uuid import uuid4

# Instantiate the Node
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['SECRET_KEY'] = f'Secret key for session {random.random()}'

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchainObj = Blockchain()


# mine endpoint should be used with argument miner,
# which should have value of miner wallet_id
@app.route('/mine', methods=['GET'])
def mine():
    # return jsonify({'message': f'Method is working with args: {request.args.get("miner")}'}), 200
    if request.args.get('miner') is None:
        return jsonify({'message': f'Miner argument is empty'}), 400
    miner = request.args.get('miner', None)

    if len(blockchainObj.pendingTransactions) <= 1:
        return jsonify({'message': f'Not enough pending transactions to mine! (Must be > 1)'}), 201

    if blockchainObj.minePendingTransactions(miner):
        return jsonify(
            {'message': f'Block Mined! Your mining reward has now been added to the pending transactions!'}), 200
    return jsonify({
        'message': get_flashed_messages()
    }), 400


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'receiver', 'amount', ]
    if not all(k in values for k in required):
        return jsonify({'message': 'Missing values'}), 400

    if not blockchainObj.addTransaction(values['sender'], values['receiver'], values['amount']):
        return jsonify({'message': get_flashed_messages()}), 400

    response = {'message': f'Transaction will be added to pending transactions'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchainObj.chainJSONencode(),
        'length': len(blockchainObj.chain),
    }
    return jsonify(response), 200


# blockchainObj DECENTRALIZED NODES
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return jsonify({'message': 'Error: Please supply a valid list of nodes'}), 400

    for node in nodes:
        blockchainObj.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchainObj.nodes),
    }
    return jsonify(response), 200


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchainObj.resolveConflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchainObj.chainJSONencode()
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchainObj.chainJSONencode()
        }

    return jsonify(response), 200
