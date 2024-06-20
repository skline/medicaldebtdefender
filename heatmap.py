import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pandas as pd

file_path = '/Users/spencerkline/Documents/Country Heatmap -- Local.xlsx'
# Load the Excel file
heatmap_data = pd.read_excel(file_path, sheet_name='2023', engine='openpyxl')

# Load the world map
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# Prepare your data similar to the DataFrame structure we discussed earlier
# Assuming 'heatmap_data' is already prepared with country names and values

# Merge the heatmap data with the world map
world_heatmap = world.merge(heatmap_data, how="left", left_on="name", right_on="Country")

# Fill NaN values with 0 for countries not in our heatmap data to keep them blank
world_heatmap['Value'].fillna(0, inplace=True)

# Plotting
fig, ax = plt.subplots(1, 1, figsize=(15, 10))
world_heatmap.plot(column='Value', ax=ax, cmap=plt.cm.colors.ListedColormap(['white', 'red']), linewidth=0.8, edgecolor='black')

# Coordinates for Singapore
singapore_coords = (103.8198, 1.3521) # Longitude, Latitude

# Add a red dot for Singapore
ax.scatter(singapore_coords[0], singapore_coords[1], color='red', s=100) # s is the size of the marker

# Remove axis
ax.set_axis_off()

# Set a title
plt.title('TeleMedC 2023 Presence')

# Show the plot
plt.show()
