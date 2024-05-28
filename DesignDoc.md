# Design of IoT Inspector Lite

## Design goals

[G1] The UI should show data as fast as possible, so that the user can observe IoT activities in real time.

[G2] The UX should tailor to non-experts as much as possible. Keep the visualizations responsive and simple.


## Overview of components

 * `core`: Collects network traffic into database; mostly using `scapy`
 * `ui`: Visualizes data with `streamlit`



## Data formats

### Summary

All data is stored in a SQLite database. There are only two tables:

   * `flows`: for storing flow-related information, including the following columns:
      * `src_device_mac_addr`: text, indexed, all lower case, no punctuation (i.e., no `:`)
      * `dst_device_mac_addr`: text, indexed
      * `src_port`: integer
      * `dst_port`: integer
      * `src_ip_addr`: text, indexed
      * `dst_ip_addr`: text, indexed
      * `src_hostname`: text, indexed
      * `dst_hostname`: text, indexed
      * `src_hostname_is_definitive`: integer; 1 if the hostname is definitive, 0 otherwise, indexed
      * `dst_hostname_is_definitive`: integer; 1 if the hostname is definitive, 0 otherwise, indexed
      * `protocol`: text, indexed, e.g., "TCP", "UDP"
      * `byte_count`: integer; number of bytes captured during this `ts` bucket
      * `packet_count`: integer; number of packets captured during this `ts` bucket
      * `ts`: integer, indexed
      * `metadata_json`: json text; for extensibility in future versions

   * `kv_store`: for storing everything else
      * `key`: text, indexed, unique
      * `value_json`: json text

The `flows` table is meant for efficient querying of flow-related information. Hence we're not using a key-value format here.

For `kv_store`, we use a key-value, format because IoT Inspector may change in every release (e.g., collecting more data/fields, per new experiments/features). This format gives us the highest flexbility while not compromising the performance (i.e., by using indices). All values are stored as JSON objects. SQLite supports fast querying of JSON data.

There is also an in-memory-only `queued_flows` table, which has exactly the same schema as `flows`. We need an in-memory version because we need to write to the memory-only table as fast as possible as each packet comes in. We aggregate flow statistics, such as the byte count and packet count, on the fly, using the tuple `(src_device_mac_addr, dst_device_mac_addr, src_ip_addr, dst_ip_addr, src_port, dst_port, protocol)` and the `ts` as the key. Every minute, we flush any `ts` beyond 60 seconds into the `flows` table.

The fast parts of the UI (e.g., displaying the flow statistics) will query the `queued_flows` table.

We will also create a `combined_flows` view, which is a union of `flows` and `queued_flows`. This view will be used for the slow parts of the UI (e.g., querying historical data). Think of "views" as a virtual table that is the result of a query. You can read from a view but you cannot write to it as it is not a real table. The benefit of having a view here is that you can query both the `flows` and `queued_flows` tables at the same time, even though one is on disk and the other is in memory. Both tables have the same schema although mutually exclusive, so the view can be created easily.


### Formats of the key-value store

The keys are hierarchical, each component separated by `:`. They are mapped to the corresponding value fields.

   * Device info
      * `device_info:<mac_addr>`: a dictionary with the following keys:
         * `ip_addr`
         * Identifying info: `dhcp_hostname`, `upnp`, `mdns`
         * User labels: `user_product_name`
         * ML-inferred info: `maybe_product_name`, based on the NYU API
         * Deivice state: `is_inspected`, `favorite_ts`

   * IP to hostname mapping
      * `ip_to_hostname:<ip_addr>`: the FQDN, based on definitive sources, including DNS and SNI
      * `ip_to_maybe_hostname:<ip_addr>`: the FQDN, based on less definitive sources, including passive DNS (from the NYU API) and reverse DNS

   * Hostname to inferred into mapping
      * `ad_tracking_company:<hostname>`: Name of the ad/tracking company
      * `maybe_company_name:<hostname>`: Name of the company, based on the NYU API

   * Configurations
      * `configs:is_donating_data`: true/false


## Data flow

### Data collection

The `core` component collects network traffic and stores it in the SQLite database.

1. A packet comes in and gets captured by `scapy`.
1. Inspector queues the packet.
1. A separate thread parses the packet. Some information can be stored directly into the `kv_store` table on disk, such as the IP to hostname mapping (e.g., in the case of DNS packets). Flow information is written to the `queued_flows` table.
1. Another thread, every minute, copies rows that are more than 60 seconds from the current time from the `queue_flows` table in memory to the `flows` table on disk, and then removes these copied flows. In doing so, the fast parts of the UI can query the `queued_flows` table, while the slow parts can query the `flows` table -- or even better, the slow parts can query the `combined_flows` view.

A friendly identifier runs as a separate thread to turn some of the info above into human-friendly information:

   * Looks up IP addresses for which the hostnames are not definitive and attempts to translate them into hostnames. Stores the results in `ip_to_hostname` and `ip_to_maybe_hostname`.
   * Asks NYU API for possible product names based on the MAC address, FQDNs contacted, and other relevant information. Stores the results in `maybe_product_name`

### Data visualization

The `ui` component visualizes the data in the SQLite database.

At the end of a page load, the UI queries the database, stores the results (along with any visualization), into `streamlit`'s `session_state`, and reruns the page. The next re-run will load the cached results from `session_state`.


## UI/UX

See https://docs.google.com/presentation/d/1i0f45M9-tE0XMGXbOLoWdo2txRscJ6zK01oOdfqM9Y0/edit#slide=id.p