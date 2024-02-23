import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# Load the data
dns_queries = pd.read_csv('audit/dns_queries.csv')
dns_responses = pd.read_csv('audit/dns_responses.csv')

# Count the number of queries and total query bytes for each second
dns_queries['time'] = pd.to_datetime(dns_queries['time'], unit='s').dt.floor('S')
dns_queries_grouped = dns_queries.groupby('time').agg(
    queries_count=('time', 'count'),
    queries_total_size=('query_size', 'sum')
).reset_index()

# Count the number of responses and total response bytes for each second
dns_responses['time'] = pd.to_datetime(dns_responses['time'], unit='s').dt.floor('S')
dns_responses_grouped = dns_responses.groupby('time').agg(
    responses_count=('time', 'count'),
    responses_total_size=('response_size', 'sum')
).reset_index()

# Plot query bytes and response bytes per second over time
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(dns_queries_grouped['time'], dns_queries_grouped['queries_total_size'], 
        label='Query', linewidth=1, color='blue', 
        marker='o', markersize=4, markerfacecolor='blue', markeredgecolor='blue')
# ax.fill_between(dns_queries_grouped['time'], dns_queries_grouped['queries_total_size'], color='blue', alpha=0.1)
ax.plot(dns_responses_grouped['time'], dns_responses_grouped['responses_total_size'], 
        label='Response', linewidth=1, color='orange',
        marker='v', markersize=4, markerfacecolor='orange', markeredgecolor='orange')
# ax.fill_between(dns_responses_grouped['time'], dns_responses_grouped['responses_total_size'], color='orange', alpha=0.1)
ax.set_xlabel('Time (Minute:Second)')
ax.set_ylabel('Bytes Per Second')
ax.set_title('Query Bps and response Bps over time')
ax.legend(loc='upper right')

# set the ticks
# x: min - 5s, max + 5s, step 2s
ax.set_xticks(np.arange(dns_queries_grouped['time'].min() - pd.Timedelta('5s'), 
                        dns_responses_grouped['time'].max() + pd.Timedelta('5s'), pd.Timedelta('5s')))

ax.set_ylim(0, max(dns_queries_grouped['queries_total_size'].max(), 
                   dns_responses_grouped['responses_total_size'].max()) + 6000)
# y: 0, max + 1000, step 1000
ax.set_yticks(np.arange(0, max(dns_queries_grouped['queries_total_size'].max(), 
                               dns_responses_grouped['responses_total_size'].max()) + 6000, 2000))

ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%M:%S'))

# only show the bottom spine
# ax.spines['top'].set_visible(False)
# ax.spines['right'].set_visible(False)
# ax.spines['left'].set_visible(False)

ax.yaxis.grid(color='gray', linewidth=0.2)
# ax.tick_params(axis='y', which='both', length=0, pad=20)
# ax.get_xaxis().get_major_ticks()[0].set_visible(False)

# save the plot to a file
plt.savefig('audit/attack_visualization.png')

