import json
import os
from shutil import copyfile

messages = []
for root, dirs, files in os.walk('./json'):
    for name in files:
        if name.endswith((".json")):
            src_file_path = os.path.join(root,name)
            convo_name = root.split('\\')[-1]

            with open(src_file_path) as json_file:  
                data = json.load(json_file)
                print(src_file_path)
                for m in data['messages']:
                    message = {}
                    message['title'] = data['title']
                    message['participants'] = len(data['participants'])
                    content = ''
                    try:
                        content = m['content']
                    except Exception as e:
                        if m['type'] == 'Generic':
                            try:
                                content = m['photos'][0]['uri']
                                m['type'] = 'Photo'
                            except Exception as e:
                                try:
                                    content = m['sticker']['uri']
                                    m['type'] = 'Sticker'
                                except Exception as e:
                                    try:
                                        content = m['files'][0]['uri']
                                        m['type'] = 'File'
                                    except Exception as e:
                                        try:
                                            content = m['gifs'][0]['uri']
                                            m['type'] = 'Gif'
                                        except Exception as e:
                                            try:
                                                content = m['plan']['title']
                                                m['type'] = 'Plan'
                                            except Exception as e:
                                                try:
                                                    content = m['videos'][0]['uri']
                                                    m['type']='Video'
                                                except Exception as e:
                                                    try:
                                                        content = m['audio_files'][0]['uri']
                                                        m['type']='Audio'
                                                    except Exception as e:
                                                        print(m)
                    message['message'] = content
                    message['type'] = m['type']
                    message['unixTimestamp'] = m['timestamp_ms']
                    message['sender'] = m['sender_name']
                    messages.append(message)

with open("messages.json", "w", encoding='utf-8') as text_file:
    json.dump(messages, text_file) 
            