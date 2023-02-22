# POE Gem Arbitrage

A command-line Path of Exile Regrading Lens / vaal trade calculator.

## What does it do?

TL;DR: It looks up the prices of gems and regrading lenses, and uses alt-quality weights to find profitable gems to use them on. Also, does the same (roughly) for vaal orbs.

## Usage
Requires Python 3.

If you don't have Python -- you can download it here: `https://www.python.org/downloads/`

The following will need to be run in your OS's shell -- PowerShell, Bash, CMD, etc.

    Optional - set up a venv.

    python -m venv .venv
    .\.venv\Scripts\activate (Windows) OR
    source .env\bin\activate (Linux/Mac)

    Then:

    pip install -r requirements.txt
    python .\main.py


The tool will run according to the `settings.ini` file and spit out profitable trades for you to make.
You're going to see something like the text below.

No, there's no GUI, it's just text.

## Reading Lens / Output
Great, you got it to run, and it's spitting out a whole bunch of text. What does it mean?
Let's step through an example line.

    176.50/t: Superior Inspiration Support 20/20 -> Divergent Inspiration Support 20/20, repeat @ 1.801412 tries
    Value: 1113.55, Lens Cost: 765.6001, Gem Cost: 30.0, Gems Listed: Pre: 99 / Post: 98

The first line shows the different gems that make up the trade. In this case, going from Superior Inspiration to Divergent. It lists each gem's (pre- and post-) level and quality, the method used (more on this below) and the estimated amount of lenses needed to succeed.

The second line gives some more granular detail on the costs involved. 'Value' refers to the value of the final gem. 'Lens Cost' refers to the average cost of lenses needed to hit the final gem. 'Gem Cost' refers to the cost of the initial gem. 'Gems Listed' refers to the (estimated) number of gems listed of that exact level and quality from poe.ninja. It functions as a confidence estimator.

## Repeat vs. Single lens Use
What's all this about 'single' vs 'repeat' gem use?

Single refers to buying a gem, using a lens, and discarding the result if it doesn't hit.

Multiple refers to buying a gem, and using lenses on it until you hit the result.


## Efficient Tool Use and Profiteering
#### Single vs. Multiple, continued...
TL;DR: I don't like the single use strategy, I think it's a waste of time in bulk, I go multiple where possible.

One of the most important decisions / considerations when using the tool is the above single vs. multiple lens use methods.

Some trades might be more profitable when using the multiple vs. the single use method. It really all comes down to:
- Quality weights
- QOL for trading and actually making money (seriously)

Usually, gems with alt qualities have basically one valuable quality. I think, in general, it's a waste of time (time is money!) to buy up gems just to use a single lens on them and throw away. Most base gems aren't available in massive bulk quantities easily or cheaply. (Some exceptions like CWDT or Inspiration as of writing this.) This is especially true for gems that have average tries >4 or more.

In most cases there is really no reclamation of value by selling the intermediate product anyways. Sort of like how, sometimes, (back in the old days), you'd sell 5 links on the way to the 6 link. There just is no market for most of the intermediate (not-super-valuable) qualities, and you'll be stuck holding garbage.

#### 'M1' vs. 'M2' sorting methods
TL;DR: You probably want it on 'M2', but if you need to switch over to generating more skill gems to sell, switch it to 'M1'.
Let's start by reviewing how the two methods work.

Method 1 (M1) - Sort and display trades based on the total profit per success.

Method 2 (M2) - Sort and display trades based on the profit per lens use.

These two methods allow you to sort by different metrics depending on how you value your time. Generally speaking, if your trading time is the limiting factor -- you want to optimize for the profit per lens use, because that equates to profit per lens bought.

If, on the other hand, selling gems is the limiting factor, then you want to optimize for the profit per sale, because a sale made is a gem created.

There is a good chunk of skill gems with reasonably high multiple-lens costs (right around 6), that might not have a very high per-lens profit, but have a decently high per-gem profit. If you're making gems faster than you're selling them, you may want to switch over to a slower to create gem.


