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
    cd src
    python .\gem-arbitrage.py

(Make sure you run it from the `src` folder. It's a little picky with file paths...)

The tool will run according to the `settings.ini` file and spit out profitable trades for you to make.

If you want, you can run the script / executable with the `--nogui` flag to only output a text version with the same data as the GUI.

## Font
This section calculates the profitability of using the Lab font. For now, there are two outcomes that are supported:
- Transform a Skill Gem to be a random Transfigured Gem of the same colour (Font - By Color)
- Transform a non-Transfigured Skill Gem to be a random Transfigured version (Font - By Gem)

In the future, other options might be supported.
This tool does assume equal weighting amongst transfigured gems for the purposes of the divine font. If there is any evidence to support the contrary, please reach out and this can be adjusted accordingly.

## Corrupts
Each line here represents the corruption of a gem for profit. As of right now, it only supports single corrupts.
It shows profit and a breakdown of each corruption outcome's price. Recall the following outcomes, each 1-8 evenly weighted:

    1, 2 - Corrupt
    3, 4 - Vaal version (or corrupt if no vaal version)
    5 - Add up to 10% quality, to a max of 23%
    6 - Remove up to 10% quality
    7 - Add 1 level
    8 - Remove 1 level

Normally, all (or almost all) of the profit comes from hitting 21/20 gems.

### Known issues with corruption calculations
- Exceptional gems (Empower / Enlighten / Enhance) are not being included in the list
- Vaal outcome data is wrong for transfigured gems that also have a Vaal version (this is due to a lack of cost data from poe.ninja). For now, it just assumes the cost of the vaal outcome is equal to the cost of the brick outcome.
- Generally unreliable or wrong cost data for many gem corruption outcomes. Additionally, some gems (rarely) are desirable in specific quality or level that poe.ninja doesn't account for, that would significantly impact the profitability of the operation

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

## GUI
The GUI is currently created using PyQt6 and laid out using the Qt Designer tool.

You can get this by `pip install pyqt6-tools` and then launch by `pyqt6-tools designer`.

`.\tools\update_gui_py.ps1` is ran from the `src` folder to compile the `.ui` files into their `.py` counterparts.
If you're not developing on Windows feel free to skip this (or make an analogue to it), and just run the commands yourself as needed:

`pyuic6 -o gui_main.py gui_main.ui`

`pyuic6 -o gui_about.py gui_about.ui`

`pyuic6 -o gui_updates.py gui_updates.ui`

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

## In Conclusion
Please feel free to open an issue on this project to reach out with fixes / bugs / suggestions.
<br/><br/><br/>
Still sane, exile?