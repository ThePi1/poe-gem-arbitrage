import csv, json, os, sys, traceback, datetime, ctypes, time
import requests
from os import path
from pathlib import Path
from gui import Gui_MainWindow, GemTableModel
from configparser import ConfigParser
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QHeaderView

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
base_path = Path(__file__).parent
parser.read('data/settings.ini')

# The controller holds most of the data and methods used to calculate trades.
class Controller:
  # Initialize data structures
  # simulated_weight_filename = str(parser.get('filepaths', 'simulated_weight_filename'))
  # simulated_weights = import_sim_json(simulated_weight_filename)
  lens_weights = {}
  vivid_watcher_weights = {}
  gem_attributes = {"int": [], "dex": [], "str": []}
  gem_attributes_flip = {}

  # Font operation 'numbering' is reserved as follows:

  # 1 - Transform a Skill Gem to be a random Transfigured Gem of the same colour
  # 2 - Transform a non-Transfigured Skill Gem to be a random Transfigured version
  # 3 - Exchange a Support Gem for a random Exceptional Gem
  # 4 - Exchange a non-Exceptional Support Gem for its Awakened version
  # 5 - Add +#% quality to a Gem
  # 6 - Add # experience to a Gem
  # 7 - Sacrifice a Gem to gain #% of the gem's total experience stored as your own experience (disabled)
  # 8 - Sacrifice a Gem for Currency Items
  # 9 - Sacrifice a Gem to gain #% of the gem's total experience stored as a Facetor's Lens
  # 10 - Sacrifice a Gem for Treasure Keys
  # 11 - Transform a Corrupted Transfigured Skill Gem to be a random Corrupted Transfigured Skill Gem of the same colour
  # 12 - Transform a Corrupted Skill Gem to be a random Corrupted Skill Gem of the same colour
  
  # all_lens_operations = []

  all_font1_operations = []
  all_font2_operations = []
  all_corrupt_operations = []
  all_watcher_operations = []
  results = []
  gems = []
  gems_dict = {}

  include_methods_in_results = []
  include_types_in_results = []

  # I highly doubt different alt qualities will appear, but if they do, it can be updated here.
  # There are also some disallowed gems that don't have alternate qualities.
  # If you have other gems to ignore, you can put it in the DISALLOWED_GEMS list.
  support_gem_signifier = "Support"
  
  exceptional_gems = ['Enhance Support', 'Empower Support', 'Enlighten Support', 'Awakened Enhance Support', 'Awakened Empower Support', 'Awakened Enlighten Support']
  DISALLOWED_GEMS = exceptional_gems + ['Elemental Penetration Support']

  # Parse the settings.ini file for the following settings
  try:
    ninja_json_filename               = str(parser.get('filepaths', "ninja_json_filename"))
    ninja_json_currency_filename      = str(parser.get('filepaths', "ninja_json_currency_filename"))
    # gem_file                          = str(parser.get('filepaths', "gem_file"))
    vivid_watcher_file                = str(parser.get('filepaths', "vivid_watcher_file"))
    gem_attr_file                     = str(parser.get('filepaths', "gem_attr_file"))
    version_file                      = str(parser.get('filepaths', "version_file"))
    API_URL                           = str(parser.get('filepaths', 'api_url'))
    CUR_API_URL                       = str(parser.get('filepaths', 'cur_api_url'))
    version_url                       = str(parser.get('filepaths', 'version_url'))
    project_url                       = str(parser.get('filepaths', 'project_url'))
    # prime_lens_price                  = int(parser.get('market_settings', 'prime_lens_price'))
    # secondary_lens_price              = int(parser.get('market_settings', 'secondary_lens_price'))
    vivid_watcher_price               = int(parser.get('market_settings', 'vivid_watcher_price'))
    yellow_beast_price                = int(parser.get('market_settings', 'yellow_beast_price'))
    max_data_staleness                = int(parser.get('general', 'max_data_staleness'))
    DISABLE_OUT                       = not is_true(parser.get('general', 'debug_messages'))
    print_font1                       = is_true(parser.get('general', 'print_font1'))
    print_font2                       = is_true(parser.get('general', 'print_font2'))
    print_corrupts                    = is_true(parser.get('general', 'print_corrupts'))
    print_watchers                    = is_true(parser.get('general', 'print_watchers'))
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
    if display_secondary_lens_trades: include_types_in_results.append("Secondary")

  except Exception as e:
    print(f"Error loading settings.ini file. Please check the exception below and the corresponding entry in the settings file.\nMost likely, the format for your entry is off. Check the top of settings.ini for more info.\n\n{traceback.format_exc()}")
    exit()

  def get_version_from_file():
    with open(Controller.version_file) as local_version_file:
      local_version = local_version_file.read()
      return local_version
    
  def get_version_from_remote():
    try:
      latest_version = requests.get(Controller.version_url).text
      return latest_version
    except Exception as e:
      print("Error fetching remote version")
      return ''

  def check_version():
    try:
      print("Checking version...\n")
      latest_version = Controller.get_version_from_remote()
      local_version = Controller.get_version_from_file()
      if local_version != latest_version:
        print(f"Version {local_version} may be out of date!\nLatest version: {latest_version}\n\nPlease visit {Controller.project_url} to download the latest version.")
        print("Or, if running from source, please pull the latest changes via 'git pull'")
      else:
        print(f"Version {local_version} is up to date.")
    except Exception as e:
      print(f"Error checking version: {e}")

  # This may get called before everything else gets initialized
  def get_update_stats():
    project_url = str(parser.get('filepaths', 'project_url'))
    latest_version = Controller.get_version_from_remote()
    local_version = Controller.get_version_from_file()
    if local_version != latest_version:
      update_text = "Program may be out of date!"
    else:
      update_text = "Up to date."
    return (local_version, latest_version, update_text, project_url)

  # Fetch URL to file (with some error catching)
  def fetch(filename, url):
    do_fetch = True
    try:
      if path.exists(filename):
        modify_time = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
        current_time = datetime.datetime.now()
        delta = (current_time - modify_time).total_seconds()
        if delta < Controller.max_data_staleness:
          do_fetch = False
          if not Controller.DISABLE_OUT: print(f"{filename} is {int(delta)}s old, skipping a new fetch.")
    except Exception as e:
      if not Controller.DISABLE_OUT: print("ERROR: Error determining poe.ninja data staleness. Pulling new data.")
    try:
      if do_fetch:
        if not Controller.DISABLE_OUT: print("Fetching new data from poe.ninja...")
        response = requests.get(url)
        if path.exists(filename):
          if not Controller.DISABLE_OUT: print("File already exists, deleting.")
          os.remove(filename)
        if not Controller.DISABLE_OUT: print("Fetching complete.")
        f = open(filename, 'w')
        f.write(response.text)
        f.close()
    except Exception as e:
      print(url)
      if not Controller.DISABLE_OUT: print("ERROR: Error fetching.")
      if not Controller.DISABLE_OUT: print(e)

  # Load gems and prices from poe.ninja listings into memory
  def load_gems_from_json(_file):
    with open(_file) as s_json:
      raw = json.load(s_json)
    for line_item in raw['lines']:
      new_gem = Gem()


      # Set name and type
      name_parts = line_item['name'].rsplit("of", 1)
      if 'tradeFilter' in line_item:
        new_gem.type = name_parts[1].strip(' ')
        new_gem.name = name_parts[0].strip(' ')
      else:
        new_gem.name = line_item["name"]

      # Set attribute, if applicable
      if new_gem.name in Controller.gem_attributes:
        new_gem.attr = Controller.gem_attributes[new_gem.name]

      # Set quality
      if 'gemQuality' in line_item:
        new_gem.quality = int(line_item['gemQuality'])
      else:
        new_gem.quality = 0

      # Set level
      new_gem.level = int(line_item['gemLevel'])

      # Set listing counts
      new_gem.count = line_item['count']
      if 'listingCount' in line_item:
        new_gem.listing_count = line_item['listingCount']
      else:
        new_gem.listing_count = 0

      # Set gem price / chaos value
      new_gem.chaos_value = line_item['chaosValue']

      # Set corrupted status
      if 'corrupted' in line_item:
        new_gem.corrupt = True
      else:
        new_gem.corrupt = False

      Controller.gems.append(new_gem)
      if new_gem.name not in Controller.gems_dict:
        Controller.gems_dict[new_gem.name] = []
      Controller.gems_dict[new_gem.name].append(new_gem)

    print(f"Loaded {len(Controller.gems)} gems from poe.ninja.")

  def import_gem_attr(_attr_file):
    with open(_attr_file) as attr_file:
        reader = csv.reader(attr_file, delimiter=',', quotechar='|')
        line_count = 0
        for row in reader:
          line_count += 1
          if line_count == 1: continue # Skip first line in CSV
          if row[0] not in Controller.gem_attributes[row[1]]:
            Controller.gem_attributes[row[1]].append(row[0]) 
            Controller.gem_attributes_flip[row[0]] = row[1]
        print(f"Loaded {line_count} gem attribute mappings.")

  # Import gem weight csv
  # def import_gem_weights(_gem_file):
  #   with open(_gem_file) as gemsfile:
  #     reader = csv.reader(gemsfile, delimiter=',', quotechar='|')
  #     line_count = 0
  #     for row in reader:
  #       line_count += 1
  #       if line_count == 1: continue # Skip first line in CSV
  #       if row[0] not in Controller.lens_weights:
  #         Controller.lens_weights[row[0]] = {} 
  #       Controller.lens_weights[row[0]][row[1]] = int(row[2])
  #     print(f"Loaded {line_count} gem weights.")

  # Import gem weight csv
  def import_vivid_watcher_weights(_file):
    with open(_file) as w_file:
      reader = csv.reader(w_file, delimiter=',', quotechar='|')
      for row in reader:
        Controller.vivid_watcher_weights[row[0]] = int(row[1])

