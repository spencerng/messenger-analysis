import json
import os
from shutil import copyfile


def create_message(fb_m, title, participants):
    message = dict()
    message["title"] = title
    message["participants"] = participants
    content = str()

    try:
        content = fb_m["content"]
    except Exception:
        if fb_m["type"] == "Generic":
            if "photos" in fb_m.keys():
                content = fb_m["photos"][0]["uri"]
                fb_m["type"] = "Photo"
            elif "sticker" in fb_m.keys():
                content = fb_m["sticker"]["uri"]
                fb_m["type"] = "Sticker"
            elif "files" in fb_m.keys():
                content = fb_m["files"][0]["uri"]
                fb_m["type"] = "File"
            elif "gifs" in fb_m.keys():
                content = fb_m["gifs"][0]["uri"]
                fb_m["type"] = "Gif"
            elif "plan" in fb_m.keys():
                content = fb_m["plan"]["title"]
                fb_m["type"] = "Plan"
            elif "videos" in fb_m.keys():
                content = fb_m["videos"][0]["uri"]
                fb_m["type"] = "Video"
            elif "audio_files" in fb_m.keys():
                content = fb_m["audio_files"][0]["uri"]
                fb_m["type"] = "Audio"
            else:
                print(fb_m)

    message["type"] = fb_m["type"]
    message["unixTimestamp"] = fb_m["timestamp_ms"]
    message["sender"] = fb_m["sender_name"]
    try:
        message["reactions"] = fb_m["reactions"]
    except Exception:
        pass

    message["message"] = content
    return message


def build_message_arr():
    messages = list()
    for root, dirs, files in os.walk("./json"):
        for name in files:
            if not name.endswith(".json"):
                continue
            src_file_path = os.path.join(root, name)
            convo_name = root.split("\\")[-1]

            with open(src_file_path) as json_file:
                data = json.load(json_file)
                print(src_file_path)
                for m in data["messages"]:
                    m_dict = create_message(m, data["title"], len(data["participants"]))
                    messages.append(m_dict)
    return messages


def main():
    with open("messages.json", "w", encoding="utf-8") as text_file:
        json.dump(build_message_arr(), text_file)


if __name__ == "__main__":
    main()
