"""
NASAの実写画像(昼の地球 = Blue Marble / 夜の地球 = Black Marble)を
現在の太陽の位置に基づいて合成し、正射図法(地球儀の見た目)で出力する。

出力: docs/map.jpg (GitHub Pages で公開するフォルダ)
補助画像は assets/ に一度だけ保存し、以降はダウンロードせず使い回す。
"""

import os
import math
from datetime import datetime, timezone

import numpy as np
import requests
from PIL import Image

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

# --- 設定 ---------------------------------------------------------

DAY_IMAGE_URL = (
    "https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57735/"
    "land_ocean_ice_cloud_2048.jpg"
)
NIGHT_IMAGE_URL = (
    "https://eoimages.gsfc.nasa.gov/images/imagerecords/55000/55167/"
    "earth_lights_lrg.jpg"
)

ASSETS_DIR = "assets"
DAY_IMAGE_PATH = os.path.join(ASSETS_DIR, "day.jpg")
NIGHT_IMAGE_PATH = os.path.join(ASSETS_DIR, "night.jpg")

# 視点の中心(固定)。日本付近を中心にした地球儀にしています。
CENTRAL_LONGITUDE = 140.0
CENTRAL_LATITUDE = 20.0

OUTPUT_SIZE = (1200, 1200)  # ピクセル(正方形)


# --- 基礎画像の取得(初回のみダウンロードし、以降は再利用) -------------

def ensure_base_images():
    os.makedirs(ASSETS_DIR, exist_ok=True)

    if not os.path.exists(DAY_IMAGE_PATH):
        _download(DAY_IMAGE_URL, DAY_IMAGE_PATH)

    if not os.path.exists(NIGHT_IMAGE_PATH):
        _download(NIGHT_IMAGE_URL, NIGHT_IMAGE_PATH)


def _download(url, path):
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    with open(path, "wb") as f:
        f.write(response.content)


# --- 昼夜の合成 -----------------------------------------------------

def build_composite_image():
    day_img = Image.open(DAY_IMAGE_PATH).convert("RGB")
    night_img = Image.open(NIGHT_IMAGE_PATH).convert("RGB")

    # 解像度をそろえる
    size = (2048, 1024)
    day_img = day_img.resize(size)
    night_img = night_img.resize(size)

    day_arr = np.asarray(day_img).astype(np.float32)
    night_arr = np.asarray(night_img).astype(np.float32)

    width, height = size
    lons = np.linspace(-180, 180, width)
    lats = np.linspace(90, -90, height)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    now = datetime.now(timezone.utc)
    sub_lon, sub_lat = _subsolar_point(now)

    elevation = _solar_elevation(lat_grid, lon_grid, sub_lat, sub_lon)

    # 薄明(トワイライト)を含めた、なめらかな昼夜の切り替え
    twilight_deg = 8.0
    alpha = np.clip((elevation + twilight_deg) / (2 * twilight_deg), 0.0, 1.0)
    alpha = alpha[:, :, np.newaxis]  # RGB全チャンネルに適用

    composite = day_arr * alpha + night_arr * (1.0 - alpha)
    composite = np.clip(composite, 0, 255).astype(np.uint8)

    return Image.fromarray(composite), sub_lon, sub_lat


def _subsolar_point(dt):
    """現在時刻(UTC)から、太陽が真上にくる地点(緯度・経度)を概算する。"""
    day_of_year = dt.timetuple().tm_yday
    declination = 23.44 * math.sin(math.radians(360 / 365 * (day_of_year - 81)))

    decimal_hour = dt.hour + dt.minute / 60 + dt.second / 3600
    # 正午(UTC)に経度0度が正午になる、という近似(均時差は無視)
    sub_lon = (12 - decimal_hour) * 15
    sub_lon = ((sub_lon + 180) % 360) - 180

    return sub_lon, declination


def _solar_elevation(lat_grid, lon_grid, sub_lat, sub_lon):
    """各地点における太陽高度(度)を概算する。"""
    lat_r = np.radians(lat_grid)
    sub_lat_r = math.radians(sub_lat)
    delta_lon_r = np.radians(lon_grid - sub_lon)

    sin_elev = (
        np.sin(lat_r) * math.sin(sub_lat_r)
        + np.cos(lat_r) * math.cos(sub_lat_r) * np.cos(delta_lon_r)
    )
    return np.degrees(np.arcsin(np.clip(sin_elev, -1.0, 1.0)))


# --- 正射図法(地球儀)として描画 --------------------------------------

def render_globe(composite_image):
    fig = plt.figure(
        figsize=(OUTPUT_SIZE[0] / 150, OUTPUT_SIZE[1] / 150),
        dpi=150,
        facecolor="#05070d",
    )
    projection = ccrs.Orthographic(
        central_longitude=CENTRAL_LONGITUDE,
        central_latitude=CENTRAL_LATITUDE,
    )
    ax = plt.axes(projection=projection)
    ax.set_global()
    ax.set_facecolor("#05070d")

    ax.imshow(
        np.asarray(composite_image),
        origin="upper",
        extent=(-180, 180, -90, 90),
        transform=ccrs.PlateCarree(),
        interpolation="bicubic",
    )

    # 地球儀の輪郭を薄く光らせる
    ax.spines["geo"].set_edgecolor("#4a6fa5")
    ax.spines["geo"].set_linewidth(1.2)

    ax.set_axis_off()

    os.makedirs("docs", exist_ok=True)
    plt.savefig(
        "docs/map.jpg",
        bbox_inches="tight",
        pad_inches=0,
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)


def main():
    ensure_base_images()
    composite_image, _, _ = build_composite_image()
    render_globe(composite_image)


if __name__ == "__main__":
    main()
