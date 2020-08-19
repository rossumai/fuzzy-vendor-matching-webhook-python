# Example Elis Vendor Matching Connector

The connector matches extracted vendor name, address and VAT ID against a vendor database. 
Any of these data is sufficient for the right vendor match.

![Vendor Matching Connector](vendor_matching_connector.gif)

### Setup
Check out our [Developer Hub vendor matching connector guide](https://developers.rossum.ai/docs/how-to-run-sample-vendor-matching-connector) to set up
and run the connector for the first time.

After setting up the connector, update `CONNECTOR_AUTH_KEY["CONNECTOR_AUTH_KEY"]` value in `config.py`.
The value should be the same as the secret authentication token you created
following the connector guide.

To use the connector for production, run via HTTPS using, for example, Nginx proxy with Let's encrypt 
TLS/SSL certificate. 
