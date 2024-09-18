import core.model as model
import peewee
import pandas as pd
import itertools
import datetime
import time


def unix_timestamp_to_local_time(timestamp):

    # Convert the timestamp to a datetime object
    utc_datetime = datetime.datetime.utcfromtimestamp(timestamp)

    # Convert the UTC datetime to local time
    local_datetime = utc_datetime.replace(tzinfo=datetime.timezone.utc).astimezone()

    # Format the local datetime as hours:minutes:seconds
    local_time = local_datetime.strftime('%H:%M:%S')

    return local_time


def get_traffic_rate_df(last_n_seconds=20):
    """
    Returns (upload_df, download_df).

    If no data for either direction, the corresponding df is None.

    Here's a sample output from `print(traffic_rate.get_traffic_rate_df(last_n_seconds=20)[0].head(10).to_string())`:

    ```
        device_mac_addr          ts  Bandwidth (Mbps)      Time
    0  50:14:79:53:13:36  1689613436               0.0  13:03:56
    1  50:14:79:53:13:36  1689613437               0.0  13:03:57
    2  50:14:79:53:13:36  1689613438               0.0  13:03:58
    3  50:14:79:53:13:36  1689613439               0.0  13:03:59
    4  50:14:79:53:13:36  1689613440               0.0  13:04:00
    5  50:14:79:53:13:36  1689613441               0.0  13:04:01
    6  50:14:79:53:13:36  1689613442               0.0  13:04:02
    7  50:14:79:53:13:36  1689613443               0.0  13:04:03
    8  50:14:79:53:13:36  1689613444               0.0  13:04:04
    9  50:14:79:53:13:36  1689613445               0.0  13:04:05
    ```

    """
    max_ts = int(time.time())

    time_filter = model.Flow.end_ts > max_ts - last_n_seconds

    with model.db:
        graph_df = pd.DataFrame(model.Flow.select().where(time_filter).order_by(model.Flow.end_ts).dicts())
    if len(graph_df) == 0:
        return (None, None)
    graph_df['ts'] = graph_df['end_ts'].apply(int).apply(
        lambda t: t - (t % 2)
    )

    # Get all valid mac addresses
    all_mac_address_set = set()
    with model.db:
        for device in model.Device.select():
            if device.mac_addr:
                all_mac_address_set.add(device.mac_addr)

    min_ts = graph_df['ts'].min()
    max_ts = graph_df['ts'].max()
    min_ts = min_ts - min_ts % 2
    max_ts = max_ts - max_ts % 2

    output_list = []

    # Generate the upload and download dataframes
    for direction in ('src', 'dst'):

        mac_addr_col = f'{direction}_device_mac_addr'

        # Remove invalid mac addresses
        valid_mac_graph_df = graph_df[
            (graph_df[mac_addr_col].str.len() == 17)
        ]

        # Aggregate
        byte_graph_df = valid_mac_graph_df.groupby([mac_addr_col, 'ts'])['byte_count'].sum().to_frame('Mbps').reset_index()
        byte_graph_df['Mbps'] = (byte_graph_df['Mbps'] * 8.0 / 1000000.0 / 2.0)

        # Show values during the min-max timeframe
        all_ts_value_df = pd.DataFrame(
            itertools.product(
                all_mac_address_set,
                range(min_ts, max_ts + 1)
            ),
            columns=[mac_addr_col, 'ts']
        )

        byte_graph_df = pd.merge(
            all_ts_value_df,
            byte_graph_df.reset_index(),
            on=[mac_addr_col, 'ts'],
            how='left'
        ).fillna(0)

        del byte_graph_df['index']

        # Convert to ts into local times
        byte_graph_df['human_ts'] = byte_graph_df['ts'].apply(unix_timestamp_to_local_time)

        # Make the mac address field name consistent regardless of the direction
        byte_graph_df = byte_graph_df.rename(columns={
            mac_addr_col: 'device_mac_addr',
            'human_ts': 'Time',
            'Mbps': 'Bandwidth (Mbps)'
        })

        output_list.append(byte_graph_df)

    return tuple(output_list)



