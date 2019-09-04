# FB Messenger Analysis

Visualize your messaging data trends in [Tableau](https://www.tableau.com/)

## Downloading your data

1. Go to your Facebook settings
2. Click on "Your Facebook Information" in the sidebar
3. Click on "Download Your Information"
4. Select your desired date range and media quality, ensuring the download format is JSON
5. Under "Your Information," deselect everything besides "Messages"
6. Click "Create File"
7. Once Facebook finishes preparing your data for export, download the ZIP file

## Extracting JSON messages

1. Clone this repository:

    git clone https://github.com/spencerng/messenger-analysis

2. Extract the `/messages` directory of the downloaded ZIP file into the repository directory
3. Run the Python scripts, downloading dependencies as necessary:

    python3 json_extractor.py
    python3 json_parser.py

4. Open the Tableau workbook (`Messenger Analysis.twb`) to begin visualizing your data. If needed, select the `messages.json` file that was generated as your data source.