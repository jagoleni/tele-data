import os

from lxml import etree

import pandas as pd
import matplotlib.pyplot as plt

DATA_PATH = "XXX"
FIGURES_FOLDER = "XXX"

def plot_message_count_by_name(df):
    plt.figure()
    df = df[~df.name.str.contains("@", na=False)]
    df[["message_id", "name"]].groupby("name").count().plot(kind='bar',
            legend=None)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_FOLDER, "message_count_by_name.jpg"))

def parse_file(html_string):
    data = []
    parser = etree.HTMLParser()
    root = etree.HTML(html_string)
    for element in root.iter():
        if "id" in element.attrib:
            message = {}
            message["message_id"] = element.attrib["id"]
            for child in element.getchildren():
                if element.attrib["class"] == "message service" and \
                    child.attrib["class"] == "body details":
                        message["text"] = child.text.strip()
                        message['type'] = 'service_message'
                if child.attrib["class"] == "body":
                    for grandchild in child.getchildren():
                        if grandchild.attrib["class"] == "from_name":
                            name = grandchild.text.strip()
                            message["name"] = name
                        if grandchild.attrib["class"] == "pull_right date details":
                            message['timestamp'] = grandchild.attrib["title"]
                        if grandchild.attrib["class"] == "text":
                            message['text'] = grandchild.text.strip()
                            message['type'] = 'text'
                        if grandchild.attrib["class"] == "forwarded body":
                            message['type'] = "forwarded_message"
                        if grandchild.attrib["class"] == "media_wrap clearfix":
                            message['type'] = \
                                grandchild.getchildren()[0].attrib["class"].split()[-1]
            if element.attrib["class"] == "message default clearfix joined":
                message["joined_message"] = True
                message["name"] = name
            if element.attrib["class"] == "message default clearfix":
                message["joined_message"] = False
            data.append(message)
    return data

data = []
for fname in os.listdir(DATA_PATH):
    fpath = os.path.join(DATA_PATH, fname)
    if os.path.isfile(fpath) and os.path.splitext(fpath)[-1] == ".html":
        with open(fpath, encoding='utf8') as f:
            data += parse_file(f.read())
df = pd.DataFrame(data)
df["timestamp"] = pd.to_datetime(df["timestamp"])
plot_message_count_by_name(df)
