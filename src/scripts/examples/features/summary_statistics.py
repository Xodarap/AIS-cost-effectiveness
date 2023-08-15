"""
Example of how to generate summary statistics about programs.
"""

"""
Imports
"""

import sys

sys.path.append("src")

# Parameters
import parameters.tdc as p_p
import parameters.neurips_social as p_so
import parameters.neurips_workshop as p_w

# Models
import models.professional_program as mfn_pp

# Sampling
import utilities.sampling.simulate_results as so  # for data

# Helper functions
import utilities.plotting.helper_functions as help  # for tables

# Common python packages
import pandas as pd  # for reading csv
import numpy as np  # for sorting arrays
import itertools

# Simulations
from squigglepy.numbers import K, M


"""
Get data
"""

# Set parameters for data
n_sim = 30 * K
time_points = np.arange(0.0, 60.0, 1.0)
programs = ["tdc", "neurips_social", "neurips_workshop"]
default_parameters = {"tdc": p_p, "neurips_social": p_so, "neurips_workshop": p_w}
master_functions = {"tdc": mfn_pp, "neurips_social": mfn_pp, "neurips_workshop": mfn_pp}

# Call function that generates data
# This function returns two DataFrames: one with program functions and one with program parameters
df_functions, df_params = so.get_program_data(
    programs=programs,
    default_parameters=default_parameters,
    master_functions=master_functions,
    n_sim=n_sim,
    time_points=time_points,
)


"""
Compute summary statistics
"""

# Compute parameter means for each program
means = {}
for program, df in df_params.items():
    means[program] = df.mean()
print(f"years: {means['tdc']['years_until_phd_phd_cf']}")
print(f'"mean_ability": {[k for k in means["tdc"].keys() if k.startswith("mean_ability")]}')
print(f'"n_scientist_equivalent_attendee": {means["tdc"]["n_scientist_equivalent_contender"]}')
# print(df_params['tdc'].keys())
# print(df_functions['tdc'].keys())

participant_types = ["contender", "attendee"]
researcher_types = ["_professor","_scientist","_engineer","_phd"]
undergrad_types = ["_via_phd", "_not_via_phd", ""]
relevance_keys = set(["research_relevance_over_t_" + participant_type + researcher_type + undergrad_type
                  for participant_type, researcher_type, undergrad_type 
                  in itertools.product(participant_types, researcher_types, undergrad_types)])
# print(f'Found {(relevance_keys)} keys for relevance')
for program, df in df_functions.items():
    found_keys = relevance_keys & set(df.keys())
    means[program]['relevance'] = np.mean([df[key].mean() for key in found_keys])
    means[program]['relevance_cf'] = np.mean([df[key + '_cf'].mean() for key in found_keys])

for program, df in df_params.items():
    means[program]['n_scientist_equivalent_attendee'] = df.get("n_scientist_equivalent_contender", pd.Series([0])).mean() + df.get("n_scientist_equivalent_attendee", pd.Series([0])).mean()
    if 'n_scientist_equivalent_contender' in df.keys():
        print(f'Found n_scientist_equivalent_contender for {df["n_scientist_equivalent_contender"]}')
    # print(f'Found {len(found_keys)} keys for {program}')


print(f"relevance: {means['tdc']['relevance']}")
# Create a DataFrame with parameter means for each program
df_params_means = pd.DataFrame(means)
df_params_means.reset_index(inplace=True)
df_params_means.rename(columns={"index": "parameter"}, inplace=True)
# print(df_params_means['tdc']['target_budget'])
# Specify the parameter names for the cost-effectiveness summary
param_names_cost_effectiveness = ["target_budget", "qarys", "qarys_cf", "relevance", "relevance_cf", "n_scientist_equivalent_attendee"]
print(f'filter: {df_params_means[df_params_means["parameter"].isin(param_names_cost_effectiveness)]}')
# Generate a formatted markdown table for cost-effectiveness summary
help.formatted_markdown_table_cost_effectiveness(
    df_params_means, param_names_cost_effectiveness, help.format_number
)
