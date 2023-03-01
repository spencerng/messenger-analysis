import json
from collections import defaultdict
from glob import glob
from argparse import ArgumentParser
import pandas as pd
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Number of convo initates for someone to appear on the analysis graph
# Used to filter out people you don't often converse with
INIT_THRESH = 10

# We visualize only people who fall within the TOP_N people you talk to
# in any given month
TOP_N = 10

# List of names to filter for on the graph. If empty, defaults to
# the TOP_N criteria
FILTER_LIST = []

def extract_data(main_folder, name="Spencer Ng", anonymity="none"):
    raw_messages = defaultdict(list)
    df = pd.DataFrame()
    names = list()

    chat_transcripts = glob(f"{main_folder}/messages/inbox/**/*.json")

    for transcript in tqdm(chat_transcripts):
        file = open(transcript)
        json_data = json.load(file)
        file.close()

        if len(json_data["participants"]) != 2:
            # If conversation isn't a DM (e.g. a group chat), skip analysis
            continue

        partner = (
            json_data["participants"][0]["name"]
            if json_data["participants"][1]["name"] == name
            else json_data["participants"][1]["name"]
        )

        if anonymity != "none":
            first = partner.split(" ")[0]
            last = partner.split(" ")[-1]
            if anonymity == "full":
                partner = f"{first[0]}{last[0]}"
            elif anonymity == "first":
                partner = f"{first[0]}. {last}"
            elif anonymity == "last":
                partner = f"first {last[0]}."

        for message in json_data["messages"]:
            if "content" in message.keys():
                message["word_count"] = len(message["content"].split(" ")) + 1
            else:
                message["word_count"] = 1

            if "reactions" in message.keys():
                if message["reactions"][0]["reaction"] != "\u00f0\u009f\u0098\u00a2":
                    message["reaction"] = "other"
                else:
                    message["reaction"] = "like"
            else:
                message["reaction"] = "none"

            if anonymity != "none" and message["sender_name"] != name:
                message["sender_name"] = partner

            message["title"] = partner
            if partner not in names:
                names.append(partner)

        
        df = pd.concat([df, pd.DataFrame(json_data["messages"])], ignore_index=True)

    df["timestamp_ms"] = pd.to_datetime(df["timestamp_ms"], unit="ms")

    return df, names


def analyze_chat_series(message_series, friend, you):
    df = message_series.sort_index()

    initiates = dict()
    response_times = dict()
    for name in [friend, you]:
        initiates[name] = 0
        response_times[name] = list()

    prev_time = None
    prev_speaker = None

    for ts, row in df.iterrows():
        # Wait at most 1.5 days for a response
        if prev_speaker is None or (ts - prev_time).days > 2:
            try:
                initiates[row["sender_name"]] += 1
            except KeyError:
                initiates[row["sender_name"]] = 1
        elif row["sender_name"] == prev_speaker:
            # 10 minutes max for a message chain
            if (ts - prev_time).seconds > 60 * 10:
                try:
                    initiates[row["sender_name"]] += 1
                except KeyError:
                    initiates[row["sender_name"]] = 1
        else:
            time_delta = (ts - prev_time).seconds / 60
            try:
                response_times[row["sender_name"]].append(time_delta)
            except KeyError:
                response_times[row["sender_name"]] = [time_delta]
                print("Skipped", row["sender_name"])

        prev_time = ts
        prev_speaker = row["sender_name"]

    return (
        initiates[friend],
        initiates[you],
        np.mean(response_times[friend]),
        np.mean(response_times[you]),
    )


def plot_multiline(xy_pairs, xlab=str(), ylab=str(), title=str()):
    fig, ax = plt.subplots()
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.title(title)

    lines = list()

    for (x_coords, y_coords, label) in sorted(xy_pairs, key=lambda x: x[2]):
        line = ax.plot(x_coords, y_coords, label=label)
        lines.append(line)

    leg = ax.legend()
    line_dict = dict()
    for leg_line, orig_line in zip(leg.get_lines(), lines):
        leg_line.set_picker(10)
        line_dict[leg_line] = orig_line

    def onpick(event):
        leg_line = event.artist
        orig_line = line_dict[leg_line][0]
        vis = not orig_line.get_visible()
        orig_line.set_visible(vis)
        if vis:
            leg_line.set_alpha(1.0)
        else:
            leg_line.set_alpha(0.2)
        fig.canvas.draw()

    fig.canvas.mpl_connect("pick_event", onpick)

    plt.show()


def plot_line_series(df, top_n=1):
    s = df.resample("M")["title"].value_counts()

    data = dict()

    top_n_names = top_n_for_month(df, top_n)

    for (time, name), count in s.items():
        if name not in top_n_names:
            continue
        if name not in data.keys():
            data[name] = (list(), list(), name)
        data[name][0].append(time)
        data[name][1].append(count)

    plot_multiline(data.values(), "Time", "# Messages", "Friendships over Time")


def top_n_for_month(df, n):
    s = df.groupby(["month", "title"]).size()

    top_names = set()

    dates = defaultdict(list)

    for i, ((time, title), count) in enumerate(s.items()):
        dates[time].append((title, count))

    for month, series in dates.items():
        top_n = list(sorted(series, key=lambda x: x[1], reverse=True))[:n]
        for name, count in top_n:
            top_names.add(name)

    return top_names


def scatterplot(
    x_series,
    y_series,
    labels=None,
    title=str(),
    xlab=str(),
    ylab=str(),
    regression=True,
):
    sns.scatterplot(x=x_series, y=y_series)
    if labels is not None:
        for i in range(len(labels)):
            plt.text(
                x_series[i] + 0.05,
                y_series[i] + 0.02 * np.mean(y_series),
                labels[i],
                fontsize="x-small",
                ha="center",
            )

    if regression:
        sns.regplot(x=x_series, y=y_series, ci=None)

    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.title(title)
    plt.show()


