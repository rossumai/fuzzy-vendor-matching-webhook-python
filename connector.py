#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A vendor matching Python connector implemented using Flask."""

from functools import wraps
import logging

import flask
from flask import request, jsonify

from database.database import DEDatabase
import config

db = DEDatabase()


app = flask.Flask(__name__)
# app.config["DEBUG"] = True


def secret_key_required(f):
    """API method wrapper that checks the secret key in authorization header.

    :param f: Function on which the decorator will be used.
    :return: authorize_request function.
    """

    def authorize_user():
        """Checks the secret key against configured key.

        Returns whether a valid authorization has been obtained.
        """
        header = request.headers.get('Authorization')

        if not header:
            return False

        parts = header.split()

        if len(parts) != 2 or parts[0] != 'secret_key':
            logging.error('Invalid Authorization header: %s' % header)
            raise ValueError('Invalid Authorization header')

        secret_key = parts[1]
        if secret_key == config.CONNECTOR_AUTH_KEY['CONNECTOR_AUTH_KEY']:
            return True
        else:
            logging.error('Invalid Authorization secret key: %s' % secret_key)
            raise ValueError('Invalid Authorization secret key')

    @wraps(f)
    def authorize_request(*args, **kwargs):
        """Checks whether authorization key is present."""
        try:
            if not authorize_user():
                logging.error('No Authorization secret key')
                return jsonify({'error': 'authorization key missing'}), 403
        except ValueError as e:
            logging.error('authorize_user ValueError %s' % str(e))
            return jsonify({'error': str(e)}), 403
        return f(*args, **kwargs)

    return authorize_request


def find_by_schema_id(annotation_tree, schema_id):
    """Find a node with a given id (as specified in schema) in the annotation tree.

    :param annotation_tree: List of schema nodes.
    :param schema_id: Node id within the annotation tree.
    :return: value of schema_id.
    """
    for node in annotation_tree:
        if node['schema_id'] == schema_id:
            return node
        elif 'children' in node:
            node = find_by_schema_id(node['children'], schema_id)
            if node is not None:
                return node
    return None


def match_supplier(messages, updated_datapoints, annotation_tree, is_initial, previously_updated):
    """Supplier matching based on vendor name.

    How it works: vendor_name contains the name of the supplier to be matched.
    This pre-populates a vendor enum by (even partially) matching suppliers
    in our "database", to let the user make a final pick in case of ambiguity.
    It is possible to match also based on vendor's address or VAT ID. Vendor
    match enum maps the name to a vendor id that is part of the exported data.

    In case no vendor is matched, "---" is pre-populated in the enum
    and an error is displayed.

    :param messages: List for error messages.
    :param updated_datapoints: List of updated datapoints in the schema.
    :param annotation_tree: List of schema nodes.
    :param is_initial: Information on the novelty of edited invoice.
    :param previously_updated: List of ids of previously updated objects.
    """

    vendor = find_by_schema_id(annotation_tree, 'vendor_match')
    vendor_vat_id = find_by_schema_id(annotation_tree, 'vendor_vat_id')
    vendor_vat_id_norm = vendor_vat_id['value'].replace(' ', '')
    vendor_name = find_by_schema_id(annotation_tree, 'sender_name')
    vendor_address = find_by_schema_id(annotation_tree, 'sender_address')

    # Do not update the list unless we have a reason.
    if not (is_initial or
            vendor_vat_id['id'] in previously_updated or
            vendor_name['id'] in previously_updated or
            vendor_address['id'] in previously_updated):
        return

    results = db.execute_and_fetchall("""
        SELECT taxid1, CONCAT(name, ', ', address1, ', ', city, ' (', id, ')') AS vendor FROM vendor_data 
            WHERE (%s = '' OR (taxid1 IS NULL OR taxid1 = %s))
                AND (%s = '' OR UPPER(name) %% UPPER(%s))
                AND (%s = '' OR UPPER(CONCAT(address1, ' ', address2, ' ', address3, ' ', city, ' ', zipcode
                )) %% UPPER(%s))
        """, (vendor_vat_id_norm, vendor_vat_id_norm,
              vendor_name['value'], vendor_name['value'],
              vendor_address['value'], vendor_address['value']))

    if results and (vendor_vat_id_norm or vendor_name['value'] or vendor_address['value']):
        vendor_options = [{'value': id, 'label': vendor} for id, vendor in results]
    else:
        vendor_options = [{'value': '---', 'label': '---'}]
        messages.append({'id': vendor['id'], 'type': 'error', 'content': 'Vendor not found.'})
    updated_datapoints.append(
        {'id': vendor['id'], 'value': vendor_options[0]['value'], 'options': vendor_options}
    )


@app.route('/validate', methods=['POST'])
@secret_key_required
def api_validate():
    """Validate vendor name.

    :return: JSON response containing error message and updated datapoints.
    """
    annotation_tree = request.json['content']
    previously_updated = request.json['meta']['updated_datapoint_ids']
    is_initial = request.args.get('initial', 'false').lower() == 'true'
    messages = []
    updated_datapoints = []

    match_supplier(messages, updated_datapoints, annotation_tree, is_initial, previously_updated)

    return jsonify({'messages': messages, 'updated_datapoints': updated_datapoints})


@app.route('/save', methods=['POST'])
@secret_key_required
def api_save():
    # We do nothing explicit on invoice export - yet.
    return jsonify({})


@app.route('/healthz', methods=['GET'])
def api_healthz():
    # This is not required by Elis, but useful when running the connector
    # in a managed environment (e.g. Kubernetes).
    return '', 204


app.run(host='0.0.0.0', port=5000)
