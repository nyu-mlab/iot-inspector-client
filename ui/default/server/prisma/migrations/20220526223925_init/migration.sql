-- CreateTable
CREATE TABLE "Device" (
    "device_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "ip" TEXT NOT NULL,
    "mac" TEXT NOT NULL,
    "dhcp_hostname_list" TEXT NOT NULL,
    "netdisco_list" TEXT NOT NULL,
    "user_agent_list" TEXT NOT NULL,
    "syn_scan_port_list" TEXT NOT NULL,
    "auto_name" TEXT NOT NULL,
    "last_updated_ts" INTEGER NOT NULL
);

-- CreateTable
CREATE TABLE "CounterParty" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "remote_ip" TEXT NOT NULL,
    "hostname" TEXT NOT NULL,
    "source" TEXT NOT NULL,
    "resolver_ip" TEXT NOT NULL,
    "ts" INTEGER NOT NULL,
    "device_id" INTEGER NOT NULL,
    CONSTRAINT "CounterParty_device_id_fkey" FOREIGN KEY ("device_id") REFERENCES "Device" ("device_id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "Flow" (
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
    "device_id" INTEGER NOT NULL,
    "counterPartyId" INTEGER NOT NULL,
    CONSTRAINT "Flow_device_id_fkey" FOREIGN KEY ("device_id") REFERENCES "Device" ("device_id") ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT "Flow_counterPartyId_fkey" FOREIGN KEY ("counterPartyId") REFERENCES "CounterParty" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
