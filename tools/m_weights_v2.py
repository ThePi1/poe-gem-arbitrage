# WIP redo of the M2 weights (works really well for gems that don't have 4 quality types)

import csv
import time
import json

v2_weights_m1 = {}
gem_types = ['Superior', 'Anomalous', 'Divergent', 'Phantasmal']
gem_file = "../data/gems.csv"
accuracy = 15

def import_gem_weights(_gem_file):
  with open(_gem_file) as gemsfile:
    reader = csv.reader(gemsfile, delimiter=',', quotechar='|')
    line_count = 0
    for row in reader:
      line_count += 1
      if line_count == 1: continue # Skip first line in CSV
      if row[0] not in v2_weights_m1:
        v2_weights_m1[row[0]] = {}
      v2_weights_m1[row[0]][row[1]] = int(row[2])

weights = {"Superior":1, "Anomalous":1, "Divergent":1, "Phantasmal":1}
start = "Superior"
end = "Divergent"

def calculate_tries(limit, weights, start, end):
  all_paths = []
  for path_length in range(0, limit):
      #print(f"Calculating paths of depth {path_length}")
      paths = recurse_generate(0, path_length , [start], weights, start, end)
      all_paths.append(paths)
  
  total_lens_tries = 0
  for i in range(len(all_paths)):
    #print(all_paths[i])
    for tup in all_paths[i]:
      total_lens_tries += (i+1)*(tup[1])
  return total_lens_tries

def recurse_generate(current_depth, max_depth, current_path, weights, start, end):
  #print(f"recurse_generate {current_depth}, {max_depth}, {current_path}, {weights}, {start}, {end}")
  # Create new list of 'paths below me'
  paths_out = []

  if current_depth == max_depth:
    path_out = current_path + [end]
    chance = 1
    for i in range(len(path_out) - 1):
      from_qual = path_out[i]
      to_qual = path_out[i+1]

      swap_filter_dict = dict(weights)
      swap_filter_dict.pop(from_qual)

      next_chance = weights[to_qual] / sum(swap_filter_dict.values())
      chance *= next_chance
    return [(path_out, chance)]
  else:
    # either weights is 3-long or 4-long
    # if 3-long, branching factor is 1, ie, there is 1 possibility for failure
    # 4 long == 2 possibility for failure = 2 paths to go down

    # Iterate through the non-stop, non-end weights: this is a valid target path aka failure
    filtered_weights = dict(weights)
    if len(current_path) == 0:
      filtered_weights.pop(start)
    else:
      filtered_weights.pop(current_path[-1])
    filtered_weights.pop(end)

    for fail_qual_key,fail_qual_val in filtered_weights.items():
      #print(f"Found fail quality: {fail_qual_key}")
      # Copy current path and add make it the new fail path
      newpath = [el for el in current_path]
      newpath.append(fail_qual_key)
      # Recurse and extend the paths down as far as they go
      new_path = recurse_generate(current_depth + 1, max_depth, newpath, weights, start, end)

      # Add to the paths out
      for p in new_path:
        paths_out.append(p)
    return paths_out
  
def p_export(item, filename):
  gem_map = {"gems": []}
  for gem in item.items():
    gem_map['gems'].append({"name": gem[0][0], "from_gem": gem[0][1], "to_gem": gem[0][2], "tries": gem[1]})

  with open(filename, 'w') as m2_json_file:
    m2_json_file.write(json.dumps(gem_map))  

def calc_m2_weights():
  start_time = time.time()
  all_m2_weights = {}
  for gem in v2_weights_m1.keys():
    for from_type in v2_weights_m1[gem]:
      for to_type in [qual for qual in v2_weights_m1[gem] if qual != from_type]:
        est_tries = calculate_tries(accuracy, v2_weights_m1[gem], from_type, to_type)
        #print(f"{gem}, {from_type[0]}->{to_type[0]}: {est_tries}")
        all_m2_weights[(gem, from_type, to_type)] = est_tries
    print(f"Finished {gem}.")
  #print(all_m2_weights)
  p_export(all_m2_weights, "../data/m_weights_v2.json")
  end_time = time.time()
  print('Done in {:.4f} seconds'.format(end_time - start_time))
  
import_gem_weights(gem_file)
print(v2_weights_m1)
# calc_m2_weights()

out = ""
for i in range(1, 21):
  tries = calculate_tries(i, weights, start, end)
  print(f'{i} levels: {tries}')
  out += f'{{{i},{tries:.2f}}},'

print(out)