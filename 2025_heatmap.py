import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


file_path = '/Users/spencerkline/Documents/Country Heatmap -- Local.xlsx'
# Load the Excel file
heatmap_data = pd.read_excel(file_path, sheet_name='2025', engine='openpyxl')

# Load the world map
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# Merge the heatmap data with the world map
world_heatmap = world.merge(heatmap_data, how="left", left_on="name", right_on="Country")

# Fill NaN values with 0 for countries not in our heatmap data to keep them blank
world_heatmap['Value'].fillna(0, inplace=True)

# Define a custom color map: white for 0, red for 1, green for 2
from matplotlib.colors import ListedColormap
custom_cmap = ListedColormap(['white', 'blue', 'green'])

# Ensure 'Value' is of a categorical type for proper color mapping
world_heatmap['Value'] = pd.Categorical(world_heatmap['Value'])

# Plotting
fig, ax = plt.subplots(1, 1, figsize=(15, 10))
world_heatmap.plot(column='Value', ax=ax, cmap=custom_cmap, linewidth=0.8, edgecolor='black')

# Coordinates for Singapore
singapore_coords = (103.8198, 1.3521)  # Longitude, Latitude

# Add a red dot for Singapore if its value is 1 or green dot if its value is 2
singapore_value = heatmap_data.loc[heatmap_data['Country'] == 'Singapore', 'Value'].iloc[0]
if singapore_value == 1:
    ax.scatter(singapore_coords[0], singapore_coords[1], color='blue', s=100)
elif singapore_value == 2:
    ax.scatter(singapore_coords[0], singapore_coords[1], color='green', s=100)

# Remove axis
ax.set_axis_off()

# Set a title
plt.title('TeleMedC 2025 Presence')

# Show the plot
plt.savefig('/Users/spencerkline/Documents/2025.png', dpi=300, bbox_inches='tight')

