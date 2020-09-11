#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A vendor matching Python webhook implemented using Flask."""
import hashlib
import hmac
from functools import wraps
from typing import List, Dict

import flask
from flask import request, jsonify
from werkzeug.exceptions import abort

from database.database import VendorDatabase

db = VendorDatabase()


app = flask.Flask(__name__)
# app.config["DEBUG"] = True

SECRET_KEY = "Your secret key stored in hook.config.secret"  # never store this in code


def hmac_signature_required(f):
    @wraps(f)
    def authorize_request(*args, **kwargs):
        """Verify the validity of the request coming from Rossum."""
        digest = hmac.new(SECRET_KEY.encode(), request.data, hashlib.sha1).hexdigest()
        try:
            prefix, signature = request.headers["X-Elis-Signature"].split("=")
        except ValueError:
            abort(401, "Incorrect header format")
        if not (prefix == "sha1" and hmac.compare_digest(signature, digest)):
            abort(401, "Authorization failed.")
        return f(*args, **kwargs)

    return authorize_request


def find_by_schema_id(annotation_tree: List[Dict], schema_id: str):
    """Find a node with a given id (as specified in schema) in the annotation tree."""
    for node in annotation_tree:
        if node["schema_id"] == schema_id:
            return node
        elif "children" in node:
            node = find_by_schema_id(node["children"], schema_id)
            if node is not None:
                return node
    return None


def match_vendor(annotation_tree: List[dict], updated_datapoints: List[int], action: str):
    """Vendor matching based on vendor name.

    How it works: vendor_name contains the name of the vendor to be matched.
    This pre-populates a vendor enum by (even partially) matching vendors
    in the database, to let the user make a final pick in case of ambiguity.
    It is possible to match also based on vendor's address or VAT ID. In the
    exported data, the matched value holds the vendor id (not the label).

    In case no vendor is matched, "---" is pre-populated in the enum
    and an error is displayed."""

    vendor = find_by_schema_id(annotation_tree, "vendor_match")
    vendor_vat_id = find_by_schema_id(annotation_tree, "vendor_vat_id")
    vendor_vat_id_norm = vendor_vat_id["content"]["value"].replace(" ", "")
    vendor_name = find_by_schema_id(annotation_tree, "sender_name")
    vendor_address = find_by_schema_id(annotation_tree, "sender_address")

    results = db.execute_and_fetchall(
        """
        SELECT taxid1, CONCAT(name, ', ', address1, ', ', city, ' (', id, ')') AS vendor FROM vendor_data
            WHERE (%s = '' OR (taxid1 IS NULL OR taxid1 = %s))
                AND (%s = '' OR UPPER(name) %% UPPER(%s))
                AND (%s = '' OR UPPER(CONCAT(address1, ' ', address2, ' ', address3, ' ', city, ' ', zipcode
                )) %% UPPER(%s))
        """,
        (
            vendor_vat_id_norm,
            vendor_vat_id_norm,
            vendor_name["content"]["value"],
            vendor_name["content"]["value"],
            vendor_address["content"]["value"],
            vendor_address["content"]["value"],
        ),
    )

    # Do not update the list unless we have a reason.
    if not (action == "initialize" or
            vendor_vat_id["id"] in updated_datapoints or
            vendor_name["id"] in updated_datapoints or
            vendor_address["id"] in updated_datapoints):
        return

    messages = []
    if results and (
        vendor_vat_id_norm
        or vendor_name["content"]["value"]
        or vendor_address["content"]["value"]
    ):
        vendor_options = [{"value": id, "label": vendor} for id, vendor in results]
    else:
        vendor_options = [{"value": "---", "label": "---"}]
        messages = [
            {"id": vendor["id"], "type": "error", "content": "Vendor not found."}
        ]
    operations = [
        {
            "op": "replace",
            "id": vendor["id"],
            "value": {
                "content": {"value": vendor_options[0]["value"]},
                "options": vendor_options,
                "validation_sources": ["connector"],
            },
        }
    ]
    return messages, operations


@app.route("/vendor_matching", methods=["POST"])
@hmac_signature_required
def vendor_matching():
    """Validate vendor name."""
    annotation_tree = request.json["annotation"]["content"]
    updated_datapoints = request.json["updated_datapoints"]
    action = request.json["action"]
    messages, operations = match_vendor(annotation_tree, updated_datapoints, action)
    return jsonify({"messages": messages, "operations": operations})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
