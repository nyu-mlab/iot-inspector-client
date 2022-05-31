/*
  Warnings:

  - The primary key for the `Device` table will be changed. If it partially fails, the table could be left without primary key constraint.

*/
-- RedefineTables
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_Flow" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "device_port" INTEGER NOT NULL,
    "counterparty_ip" TEXT NOT NULL,
    "counterparty_port" INTEGER NOT NULL,
    "counterparty_hostname" TEXT NOT NULL,
    "counterparty_friendly_name" TEXT NOT NULL,
    "counterparty_country" TEXT NOT NULL,
    "counterparty_is_ad_tracking" INTEGER NOT NULL,
    "transport_layer_protocol" TEXT NOT NULL,
    "uses_weak_encryption" INTEGER NOT NULL,
    "ts" INTEGER NOT NULL,
    "ts_mod_60" INTEGER NOT NULL,
    "ts_mod_600" INTEGER NOT NULL,
    "ts_mod_3600" INTEGER NOT NULL,
    "window_size" INTEGER NOT NULL,
    "inbound_byte_count" INTEGER NOT NULL,
    "outbound_byte_count" INTEGER NOT NULL,
    "inbound_packet_count" INTEGER NOT NULL,
    "outbound_packet_count" INTEGER NOT NULL,
    "device_id" TEXT NOT NULL,
    "counterPartyId" INTEGER NOT NULL,
    CONSTRAINT "Flow_device_id_fkey" FOREIGN KEY ("device_id") REFERENCES "Device" ("device_id") ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT "Flow_counterPartyId_fkey" FOREIGN KEY ("counterPartyId") REFERENCES "CounterParty" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
INSERT INTO "new_Flow" ("counterPartyId", "counterparty_country", "counterparty_friendly_name", "counterparty_hostname", "counterparty_ip", "counterparty_is_ad_tracking", "counterparty_port", "device_id", "device_port", "id", "inbound_byte_count", "inbound_packet_count", "outbound_byte_count", "outbound_packet_count", "transport_layer_protocol", "ts", "ts_mod_3600", "ts_mod_60", "ts_mod_600", "uses_weak_encryption", "window_size") SELECT "counterPartyId", "counterparty_country", "counterparty_friendly_name", "counterparty_hostname", "counterparty_ip", "counterparty_is_ad_tracking", "counterparty_port", "device_id", "device_port", "id", "inbound_byte_count", "inbound_packet_count", "outbound_byte_count", "outbound_packet_count", "transport_layer_protocol", "ts", "ts_mod_3600", "ts_mod_60", "ts_mod_600", "uses_weak_encryption", "window_size" FROM "Flow";
DROP TABLE "Flow";
ALTER TABLE "new_Flow" RENAME TO "Flow";
CREATE TABLE "new_CounterParty" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "remote_ip" TEXT NOT NULL,
    "hostname" TEXT NOT NULL,
    "source" TEXT NOT NULL,
    "resolver_ip" TEXT NOT NULL,
    "ts" INTEGER NOT NULL,
    "device_id" TEXT NOT NULL,
    CONSTRAINT "CounterParty_device_id_fkey" FOREIGN KEY ("device_id") REFERENCES "Device" ("device_id") ON DELETE RESTRICT ON UPDATE CASCADE
);
INSERT INTO "new_CounterParty" ("device_id", "hostname", "id", "remote_ip", "resolver_ip", "source", "ts") SELECT "device_id", "hostname", "id", "remote_ip", "resolver_ip", "source", "ts" FROM "CounterParty";
DROP TABLE "CounterParty";
ALTER TABLE "new_CounterParty" RENAME TO "CounterParty";
CREATE TABLE "new_Device" (
    "device_id" TEXT NOT NULL PRIMARY KEY,
    "ip" TEXT NOT NULL,
    "mac" TEXT NOT NULL,
    "dhcp_hostname_list" TEXT NOT NULL,
    "netdisco_list" TEXT NOT NULL,
    "user_agent_list" TEXT NOT NULL,
    "syn_scan_port_list" TEXT NOT NULL,
    "auto_name" TEXT NOT NULL,
    "last_updated_ts" INTEGER NOT NULL
);
INSERT INTO "new_Device" ("auto_name", "device_id", "dhcp_hostname_list", "ip", "last_updated_ts", "mac", "netdisco_list", "syn_scan_port_list", "user_agent_list") SELECT "auto_name", "device_id", "dhcp_hostname_list", "ip", "last_updated_ts", "mac", "netdisco_list", "syn_scan_port_list", "user_agent_list" FROM "Device";
DROP TABLE "Device";
ALTER TABLE "new_Device" RENAME TO "Device";
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
