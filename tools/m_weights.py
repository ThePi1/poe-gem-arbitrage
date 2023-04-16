import csv
from p_tqdm import p_map
import random
import time
import json

v2_weights_m1 = {}
gem_types = ['Superior', 'Anomalous', 'Divergent', 'Phantasmal']
gem_file = "data/gems.csv"
global_iterations = 1000000

def import_gem_weights(_gem_file):
  with open(_gem_file) as gemsfile:
    reader = csv.reader(gemsfile, delimiter=',', quotechar='|')
    line_count = 0
    for row in reader:
      line_count += 1
      if row[0] not in v2_weights_m1:
        v2_weights_m1[row[0]] = {}
      v2_weights_m1[row[0]][row[1]] = int(row[2])


def gemcalc(a, start_type, end_type):
  cur = start_type
  end = end_type
  num = 0

  while cur != end:
    prob_floor = 0
    prob_top = 0
    r = random.random()
    num += 1
    nextgems = {i: a[i] for i in a if i != cur}
    probsum = sum(nextgems.values())
    gem_and_prob_range = {}
    for gem in nextgems.items():
      prob_floor = prob_top  
      prob_top = prob_floor + (gem[1] / probsum)
      gem_and_prob_range[gem[0]] = (prob_floor, prob_top) 

    chosen_gem = ''
    for gem in gem_and_prob_range.items():
      if gem[1][0] <= r < gem[1][1]: 
        chosen_gem = gem[0]

    if chosen_gem == end:
      return num
    else:
      cur = chosen_gem


def lenses_to_hit(gem_name):
  iterations = global_iterations  # This will take about 900-1000 seconds @ 1million on 5950x with 32 threads in the pool
  m2_weights_ = {}
  import_gem_weights(gem_file)
  pruned_start = [i for i in gem_types if i in v2_weights_m1[gem_name].keys()]
  for start_type in pruned_start:
    pruned_end = [i for i in pruned_start if i != start_type]
    for end_type in pruned_end:
      lenses_used = 0
      for i in range(iterations):
        lenses_used += gemcalc(v2_weights_m1[gem_name], start_type, end_type)
      m2_weights_[(gem_name, start_type, end_type)] = lenses_used / iterations
  return m2_weights_


def p_export(item, filename):
  gem_map = {"gems": []}
  for gem in item.items():
    gem_map['gems'].append({"name": gem[0][0], "from_gem": gem[0][1], "to_gem": gem[0][2], "tries": gem[1]})

  with open(filename, 'w') as m2_json_file:
    m2_json_file.write(json.dumps(gem_map))


def calc_m2_weights():
  start_time = time.time()
  all_m2_weights = {}

  out = p_map(lenses_to_hit, list(v2_weights_m1.keys()))
  for m2_gem_weight in out:
    all_m2_weights.update(m2_gem_weight)
  p_export(all_m2_weights, "data/m_weights.json")
  end_time = time.time()
  print('Done in {:.4f} seconds'.format(end_time - start_time))


def main():
  import_gem_weights(gem_file)
  calc_m2_weights()


if __name__ == '__main__':
  main()
