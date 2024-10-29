import sqlite3
import pandas as pd
from sklearn.cluster import KMeans

# Connect to the SQLite database
conn = sqlite3.connect('/tmp/blacklist.db')
query = "SELECT sip, dip, sport, dport, protocol, count FROM SnifferInfo"
df = pd.read_sql_query(query, conn)

# Assuming the data needs to be clustered based on all columns
# If you need specific columns, you can select them like df[['col1', 'col2']]
data = df.values

# Perform KMeans clustering
kmeans = KMeans(n_clusters=2)  # You can change the number of clusters
kmeans.fit(data)

# Add the cluster labels to the dataframe
df['cluster'] = kmeans.labels_


# Close the connection
conn.close()