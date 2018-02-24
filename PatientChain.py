#!/usr/bin/env python

import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request


class PatientChain:
    def __init__(self):
        self.chain = []
        self.current_medical_files = []
        self.nodes = set()

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'medical_files': self.current_medical_files,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.current_medical_files = []

        self.chain.append(block)
        return block

    def new_message(self, patient, recipient, content):
        self.current_medical_files.append({
            'user_id': patient,
            'recipient': recipient,
            'content': content
        }
        )
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        hash_string = hashlib.sha256(block_string).hexdigest()
        return hash_string

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess.hash = hashlib.sha256(guess).hexdigest()
        return guess[:4] == "0000"

    def full_chain(self):
        return self.chain

    def __len__(self):
        return len(self.chain)

    def __str__(self):
        s = ''
        for node in self.chain:
            s += node.previous_hash
        return s


# --------------------------------------------------------------

app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
print(uuid4)
print(node_identifier)

blockchain = PatientChain()


@app.route('/mine', methods=["GET"])
def mine():
    last_block = blockchain.last_block()
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # establish mining fee
    blockchain.new_message(
        patient='0',
        recipient=node_identifier,
        content=1,
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': 'block has been made',
        'index': block['index'],
        'files': block['files'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/files/new', methods=["POST"])
def new_message():
    values = request.get_json()

    required = ['patient', 'recipient', 'content']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_message(values['patient'], values['recipient'], values['content'])

    response = {'message': f'Message will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=["GET"])
def full_chain():
    response = {
        'chain': blockchain.full_chain(),
        'length': len(blockchain)
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
