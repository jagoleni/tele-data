import os
import json
import logging
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

DATA_PATH = Path("data/result.json")
FIGURES_FOLDER = Path("figures/")


def plot_posts_over_time(df: pd.DataFrame, fname: str = "posts_over_time.jpg") -> None:
    df_copy = df.copy()
    plt.figure()
    sns.countplot(x="year", data=df_copy)
    plt.title("Total Posts")
    plt.savefig(os.path.join(FIGURES_FOLDER, fname), dpi=300)


def load_data() -> pd.DataFrame:
    with open(DATA_PATH, "r", encoding="utf8") as f:
        messages = json.load(f)["messages"]
    return pd.DataFrame(messages)


def preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df["type"] == "message"]
    df = df.rename(columns={"from": "name"})
    df["reactions_count"] = df["reactions"].apply(
        lambda x: len(x) if isinstance(x, list) else 0
    )
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.strftime("%Y")
    df["year-month"] = df["date"].dt.strftime("%Y-%b")
    return df


def plots(df: pd.DataFrame) -> None:
    plot_posts_over_time(df)


def main() -> None:
    logger.info("Loading data...")
    df = load_data()
    logger.info("Preprocessing data...")
    df = preprocessing(df)
    logger.info("Start plotting...")
    plots(df)
    logger.info("Done!")


if __name__ == "__main__":
    main()