# Import currency prices from file
  def import_currency_prices():
    with open(Controller.ninja_json_currency_filename) as curfile:
      raw = json.load(curfile)
      for line_item in raw['lines']:
        if line_item['currencyTypeName'] == 'Divine Orb':
          Controller.DIV_PRICE = int(line_item['chaosEquivalent'])
      if not Controller.DISABLE_OUT: print(f'Using poe.ninja currency prices:\nDivine: {Controller.DIV_PRICE}c\n')


  # Internal method for retrieving gems of specific attributes
  def get_gems(_name, _type=None, _lv=None, _qual=None, _isCorrupt=None):
    _gems = []
    if _name not in Controller.gems_dict: return []
    for gem in Controller.gems_dict[_name]:
      if gem.name == _name:
        exclude =\
          (_type is not None and _type != gem.type) or\
          (_lv is not None and _lv != gem.level) or\
          (_qual is not None and _qual != gem.quality) or\
          (_isCorrupt is not None and _isCorrupt != gem.corrupt)

        if not exclude:_gems.append(gem)
    return _gems

  # Returns all valid types for a gem name
  def get_types_by_name(_name):
    valid_gems = Controller.get_gems(_name)
    types = []
    for gem in valid_gems:
      if gem.type not in types:
        types.append(gem.type)
    return types

  # Internal method for retrieving all gem names
  def get_gem_names():
    return list(Controller.gems_dict.keys())


  # Internal method for determining the most common variant (level / quality) of a gem to determine price
  def choose_gem(_gem_type_list, lookup_map_l, lookup_map_q):
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
  # def get_tries(_pre_gem, _post_gem, _method):
  #   if _method == "single":
  #     name = _pre_gem.name
  #     pre_type = _pre_gem.type
  #     post_type = _post_gem.type
  #     if not (name in Controller.lens_weights and pre_type in Controller.lens_weights[name] and post_type in
  #             Controller.lens_weights[name]):
  #       if not Controller.DISABLE_OUT: print(f"Warning: {_pre_gem.name} not found in CSV weights")
  #       return -1
  #     pre_weight = Controller.lens_weights[name][pre_type]
  #     post_weight = Controller.lens_weights[name][post_type]
  #     weight_sum = sum(Controller.lens_weights[name].values())
  #     chance = post_weight / (weight_sum - pre_weight)
  #     return 1 / chance

  #   elif _method == "repeat":
  #     name = _pre_gem.name
  #     pre_type = _pre_gem.type
  #     post_type = _post_gem.type
  #     tup = (name, pre_type, post_type)
  #     if tup in Controller.simulated_weights:
  #       return Controller.simulated_weights[tup]
  #     else:
  #       return -1
  #   else:
  #     print(f"Error: Invalid method {_method}")
  #     return -1




  # Main method for doing trade calculations
  def calc():
    gem_name_list = Controller.get_gem_names()
    if not Controller.DISABLE_OUT: print("Calculating trades...")

    # If applicable, calculate global VW profit
    if Controller.print_watchers:
      WatcherOperation.get_return()

    # If applicable, generate the 3 attribute font1 operations
    for attr in ['str', 'dex', 'int']:
      font1_op = Font1Operation()
      font1_op.attribute = attr
      Controller.all_font1_operations.append(font1_op)
      types = []
      for gem_name in gem_name_list:
        if gem_name in Controller.gem_attributes_flip and Controller.gem_attributes_flip[gem_name] == attr:
          valid_types = Controller.get_types_by_name(gem_name)
          for t in valid_types:
            if t not in types:
              types.append((gem_name, t))
      
      num_types = len(types)
      print(f"Using {num_types} types for font1.")
      for gem_name_type in types:
        candidates = Controller.get_gems(gem_name_type[0], _type=gem_name_type[1])
        post_gem = Controller.choose_gem(candidates, Font1Operation.gem_order, Font1Operation.qual_order)
        font1_op.profit += (post_gem.chaos_value / num_types)
        font1_op.post_gem_list.append(post_gem)
    
    # Font2 now
    for gem_name in gem_name_list:
      valid_types = Controller.get_types_by_name(gem_name)
      gemtypes = []
      for t in valid_types:
        typed_gems = Controller.get_gems(gem_name, t)
        pre_gem = Controller.choose_gem(typed_gems, Font2Operation.gem_order, Font2Operation.qual_order)
        font2_op = Font2Operation()
        Controller.all_font2_operations.append(font2_op)
        font2_op.pre_gem = pre_gem
        gemtypes.append(font2_op)
      sum_profit = 0
      for op in gemtypes:
        sum_profit += op.pre_gem.chaos_value
      for op in gemtypes:
        op.profit = (sum_profit / 3) - op.pre_gem.chaos_value


    for gem_name in gem_name_list:
      # If applicable, generate VW operation for this gem
      if Controller.print_watchers and WatcherOperation.is_valid_vw_by_name(gem_name):
        watcher_op = WatcherOperation()
        watcher_op.pre_gem = WatcherOperation.get_awakened_from_name(gem_name)
        watcher_op.profit = watcher_op.get_profit()
        Controller.all_watcher_operations.append(watcher_op)
      
      # If applicable, generate corrupt operation
      if Controller.print_corrupts:
        corrupt_op = CorruptOperation()

        pre_gem_list = Controller.get_gems(gem_name, _isCorrupt=False)
        pre_gem = Controller.choose_gem(pre_gem_list, CorruptOperation.level_order, CorruptOperation.qual_order)

        if not pre_gem_list:
          pass
        else:
          corrupt_op.pre_gem = pre_gem
          corrupt_op.profit = corrupt_op.get_profit()
          if corrupt_op.profit:
            Controller.all_corrupt_operations.append(corrupt_op)
      
      
      # TODO - Add font1 and font2 calcs here

    # Done!
    if not Controller.DISABLE_OUT: print("Done!\n")


      # for pre_type in Controller.gem_types:
      #   if Controller.print_corrupts:
      #     # Corrupt Operation
      #     corrupt_op = CorruptOperation()

      #     pre_gem_list = Controller.get_gems(gem_name, _type=pre_type, _isCorrupt=False)
      #     pre_gem = Controller.choose_gem(pre_gem_list, CorruptOperation.level_order, CorruptOperation.qual_order)

      #     if not pre_gem_list:
      #       pass
      #     else:
      #       corrupt_op.pre_gem = pre_gem
      #       corrupt_op.profit = corrupt_op.get_profit()
      #       if corrupt_op.profit:
      #         Controller.all_corrupt_operations.append(corrupt_op)

      #   for post_type in [g for g in Controller.gem_types if g != pre_type]:
      #     pre_gems = Controller.get_gems(gem_name, _type=pre_type)
      #     post_gems = Controller.get_gems(gem_name, _type=post_type)

      #     if None in pre_gems or None in post_gems:
      #       continue

      #     pre_quals = []
      #     pre_levels = []
      #     post_quals = []
      #     post_levels = []

      #     for gem in pre_gems:
      #       if gem.quality not in pre_quals: pre_quals.append(gem.quality)
      #       if gem.level not in pre_levels: pre_levels.append(gem.level)
      #     for gem in post_gems:
      #       if gem.quality not in post_quals: post_quals.append(gem.quality)
      #       if gem.level not in post_levels: post_levels.append(gem.level)

      #     filtered_pre_level_match_order = [i for i in Controller.gem_level_match_order if i in pre_levels]
      #     filtered_pre_qual_match_order = [i for i in Controller.gem_qual_match_order if i in pre_quals]
      #     filtered_post_level_match_order = [i for i in Controller.gem_level_match_order if i in post_levels]
      #     filtered_post_qual_match_order = [i for i in Controller.gem_qual_match_order if i in post_quals]

      #     pre_gem = Controller.choose_gem(pre_gems, filtered_pre_level_match_order, filtered_pre_qual_match_order)
      #     post_gem = Controller.choose_gem(post_gems, filtered_post_level_match_order, filtered_post_qual_match_order)

      #     if None in [pre_gem, post_gem]:
      #       continue

      #     for method in Controller.include_methods_in_results:
      #       swap = LensOperation()
      #       swap.pre_gem = pre_gem
      #       swap.post_gem = post_gem
      #       swap.method = method
      #       swap.sort_method = Controller.LENS_SORT_METHOD
      #       swap.gem_cost = pre_gem.chaos_value
      #       swap.tries = Controller.get_tries(pre_gem, post_gem, method)
      #       swap.value = post_gem.chaos_value
      #       Controller.all_lens_operations.append(swap)


  # Sort through all trades calculated and display them based on settings
  # def get_profitable_trades():
  #   profitable_trades = [op for op in Controller.all_lens_operations if
  #                        op.switched_profit()() > Controller.gem_operation_price_floor and op.tries > 0 and
  #                        op.obeys_confidence() and op.obeys_vaal() and op.obeys_disallow() and
  #                        (op.lens_type() in Controller.include_types_in_results)]

  #   profitable_trades.sort(key=lambda x: x.switched_profit()(), reverse=not Controller.reverse_console_listings)
    
  #   if Controller.reverse_console_listings:
  #     return profitable_trades[len(profitable_trades) - min(Controller.MAX_RESULTS, len(profitable_trades)):]
  #   else:
  #     return profitable_trades[:Controller.MAX_RESULTS]

  # def get_profitable_trades():
  #   return []

  def get_profitable_font1():
    profitable_font1 = [op for op in Controller.all_font1_operations]
    profitable_font1.sort(key = lambda x: x.profit, reverse=not Controller.reverse_console_listings)
    return profitable_font1
  
  def get_profitable_font2():
    profitable_font2 = [op for op in Controller.all_font2_operations]
    profitable_font2.sort(key = lambda x: x.profit, reverse=not Controller.reverse_console_listings)
    return profitable_font2

  # Sort through all vaal operations calculated and display them based on settings
  def get_profitable_vaal():
    profitable_vaal = [op for op in Controller.all_corrupt_operations if
                       op.profit > 0 and op.obeys_price_floor() and op.obeys_confidence()]
    profitable_vaal.sort(key=lambda x: x.profit, reverse=not Controller.reverse_console_listings)

    if Controller.reverse_console_listings:
      return profitable_vaal[len(profitable_vaal) - min(Controller.MAX_RESULTS, len(profitable_vaal)):]
    else:
      return profitable_vaal[:Controller.MAX_RESULTS]
    
  # Sort through all vivid watcher operations calculated and display them based on settings
  def get_profitable_watcher():
    profitable_watcher = [op for op in Controller.all_watcher_operations if op.profit != None]
    profitable_watcher.sort(key=lambda x: x.profit, reverse=not Controller.reverse_console_listings)

    if Controller.reverse_console_listings:
      return profitable_watcher[len(profitable_watcher) - min(Controller.MAX_RESULTS, len(profitable_watcher)):]
    else:
      return profitable_watcher[:Controller.MAX_RESULTS]

  # Reset local variables
  def reset():
    Controller.lens_weights = {}
    Controller.vivid_watcher_weights = {}
    Controller.all_font1_operations = []
    Controller.all_font2_operations = []
    Controller.all_corrupt_operations = []
    Controller.all_watcher_operations = []
    Controller.results = []
    Controller.gems = []
    Controller.gems_dict = {}

