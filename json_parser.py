import json
import os
from shutil import copyfile
from json_extractor import DATA_DIRECTORY, IS_WINDOWS
from glob import glob


def create_message(fb_m, title, participants):
    message = dict()
    message["title"] = title
    message["participants"] = participants
    content = str()

    try:
        content = fb_m["content"]
    except KeyError:
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
            print("WARNING: Skipping message", fb_m)

    message["unixTimestamp"] = fb_m["timestamp_ms"]
    message["sender"] = fb_m["sender_name"]
    try:
        message["reactions"] = fb_m["reactions"]
    except Exception:
        pass

    message["message"] = content
    return message


def build_message_arr(dir):
    messages = list()
    for root, dirs, files in os.walk(dir):
        for name in files:
            if not name.endswith(".json"):
                continue
            src_file_path = os.path.join(root, name)
            convo_name = root.split("\\" if IS_WINDOWS else "/")[-1]

            with open(src_file_path) as json_file:
                data = json.load(json_file)
                try:
                    for m in data["messages"]:
                        m_dict = create_message(m, data["title"], len(data["participants"]))
                        messages.append(m_dict)
                except KeyError:
                    print("ERROR: Skipping message in", src_file_path)
    return messages


def main():
    message_arr = list()
    for file in glob(f"{DATA_DIRECTORY}/messages*.json"):
        message_arr += json.loads(open(file, "r").read())
    
    message_arr += build_message_arr(f"{DATA_DIRECTORY}/json")
    
    for i, start_block in enumerate(range(0, len(message_arr), 200000)):
        with open(f"college-years/messages{i}.json", "w+", encoding="utf-8") as text_file:
            json.dump(message_arr[start_block:start_block + 200000], text_file)
    


if __name__ == "__main__":
    main()
    # with open("./messages_insta.json", "r", encoding="utf8") as insta:
    #     arr = json.loads(insta.read())
    #     convo_lens = dict()
    #     for convo in arr:
    #         participant = convo["participants"][-1]
    #         convo_lens[participant] = len(convo["conversation"])
    #     print(dict(sorted(convo_lens.items(), key=lambda x: x[1])))
                
        
