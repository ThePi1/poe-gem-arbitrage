import csv
import json
import os
from configparser import ConfigParser
import traceback
import requests
import datetime
from os import path

# Import simulated ("multiple" method) weights
def import_sim_json(file):
  with open(file, 'r') as m2_file:
    j = json.load(m2_file)
    json_out = {}
    for gem in j['gems']:
      json_out[(gem['name'], gem['from_gem'], gem['to_gem'])] = gem['tries']
    return json_out

# Parse string to boolean
def is_true(val):
  val = val.lower()
  if val in ('y', 'yes', 't', 'true', 'on', '1'):
    return True
  elif val in ('n', 'no', 'f', 'false', 'off', '0'):
    return False
  else:
    raise ValueError("invalid truth value %r" % (val,))

# Set up config parser and read in the settings file
parser = ConfigParser()
parser.read('data/settings.ini')

# The controller holds most of the data and methods used to calculate trades.
class Controller:
  # Initialize data structures
  simulated_weight_filename = str(parser.get('filepaths', 'simulated_weight_filename'))
  simulated_weights = import_sim_json(simulated_weight_filename)
  lens_weights = {}
  all_lens_operations = []
  all_corrupt_operations = []
  results = []
  gems = []
  gems_dict = {}

  include_methods_in_results = []
  include_types_in_results = []

  # It looks a bit arcane, but these determine the priority of levels and qualities when determining the price of a gem.
  # The goal here is to ask, "for any gem X, what is the most common and reasonable level and quality for that gem, so that we can price it?"
  # Gems are matched level first, then quality.
  # See the readme for more information.
  gem_level_match_order = [20, 16, 17, 18, 19, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
  gem_qual_match_order = [20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

  # I highly doubt different alt qualities will appear, but if they do, it can be updated here.
  # There are also some disallowed gems that don't have alternate qualities.
  # If you have other gems to ignore, you can put it in the DISALLOWED_GEMS list.
  gem_types = ['Superior', 'Anomalous', 'Divergent', 'Phantasmal']
  support_gem_signifier = "Support"
  DISALLOWED_GEMS = ['Enhance Support', 'Empower Support', 'Enlighten Support', 'Elemental Penetration Support']

  # Parse the settings.ini file for the following settings
  try:
    ninja_json_filename               = str(parser.get('filepaths', "ninja_json_filename"))
    ninja_json_currency_filename      = str(parser.get('filepaths', "ninja_json_currency_filename"))
    gem_file                          = str(parser.get('filepaths', "gem_file"))
    API_URL                           = str(parser.get('filepaths', 'api_url'))
    CUR_API_URL                       = str(parser.get('filepaths', 'cur_api_url'))
    prime_lens_price                  = int(parser.get('market_settings', 'prime_lens_price'))
    secondary_lens_price              = int(parser.get('market_settings', 'secondary_lens_price'))
    max_data_staleness                = int(parser.get('general', 'max_data_staleness'))
    DISABLE_OUT                       = not is_true(parser.get('general', 'debug_messages'))
    print_trades                      = is_true(parser.get('general', 'print_trades'))
    print_corrupts                    = is_true(parser.get('general', 'print_corrupts'))
    pull_currency_prices              = is_true(parser.get('general', 'pull_currency_prices'))
    MAX_RESULTS                       = int(parser.get('general', 'max_results'))
    DIV_PRICE                         = int(parser.get('market_settings', 'divine_price'))
    reverse_console_listings          = is_true(parser.get('general', 'reverse_console_listings'))
    gem_operation_price_floor         = int(parser.get('general', "gem_operation_price_floor"))
    corrupt_operation_price_floor     = int(parser.get('general', "corrupt_operation_price_floor"))
    LOW_CONF_COUNT                    = int(parser.get('general', "low_confidence_count"))
    LENS_SORT_METHOD                  = str(parser.get('general', 'lens_sort_method')).upper()
    display_single_lens_trades        = is_true(parser.get('general', 'display_single_lens_trades'))
    display_repeat_lens_trades        = is_true(parser.get('general', 'display_repeat_lens_trades'))
    display_primary_lens_trades       = is_true(parser.get('general', 'display_primary_lens_trades'))
    display_secondary_lens_trades     = is_true(parser.get('general', 'display_secondary_lens_trades'))

    # Set up lists from settings
    if display_single_lens_trades: include_methods_in_results.append("single")
    if display_repeat_lens_trades: include_methods_in_results.append("repeat")
    if display_primary_lens_trades: include_types_in_results.append("Primary")
    if display_primary_lens_trades: include_types_in_results.append("Secondary")

  except Exception as e:
    print(f"Error loading settings.ini file. Please check the exception below and the corresponding entry in the settings file.\nMost likely, the format for your entry is off. Check the top of settings.ini for more info.\n\n{traceback.format_exc()}")
    exit()

  # Fetch URL to file (with some error catching)
  def fetch(self, filename, url):
    do_fetch = True
    try:
      if path.exists(filename):
        modify_time = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
        current_time = datetime.datetime.now()
        delta = (current_time - modify_time).total_seconds()
        if delta < Controller.max_data_staleness:
          do_fetch = False
          if not self.DISABLE_OUT: print(f"Data is {int(delta)}s old, skipping a new fetch.")
    except Exception as e:
      if not self.DISABLE_OUT: print("ERROR: Error determining poe.ninja data staleness. Pulling new data.")
    try:
      if do_fetch:
        if not self.DISABLE_OUT: print("Fetching new data from poe.ninja...")
        response = requests.get(url)
        if path.exists(filename):
          if not self.DISABLE_OUT: print("File already exists, deleting.")
          os.remove(filename)
        if not self.DISABLE_OUT: print("Fetching complete.")
        f = open(filename, 'w')
        f.write(response.text)
        f.close()
    except Exception as e:
      print(url)
      if not self.DISABLE_OUT: print("ERROR: Error fetching.")
      if not self.DISABLE_OUT: print(e)

  # Load gems and prices from poe.ninja listings into memory
  def load_gems_from_json(self, _file):
    with open(_file) as s_json:
      raw = json.load(s_json)
    for line_item in raw['lines']:
      new_gem = Gem()

      for gem_type in self.gem_types:
        if gem_type in line_item['name']:
          new_gem.name = ' '.join(line_item['name'].split()[1:])
          new_gem.type = gem_type
          break

      if new_gem.type == "":
        new_gem.name = line_item['name']
        new_gem.type = "Superior"

      if 'gemQuality' in line_item:
        new_gem.quality = int(line_item['gemQuality'])
      else:
        new_gem.quality = 0
      new_gem.level = int(line_item['gemLevel'])

      new_gem.count = line_item['count']
      if 'listingCount' in line_item:
        new_gem.listing_count = line_item['listingCount']
      else:
        new_gem.listing_count = 0

      new_gem.chaos_value = line_item['chaosValue']
      if 'corrupted' in line_item:
        new_gem.corrupt = True
      else:
        new_gem.corrupt = False

      self.gems.append(new_gem)
      if new_gem.name not in self.gems_dict:
        self.gems_dict[new_gem.name] = []
      self.gems_dict[new_gem.name].append(new_gem)

    print(f"Loaded {len(self.gems)} gems from poe.ninja.")

  # Import gem weight csv
  def import_gem_weights(self, _gem_file):
    with open(_gem_file) as gemsfile:
      reader = csv.reader(gemsfile, delimiter=',', quotechar='|')
      line_count = 0
      for row in reader:
        line_count += 1
        if row[0] not in Controller.lens_weights:
          Controller.lens_weights[row[0]] = {} 
        Controller.lens_weights[row[0]][row[1]] = int(row[2])
      print(f"Loaded {line_count} gem weights.")

# Import currency prices from file
  def import_currency_prices(self):
    with open(self.ninja_json_currency_filename) as curfile:
      raw = json.load(curfile)
      for line_item in raw['lines']:
        if line_item['currencyTypeName'] == 'Prime Regrading Lens':
          self.prime_lens_price = int(line_item['chaosEquivalent'])

        if line_item['currencyTypeName'] == 'Secondary Regrading Lens':
          self.secondary_lens_price = int(line_item['chaosEquivalent'])

        if line_item['currencyTypeName'] == 'Divine Orb':
          self.DIV_PRICE = int(line_item['chaosEquivalent'])
      if not self.DISABLE_OUT: print(f'Using poe.ninja currency prices:\nPrime: {self.prime_lens_price}c\nSecondary: {self.secondary_lens_price}c\nDivine: {self.DIV_PRICE}c\n')


  # Internal method for retrieving gems of specific attributes
  def get_gems(self, _name, _type=None, _lv=None, _qual=None, _isCorrupt=None):
    _gems = []
    if _name not in self.gems_dict: return []
    for gem in self.gems_dict[_name]:
      if gem.name == _name:
        exclude =\
          (_type is not None and _type != gem.type) or\
          (_lv is not None and _lv != gem.level) or\
          (_qual is not None and _qual != gem.quality) or\
          (_isCorrupt is not None and _isCorrupt != gem.corrupt)

        if not exclude:_gems.append(gem)
    return _gems


  # Internal method for retrieving all gem names
  def get_gem_names(self):
    return list(self.gems_dict.keys())


  # Internal method for determining the most common variant (level / quality) of a gem to determine price
  def choose_gem(self, _gem_type_list, lookup_map_l, lookup_map_q):
    for level in lookup_map_l:
      for quality in lookup_map_q:
        for gem in _gem_type_list:
          if gem.level == level and gem.quality == quality and not gem.corrupt:
            return gem
    if not _gem_type_list:
      return None
    else:
      return _gem_type_list[0]


  # Returns how many tries on average it will take to get from one gem to another
  def get_tries(self, _pre_gem, _post_gem, _method):
    if _method == "single":
      name = _pre_gem.name
      pre_type = _pre_gem.type
      post_type = _post_gem.type
      if not (name in Controller.lens_weights and pre_type in Controller.lens_weights[name] and post_type in
              Controller.lens_weights[name]):
        if not self.DISABLE_OUT: print(f"Warning: {_pre_gem.name} not found in CSV weights")
        return -1
      pre_weight = Controller.lens_weights[name][pre_type]
      post_weight = Controller.lens_weights[name][post_type]
      weight_sum = sum(Controller.lens_weights[name].values())
      chance = post_weight / (weight_sum - pre_weight)
      return 1 / chance

    elif _method == "repeat":
      name = _pre_gem.name
      pre_type = _pre_gem.type
      post_type = _post_gem.type
      tup = (name, pre_type, post_type)
      if tup in Controller.simulated_weights:
        return Controller.simulated_weights[tup]
      else:
        return -1
    else:
      print(f"Error: Invalid method {_method}")
      return -1


  # Main method for doing trade calculations
  def calc(self):
    gem_name_list = self.get_gem_names()
    if not self.DISABLE_OUT: print("Calculating trades...")
    for gem_name in gem_name_list:
      for pre_type in self.gem_types:
        # Corrupt Operation
        corrupt_op = CorruptOperation()
        corrupt_op.control = self

        pre_gem_list = self.get_gems(gem_name, _type=pre_type, _lv=20, _qual=20, _isCorrupt=False)

        if not pre_gem_list:
          pass
        else:
          pre_gem = pre_gem_list[0]
          corrupt_op.pre_gem = pre_gem
          corrupt_op.profit = corrupt_op.get_profit()
          if corrupt_op.profit:
            Controller.all_corrupt_operations.append(corrupt_op)

        for post_type in [g for g in self.gem_types if g != pre_type]:
          pre_gems = self.get_gems(gem_name, _type=pre_type)
          post_gems = self.get_gems(gem_name, _type=post_type)

          if None in pre_gems or None in post_gems:
            continue

          pre_quals = []
          pre_levels = []
          post_quals = []
          post_levels = []

          for gem in pre_gems:
            if gem.quality not in pre_quals: pre_quals.append(gem.quality)
            if gem.level not in pre_levels: pre_levels.append(gem.level)
          for gem in post_gems:
            if gem.quality not in post_quals: post_quals.append(gem.quality)
            if gem.level not in post_levels: post_levels.append(gem.level)

          filtered_pre_level_match_order = [i for i in self.gem_level_match_order if i in pre_levels]
          filtered_pre_qual_match_order = [i for i in self.gem_qual_match_order if i in pre_quals]
          filtered_post_level_match_order = [i for i in self.gem_level_match_order if i in post_levels]
          filtered_post_qual_match_order = [i for i in self.gem_qual_match_order if i in post_quals]

          pre_gem = self.choose_gem(pre_gems, filtered_pre_level_match_order, filtered_pre_qual_match_order)
          post_gem = self.choose_gem(post_gems, filtered_post_level_match_order, filtered_post_qual_match_order)

          if None in [pre_gem, post_gem]:
            continue

          for method in self.include_methods_in_results:
            swap = LensOperation()
            swap.pre_gem = pre_gem
            swap.post_gem = post_gem
            swap.method = method
            swap.sort_method = Controller.LENS_SORT_METHOD
            swap.gem_cost = pre_gem.chaos_value
            swap.tries = self.get_tries(pre_gem, post_gem, method)
            swap.value = post_gem.chaos_value
            Controller.all_lens_operations.append(swap)


  # Sort through all trades calculated and display them based on settings
  def get_profitable_trades(self):
    profitable_trades = [op for op in Controller.all_lens_operations if
                         op.switched_profit()() > self.gem_operation_price_floor and op.tries > 0 and
                         op.obeys_confidence() and op.obeys_vaal() and op.obeys_disallow() and
                         (op.lens_type() in self.include_types_in_results)]

    profitable_trades.sort(key=lambda x: x.switched_profit()(), reverse=not self.reverse_console_listings)
    
    if self.reverse_console_listings:
      return profitable_trades[len(profitable_trades) - min(self.MAX_RESULTS, len(profitable_trades)):]
    else:
      return profitable_trades[:self.MAX_RESULTS]


  # Sort through all vaal operations calculated and display them based on settings
  def get_profitable_vaal(self):
    profitable_vaal = [op for op in Controller.all_corrupt_operations if op.profit > 0 and op.obeys_price_floor()]
    profitable_vaal.sort(key=lambda x: x.profit, reverse=not self.reverse_console_listings)

    if self.reverse_console_listings:
      return profitable_vaal[len(profitable_vaal) - min(self.MAX_RESULTS, len(profitable_vaal)):]
    else:
      return profitable_vaal[:self.MAX_RESULTS]


# Holds data and methods for trades (lens operations)
class LensOperation:
  def __init__(self):
    self.pre_gem = None
    self.post_gem = None
    # "single" or "repeat". 'single' is buy gem, hit, discard if not. 'repeat' is buy, hit until succeed.
    self.method = None
    # "M1" or "M2". M1 is $/gem hit. M2 is $/lens used.
    self.sort_method = None
    self.tries = None
    self.gem_cost = None
    self.value = None

  def __str__(self):
    return self.str_calc(False)

  # Defines how trades are displayed in the console
  def str_calc(self, use_tab):
    out = ""
    tab_char = "\t" if use_tab else ""
    if self.sort_method == "M1":
      out += tab_char
      out += f"{self.profit():.2f}: {self.pre_gem} -> {self.post_gem}, {self.method} @ {self.tries} tries\n"
      out += tab_char
      out += f"Value: {self.value}, Lens Cost: {self.lens_cost()}, Gem Cost: {self.gem_cost}, Gems Listed: Pre: {self.pre_gem.count} / Post: {self.post_gem.count}"

    if self.sort_method == "M2":
      out += tab_char
      out += f"{self.m2_profit():.2f}/t: {self.pre_gem} -> {self.post_gem}, {self.method} @ {self.tries} tries\n"
      out += tab_char
      out += f"Value: {self.value}, Lens Cost: {self.lens_cost()}, Gem Cost: {self.gem_cost}, Gems Listed: Pre: {self.pre_gem.count} / Post: {self.post_gem.count}"

    return out

  def tabbed_output(self):
    return self.str_calc(True)

  def profit(self):
    return self.value - self.lens_cost() - self.gem_cost

  def m2_profit(self):
    return self.profit() / self.tries

  def switched_profit(self):
    if self.sort_method == "M1":
      return self.profit
    else:
      return self.m2_profit

  def lens_cost(self):
    if self.pre_gem.is_support():
      return self.tries * Controller.secondary_lens_price
    else:
      return self.tries * Controller.prime_lens_price

  def obeys_confidence(self):
    return self.pre_gem.count > Controller.LOW_CONF_COUNT and self.post_gem.count > Controller.LOW_CONF_COUNT

  def obeys_vaal(self):
    return not (self.pre_gem.is_vaal() or self.post_gem.is_vaal())

  def obeys_disallow(self):
    return self.pre_gem.is_allowed() and self.post_gem.is_allowed()

  def lens_type(self):
    if self.pre_gem.is_support():
      return "Secondary"
    else:
      return "Primary"


# Holds data and methods for corrupt operations
class CorruptOperation:
  def __init__(self):
    self.pre_gem = None
    # Manually only include 20/20 gems to corrupt for now
    # M1 for single corrupt, M2 for temple double corrupt
    # M2 / double corrupt isn't implemented yet
    self.corrupt_mode = "M1"
    self.control = None
    self.profit = None
    self.all_gems = None

  def __str__(self):
    all_gems_div = [gem.chaos_value / Controller.DIV_PRICE for gem in self.all_gems]
    out = f"{self.pre_gem.short_name()} ({self.corrupt_mode}: {self.profit}/t)\n\t {self.pre_gem.chaos_value / Controller.DIV_PRICE:.2f}: "
    for num in all_gems_div:
      out += f"{num:.2f}, "
    return out[:-2]


  # Determines the profit for corrupting a given gem
  # Really depends on good data, and poe.ninja data is shaky at best
  # Your mileage may vary
  def get_profit(self):
    start_lv = 20
    start_qual = 20
    sum = 0
    named_gems = self.control.get_gems(self.pre_gem.name, _type=self.pre_gem.type)
    named_vaal_gems = self.control.get_gems(f"Vaal {self.pre_gem.name}")
    has_vaal = self.pre_gem.has_vaal()
    gems_0_8 = [None, None, None, None, None, None, None, None]

    for gem in named_gems:
      if gem.level == start_lv and gem.quality == start_qual and gem.corrupt and not gem.is_vaal():
        gems_0_8[0] = gem
        gems_0_8[1] = gem
        continue
      if gem.level == start_lv and gem.quality > start_qual and gem.corrupt and not gem.is_vaal():
        gems_0_8[4] = gem
        continue
      if gem.level == start_lv and gem.quality < start_qual and gem.corrupt and not gem.is_vaal():
        gems_0_8[5] = gem  # This could be better than "just go with the first one" but is ok for now
        continue
      if gem.level == start_lv+1 and gem.quality == start_qual and gem.corrupt and not gem.is_vaal():
        gems_0_8[6] = gem
        continue
      if gem.level == start_lv-1 and gem.quality == start_qual and gem.corrupt and not gem.is_vaal():
        gems_0_8[7] = gem
        continue

    if not has_vaal:
      gems_0_8[2] = gems_0_8[0]
      gems_0_8[3] = gems_0_8[0]
    else:
      for gem in named_vaal_gems:
        if gem.level == start_lv and gem.quality == start_qual and gem.corrupt and gem.is_vaal():
          gems_0_8[2] = gem
          gems_0_8[3] = gem

    if not gems_0_8[7] and gems_0_8[0]:  # If we don't have price for 19/20, use 20/20 corrupt
      gems_0_8[7] = gems_0_8[0]

    # Vaal corrupt outcomes:
    # 0,1 - corrupt
    # 2,3 - vaal version (or corrupt if no vaal version)
    # 4 - add up to 10% quality, to a max of 23%
    # 5 - remove up to 10% quality
    # 6 - add 1 level
    # 7 - remove 1 level

    if None in gems_0_8:
      return None
    else:
      for gem in gems_0_8:
        sum += gem.chaos_value

      self.all_gems = gems_0_8
      return (sum / 8) - self.pre_gem.chaos_value

  def obeys_price_floor(self):
    return self.pre_gem.chaos_value > Controller.corrupt_operation_price_floor


# Hold gem data (defines a gem with specific lv/qual/type)
class Gem:
  def __init__(self):
    self.name = ""
    self.level = -1
    self.quality = -1
    self.type = ""
    self.chaos_value = -1
    self.count = -1
    self.listing_count = -1
    self.weight = -1
    self.corrupt = None

  def __repr__(self):
    return self.__str__()

  def __str__(self):
    return f"{self.type} {self.name} {self.level}/{self.quality}"

  def is_support(self):
    return "Support" in self.name

  def is_vaal(self):
    return "Vaal" in self.name

  def is_allowed(self):
    return not (self.name in Controller.DISALLOWED_GEMS)

  def short_name(self):
    return f"{self.type} {self.name}"

  def has_vaal(self):
    return f"Vaal {self.name}" in Controller.lens_weights


# Main method
def main():
  control = Controller()
  control.fetch(control.ninja_json_filename, control.API_URL)
  if control.pull_currency_prices:
    control.fetch(control.ninja_json_currency_filename, control.CUR_API_URL)
    control.import_currency_prices()
  elif not control.DISABLE_OUT:
      print(f'Using manual currency prices:\nPrime: {control.prime_lens_price}c\nSecondary: {control.secondary_lens_price}c\nDivine: {control.DIV_PRICE}c\n')

  control.load_gems_from_json(control.ninja_json_filename)
  control.import_gem_weights(control.gem_file)
  control.calc()
  profitable_trades = control.get_profitable_trades()
  profitable_vaal = control.get_profitable_vaal()

  if Controller.print_trades:
    print(f"Displaying {len(profitable_trades)} trades.\n")
    for op in profitable_trades:
      print(f"{op}\n")
  if Controller.print_corrupts:
    print(f"{len(Controller.all_corrupt_operations)} valid corrupt operations found.")
    for op in profitable_vaal:
      print(f"{op}\n")


if __name__ == '__main__':
  main()