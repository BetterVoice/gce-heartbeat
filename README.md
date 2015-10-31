# gce-heartbeat
Is a simple service used to have a secondary instace on the Google Compute Engine observe a primary instance for failure. In the case the primary instance fails the secondary instance will take over the static IP assigned to the master instance. Enjoy!

# gce-heartbeat deployment

Open the gce-heartbeat file in your favorite editor and set the variables at the beginning of the file to the proper values. Then execute the commands listed below.

```
$] sudo apt-get install libpq-dev python-dev
$] pip install psycopg2
$] pip install google-api-python-client
$] cp heartbeat.py /usr/local/bin
$] cp gce-heartbeat /etc/init.d
$] chmod +x /etc/init.d/gce-heartbeat
$] update-rc.d -f gce-heartbeat defaults
$] service gce-heartbeat start
```

# gce man

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
