"""
昼夜の世界地図（画像）を生成するスクリプト。
GitHub Actions から1時間ごとに実行される想定。
出力: docs/map.jpg （GitHub Pages で公開するフォルダ）
"""

import os
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")  # 画面なしのサーバー環境で描画するための設定
import matplotlib.pyplot as plt

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature.nightshade import Nightshade


def main():
    now = datetime.now(timezone.utc)

    fig = plt.figure(figsize=(10, 5), dpi=150)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_global()

    # 基本的な地図の見た目（海・陸・国境線・海岸線）
    ax.add_feature(cfeature.OCEAN, facecolor="#a9cbe0")
    ax.add_feature(cfeature.LAND, facecolor="#eae6d6")
    ax.add_feature(cfeature.COASTLINE, linewidth=0.4)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3, linestyle=":")

    # 現在時刻に基づく夜側の陰影（昼夜の境界線）
    ax.add_feature(Nightshade(now, alpha=0.35))

    ax.set_axis_off()

    os.makedirs("docs", exist_ok=True)
    plt.savefig(
        "docs/map.jpg",
        bbox_inches="tight",
        pad_inches=0,
    )
    plt.close(fig)


if __name__ == "__main__":
    main()