class Font1Operation:
  gem_order = [20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0]
  qual_order = [20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0]

  def __init__(self):
    self.post_gem_list = []
    self.attribute = None
    self.profit = 0

  def table_format(self):
      return [self.profit, self.attribute, len(self.post_gem_list)]
  
  def __str__(self):
    return f"Profit: {self.profit}, Attribute: {self.attribute}, # possible gems: {len(self.post_gem_list)}"

class Font2Operation:
  gem_order = [20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0]
  qual_order = [20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0]

  def __init__(self):
    self.pre_gem = None
    self.profit = 0

  def table_format(self):
      return [f"{self.profit:.2f}", str(self.pre_gem), self.pre_gem.chaos_value]
  
  def __str__(self):
    return f"Profit: {self.profit:.2f}, Pre Gem: {self.pre_gem.__str__()}, Base Value: {self.pre_gem.chaos_value}"

# Holds data and methods for trades (lens operations)
# class LensOperation:
#   def __init__(self):
#     self.pre_gem = None
#     self.post_gem = None
#     # "single" or "repeat". 'single' is buy gem, hit, discard if not. 'repeat' is buy, hit until succeed.
#     self.method = None
#     # "M1" or "M2". M1 is $/gem hit. M2 is $/lens used.
#     self.sort_method = None
#     self.tries = None
#     self.gem_cost = None
#     self.value = None