def months_and_totals(df, top_n=3):
    s = df.groupby(["month", "title"]).size()

    top_n_names = top_n_for_month(df, top_n)
    dates = defaultdict(list)

    for (time, title), count in s.items():
        if title not in top_n_names:
            continue

        dates[title].append(count)

    num_months = list()
    total_messages = list()
    labels = list()

    for name, message_counts in dates.items():
        x = len(message_counts)
        y = sum(message_counts)

        if x <= 5 and y <= 1000:
            continue

        num_months.append(x)
        total_messages.append(y)
        labels.append(name)

    scatterplot(
        num_months,
        total_messages,
        labels,
        "Rapid Friend Making",
        "Months Talking",
        "Total Messages",
    )


def message_imbalances_counts(df):
    your_sent_count = list()
    friend_sent_count = list()
    labels = list()

    print("Message send ratio imbalances")
    for friend in set(df["title"]):
        friend_messages = df[df.sender_name == friend].count()["sender_name"]
        your_messages = df[df.title == friend].count()["sender_name"] - friend_messages

        if friend_messages < 500 and your_messages < 500:
            continue

        if (
            friend_messages / (friend_messages + your_messages) < 0.4
            or friend_messages / (friend_messages + your_messages) > 0.6
        ):
            print(friend, friend_messages / (friend_messages + your_messages))

        friend_sent_count.append(friend_messages)
        your_sent_count.append(your_messages)
        labels.append(friend)

    scatterplot(
        your_sent_count,
        friend_sent_count,
        labels,
        "Friendship Imbalances: # Messages",
        "Your Sent Messages",
        "Their Sent Messages",
    )


def message_imbalances_words(df):
    your_words = list()
    friend_words = list()
    labels = list()

    print("Word ratio imbalances")
    for friend in set(df["title"]):
        friend_total_words = df[df.sender_name == friend]["word_count"].sum()
        your_total_words = (
            df[df.title == friend]["word_count"].sum() - friend_total_words
        )

        if your_total_words < 5000 and friend_total_words < 5000:
            continue

        ratio_friend = friend_total_words / (friend_total_words + your_total_words)

        if ratio_friend < 0.4 or ratio_friend > 0.6:
            print(friend, ratio_friend)

        friend_words.append(friend_total_words)

        your_words.append(your_total_words)
        labels.append(friend)

    scatterplot(
        your_words,
        friend_words,
        labels,
        "Friendship Imbalances: Words Sent",
        "Your Sent Words",
        "Their Sent Words",
    )


def message_reacts(df):
    your_react_count = list()
    friend_react_count = list()
    labels = list()

    for friend in set(df["title"]):
        your_reacts = df[(df.sender_name == friend) & (df.reaction == "other")].count()[
            "sender_name"
        ]
        friend_react = df[
            (df.title == friend) & (df.sender_name != friend) & (df.reaction == "other")
        ].count()["sender_name"]

        if your_reacts < 30 and friend_react < 30:
            continue

        your_react_count.append(your_reacts)

        friend_react_count.append(friend_react)
        labels.append(friend)

    scatterplot(
        your_react_count,
        friend_react_count,
        labels,
        "Emotional Reacts",
        "Your Reacts",
        "Their Reacts",
        regression=False,
    )


def plot_initiates(df, your_name, filter_names=set()):
    you_initiates = list()
    friend_initiates = list()

    you_resps = list()
    friend_resps = list()
    labels = list()

    print("Imbalanced Initiations")
    for friend in set(df["title"]):
        if len(filter_names) != 0 and friend not in filter_names:
            continue

        friend_init, you_init, friend_resp, you_resp = analyze_chat_series(
            dms[dms.title == friend], friend, your_name
        )

        if friend_init < INIT_THRESH and you_init < INIT_THRESH:
            continue


        if you_init > friend_init:
            print(friend, you_init, friend_init)

        you_initiates.append(you_init)
        friend_initiates.append(friend_init)
        you_resps.append(you_resp)
        friend_resps.append(friend_resp)

        labels.append(friend)

    scatterplot(
        you_initiates,
        friend_initiates,
        labels,
        "Starting the Convo: Who Does It?",
        "Your Initiates",
        "Their Initiates",
    )

    scatterplot(
        you_resps,
        friend_resps,
        labels,
        "Caring about the Convo: Are You a Ghost?",
        "Your Avg. Response Time (min)",
        "Their Avg. Response Time (min)",
        regression=False,
    )


if __name__ == "__main__":
    parser = ArgumentParser()
    sns.set_style("darkgrid")
    sns.set()

    parser.add_argument(
        "--data", help="Folder containing all extracted Facebook data", required=True
    )
    parser.add_argument("--name", help="Your name on Facebook", required=True)
    parser.add_argument(
        "--anonymize",
        help="Level of anonymity: anonymize first name, last name, or full name",
        required=False,
        default="none",
        choices=["first", "last", "full", "none"],
    )
    args = parser.parse_args()

    dms, names = extract_data(args.data, args.name, anonymity=args.anonymize)
    print(names)
    dms["month"] = dms["timestamp_ms"].apply(lambda x: "%d/%d" % (x.month, x.year))

    dms = dms.set_index("timestamp_ms")

    if len(FILTER_LIST) == 0:
        filter_names = top_n_for_month(dms, TOP_N)
    else:
        filter_names = FILTER_LIST

    plot_line_series(dms, top_n=1)
    months_and_totals(dms, top_n=TOP_N)
    message_imbalances_counts(dms)
    message_imbalances_words(dms)
    message_reacts(dms)

    plot_initiates(dms, args.name, filter_names)
