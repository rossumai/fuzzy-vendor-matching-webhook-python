# Example Rossum Vendor Matching Webhook

The webhook matches extracted vendor name, address and VAT ID against a vendor database.
Any of these data is sufficient for the right vendor match.

![Vendor Matching Webhook](vendor_matching_webhook.gif)

You can find more information about webhooks at our [Developer Hub](https://developers.rossum.ai/docs/how-to-use-webhooks).
To set the webhook up:

  * `sudo apt install python3-pip` and `pip3 install -r requirements.txt`
  * The access credentials for the PostgreSQL database are stored in `config.py` and `~/.pgpass` file.

You can use [elisctl](https://github.com/rossumai/elisctl) tool to configure a Rossum queue to use the webhook.

Create the webhook first:

```
	 elisctl webhook create "Python Sample Webhook" --active true -e annotation_content.initialize -e annotation_content.user_update --config-url https://yourremoteurl.com/vendor_matching -q QUEUE_ID --config-secret YOUR_SECRET_HERE
```

where:
  * YOUR_SECRET_HERE = secret key that Rossum uses to create a hash signature with each payload. You will validate
  this secret in the webhook (within the hmac_signature_required() function in `webhook.py`) to check that the request
  was sent by Rossum.
 
To configure the schema for webhook to work:
```
	elisctl queue change SCHEMA_ID -s example_schema.json
```

where:
  * SCHEMA_ID = id of the schema that the webhook should be run on
  * example_schema.json = example schema that is set up to work with webhook. Can be customized based on your needs.

You can also configure the webhook via UI or using our [API](https://api.elis.rossum.ai/docs/#webhook-extension).

For more information on working with elisctl and its download see
<a href="https://github.com/rossumai/elisctl">elisctl Github page</a>.

To use the webhook for production, run via HTTPS using, for example, Nginx proxy with Let's encrypt
TLS/SSL certificate.

To import testing vendor data to database:
```
    python3 import_vendor_data.py supportive_data/vendor_data_de.csv
```

You can test the webhook on data from `supportive_data` folder.
