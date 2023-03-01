# FB Messenger Analysis

Visualize your messaging data trends in [Tableau](https://www.tableau.com/)

## Downloading your data

1. Go to your Facebook settings
2. Click on "Your Facebook Information" in the sidebar
3. Click on "Download Your Information"
4. Select your desired date range and media quality, ensuring the download format is JSON
5. Under "Your Information," deselect everything besides "Messages"
6. Click "Create File"
7. Once Facebook finishes preparing your data for export, download and extract the ZIP file

## Extracting JSON messages

1. Clone this repository:
    ```
    git clone https://github.com/spencerng/messenger-analysis
    ```
2. Install dependencies with `pip3 install -r requirements.txt`
3. In `json_extractor.py`, replace the `DATA_DIRECTORY` and `WINDOWS` parameters depending on where your messages are stored and if you are running your code on Windows.
3. Run the Python scripts from this directory, downloading dependencies as necessary:
    ```
    python3 json_extractor.py
    python3 json_parser.py
    ```
4. Open the Tableau workbook (`Messenger Analysis.twb`) to begin visualizing your data. If needed, select the `messages.json` file that was generated as your data source.
5. For personal Python analysis (instead of Tableau), run the following:
    ```
    python3 messenger_analysis.py --data <data folder location> --name <name on facebook> \
        [--anonymize {first|last|full|none} (default: none)]
    ```

    Example usage:

    ```
    python3 .\messenger_analysis.py --data . --name "Spencer Ng" \
        --anonymize first
    ```

    The `INIT_THRESH`, `FILTER_LIST`, and `TOP_N` variables can be customized in the code to filter out certain DM conversations. Graphs will display one at a time.
