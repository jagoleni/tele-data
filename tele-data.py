import os

from lxml import etree

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

DATA_PATH = "XXX"
FIGURES_FOLDER = "XXX"


def plot_message_count_by_name(df, names, fname="message_count_by_name.jpg"):
    df_copy = df.copy()
    df_copy = df_copy.loc[df_copy["name"].isin(names)]
    df_copy = df_copy[df_copy["timestamp"] > "2020-01-01 00:00"]
    plt.figure()
    plt.title("Posts by user in 2020")
    sns.countplot(y="name", data=df_copy, order=df_copy["name"].value_counts().index)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_FOLDER, fname), dpi=300)


def plot_posts_over_time(df, names, fname="posts_over_time.jpg"):
    df_copy = df.copy()
    plt.figure()
    df_copy = df_copy.loc[df_copy["name"].isin(names)]
    df_copy = df_copy[df_copy["timestamp"] > "2020-01-01 00:00"]
    df_copy["month"] = df_copy["timestamp"].dt.strftime("%b")
    sns.countplot(y="month", data=df_copy)
    plt.title("Total Posts 2020")
    plt.savefig(os.path.join(FIGURES_FOLDER, fname), dpi=300)


def plot_char_count(df, names, fname="charcount.png"):
    df_copy = df.copy()
    df_copy = df_copy.loc[df_copy["name"].isin(names)]
    df_copy = df_copy[df_copy["type"] == "text"]
    df_copy["character_count"] = df_copy["text"].apply(lambda x: len(x))
    df_copy = df_copy.loc[df_copy["name"].isin(names)]
    plt.figure()
    ax = sns.boxplot(x="name", y="character_count", data=df_copy, showfliers=False)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    plt.title("Character Counts per Message (no outliers)")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_FOLDER, fname), dpi=300)


def plot_char_total(df, names, fname="charcount_total.png"):
    df_copy = df.copy()
    df_copy = df_copy.loc[df_copy["name"].isin(names)]
    df_copy = df_copy[df_copy["type"] == "text"]
    df_copy["character_count"] = df_copy["text"].apply(lambda x: len(x))
    df_copy = df_copy.loc[df_copy["name"].isin(names)]
    df_copy = df_copy.groupby(["name"]).sum()
    df_copy = df_copy.reset_index()
    plt.figure()
    ax = sns.barplot(
        x="name",
        y="character_count",
        data=df_copy,
        order=df_copy.sort_values("character_count").name,
    )
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    plt.title("Total Character Count all Messages ever")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_FOLDER, fname), dpi=300)


def plot_char_total_2020(df, names, fname="charcount_total_2020.png"):
    df_copy = df.copy()
    df_copy = df_copy.loc[df_copy["name"].isin(names)]
    df_copy = df_copy[df_copy["type"] == "text"]
    df_copy = df_copy[df_copy["timestamp"] > "2020-01-01 00:00"]
    df_copy["character_count"] = df_copy["text"].apply(lambda x: len(x))
    df_copy = df_copy.loc[df_copy["name"].isin(names)]
    df_copy = df_copy.groupby(["name"]).sum()
    df_copy = df_copy.reset_index()
    plt.figure()
    ax = sns.barplot(
        x="name",
        y="character_count",
        data=df_copy,
        order=df_copy.sort_values("character_count").name,
    )
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    plt.title("Total Character Count all Messages 2020")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_FOLDER, fname), dpi=300)


def parse_file(html_string):
    data = []
    parser = etree.HTMLParser()
    root = etree.HTML(html_string)
    for element in root.iter():
        if "id" in element.attrib:
            message = {}
            message["message_id"] = element.attrib["id"]
            for child in element.getchildren():
                if (
                    element.attrib["class"] == "message service"
                    and child.attrib["class"] == "body details"
                ):
                    message["text"] = child.text.strip()
                    message["type"] = "service_message"
                if child.attrib["class"] == "body":
                    for grandchild in child.getchildren():
                        if grandchild.attrib["class"] == "from_name":
                            name = grandchild.text.strip()
                            message["name"] = name
                        if grandchild.attrib["class"] == "pull_right date details":
                            message["timestamp"] = grandchild.attrib["title"]
                        if grandchild.attrib["class"] == "text":
                            message["text"] = grandchild.text.strip()
                            message["type"] = "text"
                        if grandchild.attrib["class"] == "forwarded body":
                            message["type"] = "forwarded_message"
                        if grandchild.attrib["class"] == "media_wrap clearfix":
                            message["type"] = (
                                grandchild.getchildren()[0].attrib["class"].split()[-1]
                            )
            if element.attrib["class"] == "message default clearfix joined":
                message["joined_message"] = True
                message["name"] = name
            if element.attrib["class"] == "message default clearfix":
                message["joined_message"] = False
            data.append(message)
    return data


def get_data():
    data = []
    for fname in os.listdir(DATA_PATH):
        fpath = os.path.join(DATA_PATH, fname)
        if os.path.isfile(fpath) and os.path.splitext(fpath)[-1] == ".html":
            with open(fpath, encoding="utf8") as f:
                data += parse_file(f.read())
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%d.%m.%Y %H:%M:%S")
    return df


if __name__ == "__main__":
    names = ["fill_in!"]
    df = get_data()
    plot_message_count_by_name(df, names)
    plot_posts_over_time(df, names)
    plot_char_count(df, names)
    plot_char_total(df, names)
    plot_char_total_2020(df, names)
