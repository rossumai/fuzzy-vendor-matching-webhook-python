import json

import pytest

from tests.conftest import create_annotation_tree, WEBHOOK_URL
from tests.conftest import create_hashed_signature


@pytest.mark.usefixtures("fill_vendor_data_table")
class TestValidate:
    def test_success_sender_name(self, client):
        annotation_tree = create_annotation_tree(sender_name="Bernhard")
        webhook_schema = {
            "action": "initialize",
            "updated_datapoints": [],
            "hook": WEBHOOK_URL,
            "annotation": {"content": annotation_tree},
        }
        request_body = json.dumps(webhook_schema).encode("utf-8")

        annot_tree = client.post(
            data=request_body,
            path="/vendor_matching",
            headers={
                "Content-Type": "application/json",
                "X-Elis-Signature": f"sha1={create_hashed_signature(request_body)}",  # noqa
            },
        )

        assert annot_tree.status_code == 200
        assert annot_tree.json == {
            "messages": [],
            "operations": [
                {
                    "id": "190004",
                    "op": "replace",
                    "value": {
                        "content": {"value": "DE757038244"},
                        "options": [
                            {
                                "label": "Bernhard Group, Brandenburgische Strasse 55, Knittelsheim (2416)",
                                "value": "DE757038244",
                            }
                        ],
                        "validation_sources": ["connector"],
                    },
                }
            ],
        }

    def test_success_sender_vat_id(self, client):
        annotation_tree = create_annotation_tree(vendor_vat_id="DE758402667")
        webhook_schema = {
            "action": "initialize",
            "updated_datapoints": [],
            "hook": WEBHOOK_URL,
            "annotation": {"content": annotation_tree},
        }
        request_body = json.dumps(webhook_schema).encode("utf-8")

        annot_tree = client.post(
            data=request_body,
            path="/vendor_matching",
            headers={
                "Content-Type": "application/json",
                "X-Elis-Signature": f"sha1={create_hashed_signature(request_body)}",  # noqa
            },
        )

        assert annot_tree.status_code == 200
        assert annot_tree.json == {
            "messages": [],
            "operations": [
                {
                    "id": "190004",
                    "op": "replace",
                    "value": {
                        "content": {"value": "DE758402667"},
                        "options": [
                            {
                                "label": "Bosco Ltd, Flotowstr. 65, " "Aschersleben (3562)",
                                "value": "DE758402667",
                            }
                        ],
                        "validation_sources": ["connector"],
                    },
                }
            ],
        }

    def test_success_sender_address(self, client):
        annotation_tree = create_annotation_tree(sender_address="Flotowstr. 65")
        webhook_schema = {
            "action": "initialize",
            "updated_datapoints": [],
            "hook": WEBHOOK_URL,
            "annotation": {"content": annotation_tree},
        }
        request_body = json.dumps(webhook_schema).encode("utf-8")

        annot_tree = client.post(
            data=request_body,
            path="/vendor_matching",
            headers={
                "Content-Type": "application/json",
                "X-Elis-Signature": f"sha1={create_hashed_signature(request_body)}",  # noqa
            },
        )

        assert annot_tree.status_code == 200
        assert annot_tree.json == {
            "messages": [],
            "operations": [
                {
                    "id": "190004",
                    "op": "replace",
                    "value": {
                        "content": {"value": "DE758402667"},
                        "options": [
                            {
                                "label": "Bosco Ltd, Flotowstr. 65, " "Aschersleben (3562)",
                                "value": "DE758402667",
                            }
                        ],
                        "validation_sources": ["connector"],
                    },
                }
            ],
        }

    def test_vendor_not_found(self, client):
        webhook_schema = {
            "action": "initialize",
            "updated_datapoints": [],
            "hook": WEBHOOK_URL,
            "annotation": {"content": create_annotation_tree(sender_name="NotExist")},  # noqa
        }
        request_body = json.dumps(webhook_schema).encode("utf-8")

        annot_tree = client.post(
            data=request_body,
            path="/vendor_matching",
            headers={
                "Content-Type": "application/json",
                "X-Elis-Signature": f"sha1={create_hashed_signature(request_body)}",  # noqa
            },
        )

        assert annot_tree.status_code == 200
        assert annot_tree.json == {
            "messages": [
                {"content": "Vendor not found.", "id": "190004", "type": "error",}  # noqa
            ],
            "operations": [
                {
                    "id": "190004",
                    "op": "replace",
                    "value": {
                        "content": {"value": "---"},
                        "options": [{"label": "---", "value": "---"}],
                        "validation_sources": ["connector"],
                    },
                }
            ],
        }
