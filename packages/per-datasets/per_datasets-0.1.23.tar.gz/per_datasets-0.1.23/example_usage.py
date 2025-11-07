"""
Example usage of the per_datasets package
"""

import per_datasets as pds

# Initialize with your API key
pds.initialize(api_key="pk_27dae73edc477fee17f0373d77c96d6acfe907177dbe8fc651c1af596ca22c05")

# Load a random reservoir dataset
df_random = pds.reservoir.load_random()
