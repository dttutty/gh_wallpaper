import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
from config import USERNAME, TOKEN

# Function to get contribution data
def get_contribution_data(username, token):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/users/{username}/events"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    
    return response.json()

# Get contribution data
data = get_contribution_data(USERNAME, TOKEN)

if data is None:
    print("Failed to fetch data. Exiting.")
    exit()

# Process the data
contribution_counts = {}
end_date = datetime.now().date()
start_date = end_date - timedelta(days=365)

for event in data:
    event_date = datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ").date()
    if start_date <= event_date <= end_date:
        date_str = event_date.strftime("%Y-%m-%d")
        contribution_counts[date_str] = contribution_counts.get(date_str, 0) + 1

# Prepare data for plotting
dates = []
contributions = []
current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime("%Y-%m-%d")
    dates.append(current_date)
    contributions.append(contribution_counts.get(date_str, 0))
    current_date += timedelta(days=1)

# Create a DataFrame
df = pd.DataFrame({'date': dates, 'contributions': contributions})
df['weekday'] = df['date'].dt.weekday
df['week'] = df['date'].dt.to_period('W').apply(lambda r: r.start_time)

# Pivot the data for heatmap
pivot_data = df.pivot(index='weekday', columns='week', values='contributions')

# Create the heatmap
plt.figure(figsize=(20, 5))
sns.heatmap(pivot_data, cmap='YlGnBu', linewidths=0.5, linecolor='white')

plt.title(f"GitHub Contributions for {USERNAME}")
plt.xlabel("Week")
plt.ylabel("Day of Week")

# Customize y-axis labels
plt.yticks(range(7), ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])

# Save the image
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
plt.savefig(os.path.join(output_dir, "github_contributions_heatmap.png"))
plt.close()

print("Contribution heatmap has been generated and saved in the output folder.")
