# gce-heartbeat
A service to failover a static IP on the Google Compute Engine.

usage: heartbeat.py [-h] --interval INTERVAL --project PROJECT --region REGION
                    --address-name ADDRESS_NAME --primary PRIMARY
                    --primary-zone PRIMARY_ZONE --secondary SECONDARY
                    --secondary-zone SECONDARY_ZONE

Establish a heartbeat between two instances for external IP failover.

optional arguments:
  -h, --help            show this help message and exit
  --interval INTERVAL   The heartbeat interval in seconds.
  --project PROJECT     The project ID.
  --region REGION       The name of the region.
  --address-name ADDRESS_NAME
                        Name of the static address.
  --primary PRIMARY     The name of the primary instance.
  --primary-zone PRIMARY_ZONE
                        The primary instance zone.
  --secondary SECONDARY
                        The name of the secondary instance.
  --secondary-zone SECONDARY_ZONE
                        The secondary instance zone.