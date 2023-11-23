# POE Gem Arbitrage

A Path of Exile tool for generating money by changing gems. (Now with GUI!)

## What does it do?

TL;DR: It looks up the prices of gems and regrading lenses, and uses alt-quality weights to find profitable gems to use them on. Also, does the same (roughly) for vaal orbs.

## Usage
Download the latest release and unzip to a separate folder; run the executable.
Release is only for Windows at the moment. Linux users can just run it from source.

If you want to run it from source, which is basically just as easy, you'll need Python installed. If you don't have Python -- you can download it here: `https://www.python.org/downloads/`

The following will need to be run in your OS's shell, in the source folder -- PowerShell, Bash, CMD, etc.

    Optional - set up a venv.

    python -m venv .venv
    .\.venv\Scripts\activate (Windows) OR
    source .env\bin\activate (Linux/Mac)

    Then:

    pip install -r requirements.txt
    python .\src\gem-arbitrage.py


The tool will run according to the `settings.ini` file and spit out profitable trades for you to make.

## Gems
Each line here represents the use of regrading lenses on a gem, with a particular method. The profit listed is, by default, per operation (aka, regrading lens use). This can be changed in the settings.

'Target Listings' refers to the number of listings of the target gem that poe.ninja has estimated to exist at any given time. You can think of this as a confidence number, higher is better.

The rest of the fields should be reasonably straightforward. Prices in chaos.

## Corrupts
Each line here represents the corruption of a gem for profit. As of right now, it only supports single corrupts.
It shows profit and a breakdown of each corruption outcome's price. Recall the following outcomes, each 1-8 evenly weighted:

    1,2 - corrupt
    3,4 - vaal version (or corrupt if no vaal version)
    5 - add up to 10% quality, to a max of 23%
    6 - remove up to 10% quality
    7 - add 1 level
    8 - remove 1 level

Normally, all (or almost all) of the profit comes from hitting 21/20 gems.

## Vivid Vultures
The Vivid Vulture is a harvest-memory beast that rerolls Awakened Gems. I can't independently verify the weightings on these gems, so please take these results with a grain (or many) of salt.
Be sure to also update the `vivid_watcher_price` setting as it doesn't yet pull data from any API. It needs to be set manually.

Weights are taken from the "Wealthy Exiles DB" sheet and Discord.

For more information on this, see:
https://www.poewiki.net/wiki/Vivid_Watcher

## Settings
Settings are controlled by and can be found in the `settings.ini` file. Things like which sort method to use, which types of trades to use, single vs. multiple, etc., all live in the settings file.
In addition -- there are some values in the `Controller` class that probably won't need to be changed, but in some cases (like changing match order for levels / qualities).

(Settings menu in the GUI is a planned feature)

## Quirks and Issues
#### Corrupts for Exceptional gems
Currently (due to what more or less amounts to a bug/enhancement that I'm tracking) this tool isn't tracking the corrupt profitability of Empower / Enlighten / Enhance (and their Awakened counterparts).

#### General corruption data reliability
Corruption operations really depend on good data, that poe.ninja has a tough time providing. We have to take some liberties with some of the numbers (for example, most gems don't have a price for a 19/20 corrupted gem, but it's usually close enough to a corrupted 20/20, because you can level it up).
In addition -- the most important price data -- the 21/20 corrupted price, is usually low confidence for most gems. The actual price for most 21/20 corrupted gems varies a lot, and profit may depend on what price the gems actually sell for.
Also, double corrupting isn't implemented (planned feature!), mostly because the data is just not good enough to automatically import.

I would recommend -- if you're serious about making money corrupting or double-corrupting gems, to either make a spreadsheet or some sort of modification that allows for manual price entry, and to validate each outcome's price manually.

#### Regrading lens / gem choice
When choosing the most 'reasonable' price / iteration of each gem name, this tool might choose different levels for the pre- and post- gems. Something like the following:

`Divergent Blood and Sand 4/20 -> Anomalous Blood and Sand 6/20`

Usually, this isn't off by enough to totally make the trade unprofitable, but it may warrant a manual check. 

## (Re-) Generating Data Files
#### Multiple Lens Weight Generation
The data file that holds all simulated weights for multiple-style lens use can be recreated with `m_weights.py`.
Run the tool from the `src/tools/` folder as follows:

    python .\m_weights.py


When ran, it will begin to go through each gem and simulate using regrading lenses on them multiple times, to see how many lenses it takes on average to hit the desired gem (for each possible operation).

This has the potential to take a while, depending on how long you want to simulate for. The default - 1,000,000 - takes 900-1000 seconds on a 5950x with all 32 threads. It's probably overkill to run at 1 million, and the algorithm could definitely use some optimization, but it only needs to be run once, and it's pre-generated, so most people shouldn't need to touch it.

If you want to change the number of iterations, you can via the `global_iterations` variable at the top of the script.

It will overwrite the existing `m_weights.json` once it finishes, so do be careful.

#### Updating gem weights
The gem weights come from poedb.tw (POE DB), and can be found here: `https://poedb.tw/us/Quality#UnusualGemsQuality`

If needed -- due to an update or otherwise, for `gems.csv` to be recreated / updated, the website will need to be manually scraped / copy / pasted and cleaned up to be formatted right.

The way I do it is just copy/paste the whole table into Excel / Google Sheets and get to deleting rows, cleaning up, etc., to get it to fit. It's not a super clean process, but it only needs to be done once, or at least, when new skill gems are added. Old gems / data shouldn't break, just new gems won't be calculated for.

## Packaging binary
Packaged with Python 3.11.6.

Run the packaging tool from the src/ folder as follows:

    python .\tools\pack.py


Alternatively, manually, you can pack as follows:

    pip install pyinstaller
    pyinstaller .\gem-arbitrage.py --onefile --icon=data/icon.ico --hide-console=hide-early
    > Go into dist/ folder and grab gem_arbitrage.exe
    > Copy gem_arbitrage.exe, LICENSE, and data/ folder to new folder.
    > Zip up and release

I don't have it packaged for Linux/Mac on hand, but if you want to, you can.

## More info
See [this guide](guide.md) for more details, tips, and tricks using this tool.

Please feel free to open an issue on this project to reach out with fixes / bugs / suggestions.

I hope you enjoy and may you prosper in any endeavor you come across.