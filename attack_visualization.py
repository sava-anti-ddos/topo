import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import sys

DNS_QUIRES_FILE = 'audit/dns_queries.csv'
AUDIT_TRAFFIC_FILE = 'audit/audit_traffic.csv'
VISUALIZATION_FILE = 'audit/attack_visualization.png'

# check if the files exists
if not os.path.exists(DNS_QUIRES_FILE) or not os.path.exists(AUDIT_TRAFFIC_FILE):
    print('The quires or responses file does not exist. Please run the audit and attack first.')
    sys.exit(1)

# Load the data
try:
    dns_queries = pd.read_csv(DNS_QUIRES_FILE)
    audit_traffic = pd.read_csv(AUDIT_TRAFFIC_FILE)
    dns_queries['time'] = pd.to_datetime(dns_queries['time'], unit='s').dt.floor('S')
    audit_traffic['time'] = pd.to_datetime(audit_traffic['time'], unit='s').dt.floor('S')
    dns_responses = audit_traffic[audit_traffic['tag'] == 'DNS_RESPONSE']
    normal_traffic = audit_traffic[audit_traffic['tag'] == 'NORMAL']
except Exception as e:
    print('Error: ', e)
    sys.exit(1)

# Count total query bytes for each second
dns_queries_grouped = dns_queries.groupby('time').agg(
    queries_total_size=('query_size', 'sum')
).reset_index()

# Count aduit traffic total bytes for each second
audit_traffic_grouped = audit_traffic.groupby('time').agg(
    total_size=('packet_size', 'sum')
).reset_index()

# Count total response bytes for each second
dns_responses_grouped = dns_responses.groupby('time').agg(
    responses_total_size=('packet_size', 'sum')
).reset_index()

# Count total normal traffic bytes for each second
normal_traffic_grouped = normal_traffic.groupby('time').agg(
    total_size=('packet_size', 'sum')
).reset_index()

# Fill in the missing seconds
min_start_time = min(dns_queries_grouped['time'].min(), audit_traffic_grouped['time'].min())
max_end_time = max(dns_queries_grouped['time'].max(), audit_traffic_grouped['time'].max())
complete_time_range = pd.date_range(start=min_start_time, end=max_end_time, freq='S')
dns_queries_grouped = dns_queries_grouped.set_index('time').reindex(complete_time_range).fillna(0).reset_index(names='time')
dns_responses_grouped = dns_responses_grouped.set_index('time').reindex(complete_time_range).fillna(0).reset_index(names='time')
audit_traffic_grouped = audit_traffic_grouped.set_index('time').reindex(complete_time_range).fillna(0).reset_index(names='time')
normal_traffic_grouped = normal_traffic_grouped.set_index('time').reindex(complete_time_range).fillna(0).reset_index(names='time')

# Plot query bytes and response bytes per second over time
fig, ax = plt.subplots(figsize=(max(len(dns_queries_grouped) * 0.2, 12), 6))
ax.plot(dns_queries_grouped['time'], dns_queries_grouped['queries_total_size'], 
        label='Query', linewidth=1, color='blue', 
        marker='o', markersize=4, markerfacecolor='blue', markeredgecolor='blue')

ax.plot(dns_responses_grouped['time'], dns_responses_grouped['responses_total_size'], 
        label='Response', linewidth=1, color='red',
        marker='v', markersize=4, markerfacecolor='red', markeredgecolor='red')

ax.plot(audit_traffic_grouped['time'], audit_traffic_grouped['total_size'], 
        label='Total', linewidth=1, color='grey', 
        marker='s', markersize=4, markerfacecolor='grey', markeredgecolor='grey')

ax.plot(normal_traffic_grouped['time'], normal_traffic_grouped['total_size'],
        label='Normal', linewidth=1, color='green',
        marker='x', markersize=4, markerfacecolor='green', markeredgecolor='green')


ax.set_xlabel('Time (Minute:Second)')
ax.set_ylabel('Bytes Per Second')
ax.set_title('Query Bps and response Bps over time')
ax.legend(loc='upper right')

# set the ticks
# x: min - 5s, max + 5s, step 5s
ax.set_xticks(np.arange(min_start_time - pd.Timedelta('5s'), 
                        max_end_time + pd.Timedelta('5s'), pd.Timedelta('5s')))

ax.set_ylim(0, max(dns_queries_grouped['queries_total_size'].max(), 
                   dns_responses_grouped['responses_total_size'].max()) + 6000)
# y: 0, max + 6000Bps, step 2000Bps
ax.set_yticks(np.arange(0, max(dns_queries_grouped['queries_total_size'].max(), 
                               dns_responses_grouped['responses_total_size'].max()) + 6000, 2000))

ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%M:%S'))

ax.yaxis.grid(color='gray', linewidth=0.2)

# save the plot to a file
dirpath = os.path.dirname(VISUALIZATION_FILE)
if not os.path.exists(dirpath):
    os.makedirs(dirpath)
plt.savefig(VISUALIZATION_FILE)
print(f'Attack visualization saved to {VISUALIZATION_FILE}')