#   def __str__(self):
#     return self.str_calc(False)

#   # Defines how trades are displayed in the console
#   def str_calc(self, use_tab):
#     out = ""
#     tab_char = "\t" if use_tab else ""
#     if self.sort_method == "M1":
#       out += tab_char
#       out += f"{self.profit():.2f}: {self.pre_gem} -> {self.post_gem}, {self.method} @ {self.tries} tries\n"
#       out += tab_char
#       out += f"Value: {self.value}, Lens Cost: {self.lens_cost()}, Gem Cost: {self.gem_cost}, Post gems listed: {self.post_gem.count}"

#     if self.sort_method == "M2":
#       out += tab_char
#       out += f"{self.m2_profit():.2f}/t: {self.pre_gem} -> {self.post_gem}, {self.method} @ {self.tries} tries\n"
#       out += tab_char
#       out += f"Value: {self.value}, Lens Cost: {self.lens_cost()}, Gem Cost: {self.gem_cost}, Post gems listed: {self.post_gem.count}"

#     return out
  
#   def table_format(self):
#       return [f"{self.switched_profit()():.2f}", str(self.pre_gem), str(self.post_gem), self.method, self.tries, self.value, self.lens_cost(), self.gem_cost, self.post_gem.count]
    
#   def tabbed_output(self):
#     return self.str_calc(True)