## Settings
Settings are controlled by and can be found in the `settings.ini` file. Things like which sort method to use, which types of trades to use, single vs. multiple, etc., all live in the settings file.
In addition -- there are some values in the `Controller` class that probably won't need to be changed, but in some cases (like changing match order for levels / qualities).

## Vaal Outputs
The secondary mode of this tool can calculate profits on Vaaling 20/20 gems. There are some drawbacks to this, which will be detailed below, but let's take a look at an example:

    Divergent Tempest Shield (M1: 464.8549999999998/t)
            6.64: 6.40, 6.40, 6.40, 6.40, 7.97, 3.59, 28.16, 6.40

The top line lists the gem (20/20) and the estimated profit per try. The second line lists the prices of the pre-gem first, then each subsequent gem follows this list, in order, for each possible resultant quality:

    0,1 - corrupt
    2,3 - vaal version (or corrupt if no vaal version)
    4 - add up to 10% quality, to a max of 23%
    5 - remove up to 10% quality
    6 - add 1 level
    7 - remove 1 level

Normally all (or almost all) of the profit comes from hitting 21/20 gems.

## Quirks and Issues
#### Vaal operations
Vaal operations really depend on good data, that poe.ninja has a tough time providing. We have to take some liberties with some of the numbers (for example, most gems don't have a price for a 19/20 corrupted gem, but it's usually close enough to a corrupted 20/20, because you can level it up).
In addition -- the most important price data -- the 21/20 corrupted price, is usually low confidence for most gems. The actual price for most 21/20 corrupted gems varies a lot and profit may depend on what price the gems actually sell for.
Also, temple double corrupting isn't implemented, mostly because the data is just not good enough to automatically import.

I would recommend -- if you're serious about making money corrupting or double-corrupting gems, to either make a spreadsheet or some sort of modification that allows for manual price entry, and to validate each outcome's price manually.

#### Lens operations
One small quirk / issue is that, when choosing the most 'reasonable' price / iteration of each gem name, it might choose different levels for the pre- and post- gems. Something like the following:

    111.59/t: Divergent Blood and Sand 4/20 -> Anomalous Blood and Sand 6/20, repeat @ 1.598411 tries
    Value: 478.13, Lens Cost: 239.76165, Gem Cost: 60.0, Gems Listed: Pre: 32 / Post: 98

Usually, this isn't off by enough to totally make the trade unprofitable, but it may warrant a manual check, something like one of the two, depending on which sort method you care about:

    post_gem_price - initial_gem_price - (tries * lens_cost)
    (post_gem_price - initial_gem_price - (tries * lens_cost) / tries)

Much of the other 'quirks' basically come down to -- what strategy do you want to adopt when using this tool, and how do you want to sort the data?

## (Re-) Generating Data Files
#### Multiple Lens Weight Generation
The data file that holds all simulated weights for multiple-style lens use can be recreated with `m_weights.py`.
If you run this file (`python .\m_weights`), it will begin to go through each gem and simulate using regrading lenses on them multiple times, to see how many lenses it takes on average to hit the desirec gem (for each possible operation).

This has the potential to take a while, depending on how long you want to simulate for. The default - 1,000,000 - takes me 900-1000 seconds on a 5950x with all 32 threads. It's probably overkill to run at 1 million, and the algorithm could definitely use some optimization, but it only needs to be run once, and it's pre-generated, so most people shouldn't need to touch it.

If you want to change the number of iterations, you can via the `global_iterations` variable at the top of the script.

It will overwite the existing `m_weights.json` once it finishes, so do be careful.

#### Updating gem weights
The gem weights come from poedb.tw (POE DB), and can be found here: `https://poedb.tw/us/Quality#UnusualGemsQuality`

If needed -- due to an update or otherwise, for `gems.csv` to be recreated / updated, the website will need to be manually scraped / copy / pasted and cleaned up to be formatted right.

The way I do it is just copy/paste the whole table into Excel / Google Sheets and get to deleting rows, cleaning up, etc., to get it to fit. It's not a super clean process, but it only needs to be done once, or at least, when new skill gems are added. It shouldn't break, just new gems won't be calculated for.