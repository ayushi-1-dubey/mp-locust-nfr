# mp-locust-nfr
# mp-locust-nfr

This repo contains the locust files for inventory service APIs.

- proto directory : Contains proto files for distributor-service, inventory-manager and ab-service. 
- MetadataclientInterceptor : This file contains the interceptor implementation. Headers can be added as a metadata in ClientCallDetails.
- sample-load-data : This directory contains a script.py which randomly generates sample request payloads and writes them to their respective files.
- fkh_lot_ids.json : This file is generated once locust file for create inventory runs. These fkh_lot_ids are then made available to test other dependent APIs.

To generate the sample payloads, specify the count of payloads inside script.py - main function, and run the file.

## How to test the files on localhost
- Run the services (portal-service, inventory-manager, ab-service) locally.
- Make sure that mysql and redis are running and they have some seed data.
- distributor_apob_id is set to "1" in all the locust files so make sure that this apob id exists in your db.
- Generate new sample data (if not done already) or use the existing data in the repo.
  - To generate the sample payloads, specify the count of payloads inside script.py - main function, and run script.py
- Now run the following commands for each locust file : 
```
locust -f locust-files/locust_create_inv.py
locust -f locust-files/locust_update_inv_qty_using_fkhlot_id.py
locust -f locust-files/locust_update_inv_qty_using_external_lotid.py
locust -f locust-files/locust_update_sold_qty_using_fkh_lot_id.py
locust -f locust-files/locust_update_sold_qty_using_external_lot_id.py
locust -f locust-files/locust_update_sold_qty_using_fkh_lot_id.py
locust -f locust-files/locust_get_available_lots.py
locust -f locust-files/locust_get_lot_details.py
```
and so on...