def get_activities(mac_addr, last_n_seconds=20, group_by_col='hostname', show_empty=True):
    """
    Returns detailed activities for the given device. Returns (upload_df,
    download_df). If no data for either direction, the corresponding df is None.

    For the example input of
    `print(traffic_rate.get_activities('5c:e9:1e:22:84:7d')[0].head(5).to_string())`,
    the output is:

    ```
       (unknown)  Canada  China  Germany  Ireland  Japan  Netherlands  Poland  Singapore  Sweden  Switzerland  United Kingdom  United States      Time
    0   0.080828     0.0    0.0      0.0      0.0    0.0          0.0     0.0        0.0     0.0          0.0             0.0       0.080828  18:00:46
    1   0.049860     0.0    0.0      0.0      0.0    0.0          0.0     0.0        0.0     0.0          0.0             0.0       0.049860  18:00:48
    2   0.000000     0.0    0.0      0.0      0.0    0.0          0.0     0.0        0.0     0.0          0.0             0.0       0.000000  18:00:50
    3   0.000000     0.0    0.0      0.0      0.0    0.0          0.0     0.0        0.0     0.0          0.0             0.0       0.000000  18:00:52
    4   0.000000     0.0    0.0      0.0      0.0    0.0          0.0     0.0        0.0     0.0          0.0             0.0       0.000000  18:00:54
    ```

    """
    upload_df = get_activities_helper(mac_addr, group_by_col=group_by_col, upload=True, show_empty=show_empty, last_n_seconds=last_n_seconds)

    download_df = get_activities_helper(mac_addr, group_by_col=group_by_col, upload=False, show_empty=show_empty, last_n_seconds=last_n_seconds)

    return upload_df, download_df



def get_activities_helper(mac_addr, group_by_col='hostname', upload=True, show_empty=True, last_n_seconds=20):

    max_ts = int(time.time())

    device_prefix = 'src' if upload else 'dst'
    remote_prefix = 'dst' if upload else 'src'

    full_group_by_col = f'{remote_prefix}_{group_by_col}'

    # Find all flow entries
    search_filter = (
        (model.Flow.end_ts > max_ts - last_n_seconds) &
        (getattr(model.Flow, f'{device_prefix}_device_mac_addr') == mac_addr)
    )

    if not show_empty:
        search_filter &= (getattr(model.Flow, full_group_by_col) != '')

    with model.db:
        graph_df = pd.DataFrame(
            model.Flow.select() \
                .where(search_filter) \
                .order_by(model.Flow.end_ts) \
                .dicts()
            )

    if len(graph_df) == 0:
        return None

    time_base = 60 * 30
    if last_n_seconds <= 60 * 10:
        time_base = 2
    elif last_n_seconds <= 60 * 60:
        time_base = 60
    elif last_n_seconds <= 60 * 60 * 6:
        time_base = 60 * 5

    # Make timestamps multiples of `time_base`
    graph_df['ts'] = graph_df['end_ts'].apply(int).apply(
        lambda t: t - (t % time_base)
    )

    # Find top 10 group_by cols with the most data usage
    data_usage_df = graph_df.groupby(full_group_by_col)['byte_count'].sum() \
        .sort_values(ascending=False).to_frame('byte_count').reset_index().head(5)
    top_ten = list(data_usage_df[full_group_by_col])

    # Combine the non-top-ten labels into a single label
    graph_df[full_group_by_col] = graph_df[full_group_by_col].apply(
        lambda s: s if s in top_ten else '(others)'
    )

    # Aggregate
    byte_graph_df = graph_df.groupby([full_group_by_col, 'ts'])['byte_count'].sum().to_frame('byte_count').reset_index()
    byte_graph_df['Mbps'] = byte_graph_df['byte_count'] * 8.0 / 1000000.0 / 2.0

    # Relabel empty fields
    if show_empty:
        unknown_label = '(unknown)'
        if group_by_col == 'tracker_company':
            unknown_label = '(may not be ad/tracker)'
        byte_graph_df[full_group_by_col] = byte_graph_df[full_group_by_col].replace('', unknown_label)

    # Pivot by the group_by_col
    byte_graph_df = pd.pivot_table(
        byte_graph_df,
        index='ts',
        columns=full_group_by_col,
        values='Mbps',
        aggfunc='sum'
    ).reset_index()

    # Show values during the min-max timeframe
    min_ts = graph_df['ts'].min()
    max_ts = graph_df['ts'].max()
    min_ts = min_ts - min_ts % time_base
    max_ts = max_ts - max_ts % time_base
    all_ts_value_df = pd.DataFrame(
        range(min_ts, max_ts + 1, time_base),
        columns=['ts']
    )

    byte_graph_df = pd.merge(
        all_ts_value_df,
        byte_graph_df.reset_index(),
        on='ts',
        how='left'
    ).fillna(0)

    # Convert to ts into local times
    byte_graph_df['human_ts'] = byte_graph_df['ts'].apply(unix_timestamp_to_local_time)
    del byte_graph_df['index']
    del byte_graph_df['ts']

    # Top ten should not include empty/unknown values
    if '' in top_ten:
        top_ten.remove('')

    # Sort by top 10, plus other columns
    final_columns = []
    current_columns = set(byte_graph_df.columns)
    for col in top_ten:
        if col in current_columns:
            final_columns.append(col)
    remaining_columns = sorted(set(current_columns) - set(final_columns))
    final_columns += remaining_columns
    final_columns.remove('human_ts')
    final_columns.append('human_ts')

    return byte_graph_df[final_columns].rename(columns={
        'human_ts': 'Time',
    })



