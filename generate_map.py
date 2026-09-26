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

    # 視点の中心（固定）。日本付近を中心にした地球儀にしています。
    # 好みの地域があれば、この2つの数値を変更してください。
    central_longitude = 140.0
    central_latitude = 20.0

    projection = ccrs.Orthographic(
        central_longitude=central_longitude,
        central_latitude=central_latitude,
    )

    fig = plt.figure(figsize=(8, 8), dpi=150, facecolor="#05070d")
    ax = plt.axes(projection=projection)
    ax.set_global()
    ax.set_facecolor("#05070d")  # 宇宙空間のような黒背景

    # ダークモードの地球儀の見た目（海・陸・国境線・海岸線）
    ax.add_feature(cfeature.OCEAN, facecolor="#0b2b42")
    ax.add_feature(cfeature.LAND, facecolor="#3a4a3f")
    ax.add_feature(cfeature.COASTLINE, linewidth=0.4, edgecolor="#7c8f86")
    ax.add_feature(cfeature.BORDERS, linewidth=0.3, linestyle=":", edgecolor="#5c6b64")

    # 現在時刻に基づく夜側の陰影(昼夜の境界線)
    ax.add_feature(Nightshade(now, color="black", alpha=0.55))

    # 地球儀の輪郭を薄く光らせる
    ax.outline_patch.set_edgecolor("#4a6fa5") if hasattr(ax, "outline_patch") else None
    ax.spines["geo"].set_edgecolor("#4a6fa5")
    ax.spines["geo"].set_linewidth(1.0)

    ax.set_axis_off()

    os.makedirs("docs", exist_ok=True)
    plt.savefig(
        "docs/map.jpg",
        bbox_inches="tight",
        pad_inches=0,
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)


if __name__ == "__main__":
    main()
