/*

    Schema for the configs database

    Saves all configurations and UI state, readable and writable by the GraphQL
    server, but only readable by the Python server.

    This database includes the following tables:

    - device_info: names of devices and whether they are inspected
    - state_kv: a key-value store for overall application state and settings

    Data types:
    - All lists are JSON encoded.
    - All boolean fields are represented as 1 for true and 0 for false.

    See the system design diagram here:
    https://drive.google.com/file/d/1NPmysXA42BwZnroqAikgl_3HbTHSimJH/view

 */


CREATE TABLE IF NOT EXISTS device_info (
    -- Same device IDs as the other tables
    device_id TEXT PRIMARY KEY,
    -- User-entered name of the device
    device_name TEXT DEFAULT "" NOT NULL,
    -- User-entered name of the manufacturer
    vendor_name TEXT DEFAULT "" NOT NULL,
    -- User-entered tags of the manufacturer; stored as a JSON list
    tag_list TEXT DEFAULT "[]" NOT NULL,
    -- Boolean: whether the device is being inspected
    is_inspected INTEGER DEFAULT 0 NOT NULL,
    -- Boolean: whether the device is being blocked
    is_blocked INTEGER DEFAULT 0 NOT NULL,
);


/*
    I/UX developers can insert whatever default values necessary for the
    operation of the front-end (e.g., badgets, etc). Think about this as a key-value store, where the key can be any arbitrary string, and the value can be any JSON object (represented as text).
*/
CREATE TABLE IF NOT EXISTS state_kv (
    state_key TEXT PRIMARY KEY NOT NULL,
    -- JSON representation of the value
    state_value_json TEXT NOT NULL
);