def get_data_usage(mac_addr, last_n_seconds=20, group_by_col='hostname', show_empty=True):

    upload_df = get_data_usage_helper(mac_addr, group_by_col=group_by_col, upload=True, show_empty=show_empty, last_n_seconds=last_n_seconds)
    download_df = get_data_usage_helper(mac_addr, group_by_col=group_by_col, upload=False, show_empty=show_empty, last_n_seconds=last_n_seconds)

    # Combine into a single dataframe
    return pd.merge(
        upload_df,
        download_df,
        on='Entity',
        how='outer'
    ).fillna(0).sort_values(by='Data Uploaded (MB)', ascending=False)



def get_data_usage_helper(mac_addr, group_by_col='hostname', upload=True, show_empty=True, last_n_seconds=20):

    max_ts = int(time.time())

    device_prefix = 'src' if upload else 'dst'
    remote_prefix = 'dst' if upload else 'src'

    full_group_by_col = f'{remote_prefix}_{group_by_col}'

    # Find all flow entries
    search_filter = (
        (model.Flow.end_ts > max_ts - last_n_seconds) &
        (getattr(model.Flow, f'{device_prefix}_device_mac_addr') == mac_addr)
    )

    if not show_empty:
        search_filter &= (getattr(model.Flow, full_group_by_col) != '')

    with model.db:
        data_df = pd.DataFrame(
            model.Flow.select() \
                .where(search_filter) \
                .order_by(model.Flow.end_ts) \
                .dicts()
            )

    unknown_label = '(unknown)'
    if group_by_col == 'tracker_company':
        unknown_label = '(may not be ad/tracker)'

    if len(data_df) == 0:
        data_df = pd.DataFrame({
            full_group_by_col: [unknown_label],
            'byte_count': [0]
        })

    # Aggregate data usage by each entity
    data_df = data_df.groupby(full_group_by_col)['byte_count'].sum().to_frame('byte_count').reset_index()
    data_df['byte_count'] = data_df['byte_count'] / 1000000.0

    # Relabel empty fields
    if show_empty:
        data_df[full_group_by_col] = data_df[full_group_by_col].replace('', unknown_label)

    return data_df.rename(columns={
        full_group_by_col: 'Entity',
        'byte_count': ('Data Uploaded (MB)' if upload else 'Data Downloaded (MB)')
    })



def get_all_device_rate(last_n_seconds=20):

    upload_df = get_all_device_rate_helper(upload=True, last_n_seconds=last_n_seconds)
    download_df = get_all_device_rate_helper(upload=False, last_n_seconds=last_n_seconds)

    return (upload_df, download_df)



