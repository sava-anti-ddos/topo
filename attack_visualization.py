import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import sys

DNS_QUIRES_FILE_PREFIX = 'audit/dns_queries'
AUDIT_TRAFFIC_FILE = 'audit/audit_traffic.csv'
AUDIT_QUERY_TRAFFIC_FILE = 'audit/audit_query_traffic.csv'

VISUALIZATION_FILE = 'audit/attack_visualization.png'

def check_files_with_prefix(prefix):
    # Get all files in the directory
    directory = os.path.dirname(prefix)
    files = os.listdir(directory)
    file_prefix = os.path.basename(prefix)
    
    # Check if any file starts with the prefix
    for file in files:
        if file.startswith(file_prefix):
            return True
    
    return False

def load_all_queries(prefix):
    # Get all files in the directory
    file_prefix = os.path.basename(prefix)
    dir_name = os.path.dirname(prefix)
    files = os.listdir(dir_name)
    
    # Load all the queries
    all_queries = []
    for file in files:
        if file.startswith(file_prefix):
            queries_by_host = pd.read_csv(os.path.join(dir_name, file))
            all_queries.append(queries_by_host)
    
    # concat and sort by time
    return pd.concat(all_queries).sort_values(by='time')

# check if the files exists
if not check_files_with_prefix(DNS_QUIRES_FILE_PREFIX) or not os.path.exists(AUDIT_TRAFFIC_FILE):
    print('The quires or responses file does not exist. Please run the audit and attack first.')
    sys.exit(1)

# Load the data
try:
    dns_queries = load_all_queries(DNS_QUIRES_FILE_PREFIX)
    audit_traffic = pd.read_csv(AUDIT_TRAFFIC_FILE)
    for df in [dns_queries, audit_traffic]:
        df['time'] = pd.to_datetime(df['time'], unit='s').dt.floor('S')
    audit_dns_responses = audit_traffic[audit_traffic['tag'] == 'DNS_RESPONSE']
    audit_normal_traffic = audit_traffic[audit_traffic['tag'] == 'NORMAL']

    if os.path.exists(AUDIT_QUERY_TRAFFIC_FILE):
        audit_query_traffic = pd.read_csv(AUDIT_QUERY_TRAFFIC_FILE)
        audit_query_traffic['time'] = pd.to_datetime(audit_query_traffic['time'], unit='s').dt.floor('S')
except Exception as e:
    print('Error: ', e)
    sys.exit(1)


grouped_data = {
    'dns_queries': dns_queries,
    'audit_dns_responses': audit_dns_responses,
    'audit_normal_traffic': audit_normal_traffic,
}
if os.path.exists(AUDIT_QUERY_TRAFFIC_FILE):
    grouped_data['audit_query_traffic'] = audit_query_traffic

for name, df in grouped_data.items():
    grouped_data[name] = df.groupby('time').agg(
        Bps=('packet_size', 'sum')
    ).reset_index()



# Fill in the missing seconds
min_start_time = min(df['time'].min() for df in grouped_data.values())
max_end_time = max(df['time'].max() for df in grouped_data.values())
complete_time_range = pd.date_range(start=min_start_time, end=max_end_time, freq='S')
for name, df in grouped_data.items():
    grouped_data[name] = df.set_index('time').reindex(complete_time_range).fillna(0).reset_index(names='time')

# Plot query bytes and response bytes per second over time
fig, ax = plt.subplots(figsize=(max(len(complete_time_range) * 0.2, 12), 6))

plot_option_map = {
    'dns_queries': {'label': 'Attack Traffic - h2,h3', 'color': 'blue', 'marker': 'o'},
    'audit_dns_responses': {'label': 'Amplified Traffic - h5', 'color': 'red', 'marker': 'v'},
    'audit_normal_traffic': {'label': 'Normal Traffic - h5', 'color': 'green', 'marker': 'x'},
    'audit_query_traffic': {'label': 'Attack Traffic Received - h4', 'color': 'orange', 'marker': 'o'},
}

for name, df in grouped_data.items():
    ax.plot(df['time'], df['Bps'], 
            label=plot_option_map[name]['label'], linewidth=1, color=plot_option_map[name]['color'],
            marker=plot_option_map[name]['marker'], markersize=4, 
            markerfacecolor=plot_option_map[name]['color'], markeredgecolor=plot_option_map[name]['color'])

ax.set_xlabel('Time (Minute:Second)')
ax.set_ylabel('Bytes Per Second')
ax.set_title('Traffic Monitoring')
ax.legend(loc='upper right')

# set the ticks
# x: min - 5s, max + 5s, step 5s
ax.set_xticks(np.arange(min_start_time - pd.Timedelta('5s'), 
                        max_end_time + pd.Timedelta('5s'), pd.Timedelta('5s')))

max_Bps = max(df['Bps'].max() for df in grouped_data.values())
ax.set_ylim(0, max_Bps + 6000)
# y: 0, max + 6000Bps, step 2000Bps
ax.set_yticks(np.arange(0, max_Bps + 6000, 2000))

ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%M:%S'))

ax.yaxis.grid(color='gray', linewidth=0.2)

# save the plot to a file
dirpath = os.path.dirname(VISUALIZATION_FILE)
if not os.path.exists(dirpath):
    os.makedirs(dirpath)
plt.savefig(VISUALIZATION_FILE)
print(f'Attack visualization saved to {VISUALIZATION_FILE}')