#   def profit(self):
#     return self.value - self.lens_cost() - self.gem_cost

#   def m2_profit(self):
#     return self.profit() / self.tries

#   def switched_profit(self):
#     if self.sort_method == "M1":
#       return self.profit
#     else:
#       return self.m2_profit

#   def lens_cost(self):
#     if self.pre_gem.is_support():
#       return self.tries * Controller.secondary_lens_price
#     else:
#       return self.tries * Controller.prime_lens_price

#   def obeys_confidence(self):
#     return self.pre_gem.count > Controller.LOW_CONF_COUNT and self.post_gem.count > Controller.LOW_CONF_COUNT

#   def obeys_vaal(self):
#     return not (self.pre_gem.is_vaal() or self.post_gem.is_vaal())

#   def obeys_disallow(self):
#     return self.pre_gem.is_allowed() and self.post_gem.is_allowed()

#   def lens_type(self):
#     if self.pre_gem.is_support():
#       return "Secondary"
#     else:
#       return "Primary"


# Holds data and methods for corrupt operations
class CorruptOperation:
  level_order = [20, 16, 17, 18, 19, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
  qual_order = [20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
  def __init__(self):
    self.pre_gem = None
    # Manually only include 20/20 gems to corrupt for now
    # M1 for single corrupt, M2 for temple double corrupt
    # M2 / double corrupt isn't implemented yet
    self.corrupt_mode = "M1"
    self.profit = None
    self.all_gems = None

  def __str__(self):
    if self.all_gems is None:
      all_gems_div = []
    else:
      all_gems_div = [gem.chaos_value / Controller.DIV_PRICE for gem in self.all_gems]
    out = f"{self.pre_gem.short_name()} ({self.corrupt_mode}: {self.profit}/t)\n\t {self.pre_gem.chaos_value / Controller.DIV_PRICE:.2f}: "
    for num in all_gems_div:
      out += f"{num:.2f}, "
    return out[:-2]
  
  
  def table_format(self):
      all_gems = [f"{gem.chaos_value:.2f}" for gem in self.all_gems]
      # Remove #3 and #1 because they are duplicates of each other
      all_gems.pop(3)
      all_gems.pop(1)
      return [f"{self.profit:.2f}", str(self.pre_gem), "Vaal Orb", f"{self.pre_gem.chaos_value:.2f}"] + all_gems

  # Determines the profit for corrupting a given gem
  # Really depends on good data, and poe.ninja data is shaky at best
  # Your mileage may vary
  def get_profit(self):
    start_lv = self.pre_gem.level
    start_qual = self.pre_gem.quality
    sum = 0
    named_gems = Controller.get_gems(self.pre_gem.name, _type=self.pre_gem.type)
    named_vaal_gems = Controller.get_gems(f"Vaal {self.pre_gem.name}")
    has_vaal = self.pre_gem.has_vaal()
    gems_0_8 = [None, None, None, None, None, None, None, None]

    for gem in named_gems:
      if gem.level == start_lv and gem.quality == start_qual and gem.corrupt and not gem.is_vaal():
        gems_0_8[0] = gem
        gems_0_8[1] = gem
      if gem.level == start_lv and gem.quality > start_qual and gem.corrupt and not gem.is_vaal():
        gems_0_8[4] = gem
      if gem.level == start_lv and gem.quality < start_qual and gem.corrupt and not gem.is_vaal():
        gems_0_8[5] = gem  # This could be better than "just go with the first one" but is ok for now
      if gem.level == start_lv+1 and gem.quality == start_qual and gem.corrupt and not gem.is_vaal():
        gems_0_8[6] = gem
      if gem.level == start_lv-1 and gem.quality == start_qual and gem.corrupt and not gem.is_vaal():
        gems_0_8[7] = gem

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
  
  def obeys_confidence(self):
    for gem in self.all_gems:
      if gem.count < Controller.LOW_CONF_COUNT:
        return False
    if self.pre_gem.count < Controller.LOW_CONF_COUNT:
      return False
    
    return True

# Holds data and methods about the use of Vivid Watcher
class WatcherOperation:
  level_priority = [1,2,3,4,5,6]
  qual_priority = [20,0,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1]
  # Average return for all gems
  return_value = None
  def __init__(self):
    self.pre_gem = None
    # For now, the default level is 1 for all these operations
    self.default_level = 1
    self.profit = None

  def __str__(self):
    return f"{self.pre_gem.name}: {self.get_profit():.2f}/try (Base value: {self.pre_gem.chaos_value:.2f})"

  def table_format(self):
    return [f"{self.get_profit():.2f}", self.pre_gem.name, f"{self.pre_gem.chaos_value:.2f}"]

  def get_return():
    debug = False
    working_return_value = 0
    weight_sum = sum(Controller.vivid_watcher_weights.values())
    for name, weight in Controller.vivid_watcher_weights.items():
      chosen_gem = WatcherOperation.get_awakened_from_name(name)
      contribution = chosen_gem.chaos_value * (weight / weight_sum)
      if debug: print(f"Gem {chosen_gem} adds {contribution:.2f} @ {weight/weight_sum:.2f} to total return value.")
      working_return_value += contribution
    WatcherOperation.return_value = working_return_value
    if debug: print(f"Total return: {working_return_value:.2f}")
  
  def get_profit(self):
    if not self.pre_gem:
      return None
    else:
      return self.return_value - self.pre_gem.chaos_value - Controller.vivid_watcher_price - (3 * Controller.yellow_beast_price)
    
  def get_awakened_from_name(awakened_name):
    candidates = Controller.get_gems(awakened_name, _type=None, _lv=None, _qual=None, _isCorrupt=False)
    if len(candidates) < 1:
      print(f"Error - could not find gem {awakened_name} in VW calc.")
      return None
    chosen_gem = WatcherOperation.vw_choose_gem(candidates, WatcherOperation.level_priority, WatcherOperation.qual_priority)
    return chosen_gem
  
  def is_valid_vw_by_name(name):
    banned_gems = ["Empower", "Enlighten", "Enhance"]
    if "Awakened" not in name: return False
    for ban_gem in banned_gems:
      if ban_gem in name:
        return False
    return True

  def vw_choose_gem(gems, lv_prio, q_prio):
    gems.sort(key=lambda x: x.chaos_value, reverse=False)
    return gems[0]

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
    # Only skill gems need attributes, for font1 operations, so not all gems will get this
    self.attr = None

  def __repr__(self):
    return self.__str__()

  def __str__(self):
    if self.has_type():
      return f"{self.name} of {self.type}, {self.level}/{self.quality}"
    else:
      return f"{self.name}, {self.level}/{self.quality}"

  def is_support(self):
    return "Support" in self.name

  def is_vaal(self):
    return "Vaal" in self.name

  def is_allowed(self):
    return not (self.name in Controller.DISALLOWED_GEMS)
  
  def short_name(self):
    if self.has_type():
      return f"{self.name} of {self.type}"
    else:
      return f"{self.name}"

  def has_vaal(self):
    return f"Vaal {self.name}" in Controller.lens_weights
  
  def is_awakened(self):
    return f"Awakened" in self.name
  
  def has_type(self):
    return self.type != ""

def getOutput():
  Controller.reset()
  out = { 'font1': '', 'font2': '', 'corrupt': '', 'wokegem': '', 'table_font1': [], 'table_font2': [], 'table_corrupts': [], 'table_wokegem': [] }
  Controller.fetch(Controller.ninja_json_filename, Controller.API_URL)
  if Controller.pull_currency_prices:
    Controller.fetch(Controller.ninja_json_currency_filename, Controller.CUR_API_URL)
    Controller.import_currency_prices()
  elif not Controller.DISABLE_OUT:
      print(f'Using manual currency prices:\nDivine: {Controller.DIV_PRICE}c\n')

  # Need to load gem attributes before we can load gems
  Controller.import_gem_attr(Controller.gem_attr_file)
  Controller.load_gems_from_json(Controller.ninja_json_filename)
  # Controller.import_gem_weights(Controller.gem_file)
  Controller.import_vivid_watcher_weights(Controller.vivid_watcher_file)
  Controller.calc()
  # profitable_trades = Controller.get_profitable_trades()
  profitable_font1 = Controller.get_profitable_font1()
  profitable_font2 = Controller.get_profitable_font2()
  profitable_vaal = Controller.get_profitable_vaal()
  profitable_watcher = Controller.get_profitable_watcher()

  # Might add these disclaimers back in to the table format some day
  # vaal_disclaimer = "Please take these with a grain of salt. The data used for pricing can be low-confidence.\n\n"
  # wokegem_disclaimer = "Please take these with a grain of salt. I'm not able to verify the gem weightings independently.\nSee the readme for more info.\n\n"

  # if Controller.print_trades:
  #   out['gems'] += f"Displaying {len(profitable_trades)} trades.\n"
  #   for op in profitable_trades:
  #     out['gems'] += f"{op}\n"
  #     out['table_gems'].append(op.table_format())

  if Controller.print_font1:
    out['font1'] += f"Showing {len(profitable_font1)} font (by color) operations.\n"
    for op in profitable_font1:
      out['font1'] += f"{op}\n"
      out['table_font1'].append(op.table_format())  

  if Controller.print_font2:
    out['font2'] += f"Showing {len(profitable_font2)} font (by gem) operations.\n"
    for op in profitable_font2:
      out['font2'] += f"{op}\n"
      out['table_font2'].append(op.table_format())

  if Controller.print_corrupts:
    out['corrupt'] += f"Showing {len(profitable_vaal)} corrupt operations.\n"
    # out['corrupt'] += vaal_disclaimer
    for op in profitable_vaal:
      out['corrupt'] += f"{op}\n"
      out['table_corrupts'].append(op.table_format())

  if Controller.print_watchers:
    out['wokegem'] += f"Showing {len(profitable_watcher)} Vivid Watcher operations.\n"
    # out['wokegem'] += wokegem_disclaimer
    for op in profitable_watcher:
      out['wokegem'] += f"{op}\n"
      out['table_wokegem'].append(op.table_format())
  return out

def runTradesUi(window, app):
  # Set status message to start and process the change so we can see it
  start = time.time()
  window.statusBar().showMessage("Calculating...", 10000)
  app.processEvents()
  
  # Calculate the trades, set up table models, and plug in data
  out = getOutput()
  font1_table_data = {
    'gemdata': out['table_font1'],
    'columns': ['Profit', 'Attribute', "NumPossibleGems"],
    'rows': []
  }
  font2_table_data = {
    'gemdata': out['table_font2'],
    'columns': ['Profit', 'GemName', 'BaseValue'],
    'rows': []
  }
  # gem_table_data = {
  #   'gemdata': out['table_gems'],
  #   'columns': ['Profit', 'Source Gem', 'Target Gem', 'Method', 'Tries', 'Value', 'Lens Cost', 'Gem Cost', 'Target Listings'],
  #   'rows': []
  # }
  corrupt_table_data = {
    'gemdata': out['table_corrupts'],
    'columns': ['Profit', 'Gem Name', 'Method', 'PreCost', 'Brick', 'Vaal', '+Qual', '-Qual', '+Level', '-Level'],
    'rows': []
  }
  wokegem_table_data = {
    'gemdata': out['table_wokegem'],
    'columns': ['Profit', 'Gem Name', 'BaseValue'],
    'rows': []
  }
  # gem_table_model = GemTableModel(gem_table_data)
  font1_table_model = GemTableModel(font1_table_data)
  font2_table_model = GemTableModel(font2_table_data)
  corrupt_table_model = GemTableModel(corrupt_table_data)
  wokegem_table_model = GemTableModel(wokegem_table_data)
  # window.ui.gemTable.setModel(gem_table_model)
  window.ui.font1Table.setModel(font1_table_model)
  window.ui.font2Table.setModel(font2_table_model)
  window.ui.corruptTable.setModel(corrupt_table_model)
  window.ui.wokegemTable.setModel(wokegem_table_model)

  # Set the width of column headings that need to be a bit longer
  # gem_column_width = { 1:180, 2:180, 8:100 }
  corrupt_column_width = { 1:250 }
  wokegem_column_width = { 1:250 }
  font1_column_width   = { 2:120 }
  font2_column_width   = { 1:200 }
  # for k,v in gem_column_width.items():
  #   window.ui.gemTable.setColumnWidth(k, v)
  for k,v in corrupt_column_width.items():
    window.ui.corruptTable.setColumnWidth(k,v)
  for k,v in wokegem_column_width.items():
    window.ui.wokegemTable.setColumnWidth(k, v)
  for k,v in font1_column_width.items():
    window.ui.font1Table.setColumnWidth(k, v)
  for k,v in font2_column_width.items():
    window.ui.font2Table.setColumnWidth(k, v)

  # Done! Set status message
  window.statusBar().clearMessage()
  end = time.time()
  window.statusBar().showMessage(f"Done in {(end - start):.2f}s!", 10000)

def fix_win_taskbar():
  app_id = u'thepi-gemarbitrage'
  ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

# Main method
def main():
  use_gui = not '--nogui' in sys.argv
  if use_gui:
    # Use this on Windows to add the icon back to the taskbar
    # No idea how this works on Mac/Linux for now, haha
    if sys.platform == 'win32':
      fix_win_taskbar()

    # Create the application and main window
    app = QApplication(sys.argv)
    win = Gui_MainWindow()
    ver_current, ver_latest, update_text, project_url = Controller.get_update_stats()

    # Set up triggers that need specific data
    win.ui.actionRun_Trades.triggered.connect(lambda: runTradesUi(win, app))
    win.ui.actionAbout.triggered.connect(lambda: Gui_MainWindow.onAbout(win, ver_current, project_url))
    win.ui.actionUpdateCheck.triggered.connect(lambda: Gui_MainWindow.onUpdateWindow(win, ver_current, ver_latest, project_url, update_text))
    
    win.show()
    runTradesUi(win, app)

    # Run the application's main loop
    sys.exit(app.exec())
  else:
    # TODO - command line version switch
    result_text = getOutput()
    
    for key in result_text:
      if key not in ['table_font1', 'table_font2', 'table_corrupts', 'table_wokegem']:
        print(result_text[key])

    Controller.check_version()

if __name__ == '__main__':
  main()