def get_all_device_rate_helper(upload=True, last_n_seconds=20):
    """
    Sample output:

    `>>> print(traffic_rate.get_all_device_rate_helper(upload=True, last_n_seconds=300).head(5).to_string())`

    ```
       08:b4:b1:23:08:a8  9c:76:13:16:dc:cc  5c:e9:1e:22:84:7d  08:b4:b1:23:09:37  9c:76:13:13:87:7f  (others)      Time
    0          98.486020           6.344232           1.568344           0.004816           0.000000  0.046392  15:20:00
    1          15.540892           1.152096           6.126464           0.008240           0.001408  0.094952  15:21:00
    2          38.651788           7.431792           0.579808           0.059808           0.000000  0.041648  15:22:00
    3           0.868868           5.525848           0.106760           1.134128           0.000000  0.081344  15:23:00
    4          22.594804           0.024224           0.725752           0.013640           0.000000  0.041064  15:24:00
    ```

    Returns None if no data.

    """
    max_ts = int(time.time())

    device_prefix = 'src' if upload else 'dst'
    device_mac_group_by_col = f'{device_prefix}_device_mac_addr'

    # Find all flow entries
    search_filter = (
        (model.Flow.end_ts > max_ts - last_n_seconds) &
        (getattr(model.Flow, device_mac_group_by_col) != '')
    )

    with model.db:
        graph_df = pd.DataFrame(
            model.Flow.select() \
                .where(search_filter) \
                .order_by(model.Flow.end_ts) \
                .dicts()
            )

    if len(graph_df) == 0:
        return None

    time_base = 60 * 30
    if last_n_seconds <= 60:
        time_base = 2
    elif last_n_seconds <= 60 * 60:
        time_base = 60
    elif last_n_seconds <= 60 * 60 * 6:
        time_base = 60 * 5

    # Make timestamps multiples of `time_base`
    graph_df['ts'] = graph_df['end_ts'].apply(int).apply(
        lambda t: t - (t % time_base)
    )

    # Find top 10 mac addresses with the most data usage

    data_usage_df = graph_df.groupby(device_mac_group_by_col)['byte_count'].sum() \
        .sort_values(ascending=False).to_frame('byte_count').reset_index().head(5)
    top_ten = list(data_usage_df[device_mac_group_by_col])

    # Combine the non-top-ten labels into a single label
    graph_df[device_mac_group_by_col] = graph_df[device_mac_group_by_col].apply(
        lambda s: s if s in top_ten else '(others)'
    )

    # Aggregate
    byte_graph_df = graph_df.groupby([device_mac_group_by_col, 'ts'])['byte_count'].sum().to_frame('byte_count').reset_index()
    byte_graph_df['Mbps'] = byte_graph_df['byte_count'] * 8.0 / 1000000.0 / 2.0

    # Pivot by the group_by_col
    byte_graph_df = pd.pivot_table(
        byte_graph_df,
        index='ts',
        columns=device_mac_group_by_col,
        values='Mbps',
        aggfunc='sum'
    ).reset_index()

    # Show values during the min-max timeframe
    min_ts = graph_df['ts'].min()
    max_ts = graph_df['ts'].max()
    min_ts = min_ts - min_ts % time_base
    max_ts = max_ts - max_ts % time_base
    all_ts_value_df = pd.DataFrame(
        range(min_ts, max_ts + 1, time_base),
        columns=['ts']
    )

    byte_graph_df = pd.merge(
        all_ts_value_df,
        byte_graph_df.reset_index(),
        on='ts',
        how='left'
    ).fillna(0)

    # Convert to ts into local times
    byte_graph_df['human_ts'] = byte_graph_df['ts'].apply(unix_timestamp_to_local_time)
    del byte_graph_df['index']
    del byte_graph_df['ts']

    # Sort by top 10, plus other columns
    final_columns = []
    current_columns = set(byte_graph_df.columns)
    for col in top_ten:
        if col in current_columns:
            final_columns.append(col)
    remaining_columns = sorted(set(current_columns) - set(final_columns))
    final_columns += remaining_columns
    final_columns.remove('human_ts')
    final_columns.append('human_ts')

    byte_graph_df = byte_graph_df[final_columns]

    # Label all the mac addresses
    rename_dict = {}
    with model.db:
        for col in list(byte_graph_df.columns):
            if col not in ('human_ts', '(others)'):
                try:
                    device = model.Device.get(mac_addr=col)
                except model.Device.DoesNotExist:
                    del byte_graph_df[col]
                    continue
                product_name = device.product_name
                if not product_name:
                    product_name = 'Unnamed Device ' + col[-5:].replace(':', '')
                rename_dict[col] = product_name

    rename_dict.update({'human_ts': 'Time'})
    return byte_graph_df.rename(columns=rename_dict)


