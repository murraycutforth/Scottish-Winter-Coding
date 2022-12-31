from io import BytesIO
from pprint import pprint

import matplotlib.pyplot as plt
from src.web_app.mwis_database import data, LOCATIONS, get_raw_forecasts
from src.web_app.mwis_utils import freezing_level_to_numeric, cloud_to_numeric, wind_to_numeric, get_wind_direction, how_wet_to_numeric, how_snowy_to_numeric


def get_main_image():

    freezing_level_data = freezing_level_data_preparation()
    wind_data = wind_data_preparation()
    wind_dir_data = wind_direction_preparation()
    cloud_data = cloud_data_preparation()
    rain_data = rain_data_preparation()
    snow_data = snow_data_preparation()

    num_dates = len(freezing_level_data["west-highlands"][1])


    plt.clf()
    fig, axs = plt.subplots(4, 1, figsize=(num_dates * 0.5, 16), dpi=120)

    # Plot freezing level
    ax = axs[0]
    ax.set_ylim(0, 1500)
    ax.axhline(900, ls="--", c="black", alpha=0.5)
    for loc in LOCATIONS:
        x = freezing_level_data[loc][1]
        ymin = [w[0] for w in freezing_level_data[loc][0]]
        ymax = [w[1] for w in freezing_level_data[loc][0]]
        y_mean = [0.5*(w[0]+w[1]) for w in freezing_level_data[loc][0]]
        y_err = [w[1] - wmean for w, wmean in zip(freezing_level_data[loc][0], y_mean)]
        ax.fill_between(x, ymin, ymax, alpha=0.2)
        ax.errorbar(x, y_mean, yerr=y_err, capsize=5, marker="o", label=loc)
        ax.set_ylabel("Freezing level (m)")
        ax.set_xticklabels(x, rotation=45)

    ax.legend()

    # Plot wind data
    ax = axs[1]
    ax.set_ylim(0, 100)
    for loc in LOCATIONS:
        x = wind_data[loc][1]
        ymin = [w[0] for w in wind_data[loc][0]]
        ymax = [w[1] for w in wind_data[loc][0]]
        y_mean = [0.5*(w[0]+w[1]) for w in wind_data[loc][0]]
        y_err = [w[1] - wmean for w, wmean in zip(wind_data[loc][0], y_mean)]
        ax.fill_between(x, ymin, ymax, alpha=0.2)
        ax.errorbar(x, y_mean, yerr=y_err, capsize=5, marker="o", label=loc)
        ax.set_ylabel("Wind speed (mph)")
        ax.set_xticklabels(x, rotation=45)
    ax.legend()

    # Add wind direction
    ax2 = ax.twinx()
    yticks = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    y_vals = list(range(len(yticks)))
    y_to_val = {y:i for i, y in enumerate(yticks)}
    ax2.set_yticks(y_vals, yticks)
    ax2.set_yticklabels(yticks)

    for loc in LOCATIONS:
        xs = wind_dir_data[loc][1]
        ys = wind_dir_data[loc][0]

        x_extended = []
        y_extended = []
        for x, y_set in zip(xs, ys):
            for y in y_set:
                x_extended.append(x)
                y_extended.append(y_to_val[y])


        ax2.scatter(x_extended, y_extended, marker="x")
    ax2.set_ylabel("Wind direction")


    # Plot cloud data
    ax = axs[2]
    ax.set_ylim(0, 100)
    for loc in LOCATIONS:
        x = cloud_data[loc][1]
        y_min = [w[0] for w in cloud_data[loc][0]]
        y_max = [w[1] for w in cloud_data[loc][0]]
        y_mean = [0.5*(w[0]+w[1]) for w in cloud_data[loc][0]]
        y_err = [w[1] - 0.5*(w[0]+w[1]) for w in cloud_data[loc][0]]
        ax.fill_between(x, y_min, y_max, alpha=0.2)
        ax.errorbar(x, y_mean, yerr=y_err, label=loc, marker="o", capsize=5)
        ax.set_ylabel("% cloud free")
        ax.set_xticklabels(x, rotation=45)
    ax.legend()

    # Plot rain and snow data
    ax = axs[3]
    ax.set_ylim(0, 6)
    ax.set_yticks(range(6))
    ax.set_yticklabels(["dry", "light", "intermittent", "constant", "heavy", "very heavy"])
    ax.text(0, 0.94, "Snow uses solid lines with shading underneath. Rain denoted by dotted lines.", transform=ax.transAxes)
    for loc in LOCATIONS:
        x = rain_data[loc][1]
        y = rain_data[loc][0]
        y_snow = snow_data[loc][0]
        l = ax.plot(x, y, linestyle="--")
        ax.plot(x, y_snow, color=l[0].get_color(), label=loc)
        ax.fill_between(x, y_snow, alpha=0.2, color=l[0].get_color())
        ax.set_ylabel("How rainy/snowy")
        ax.set_xticklabels(x, rotation=45)
    ax.legend()

    fig.tight_layout()

    img = BytesIO()
    plt.savefig(img)
    img.seek(0)
    return img


def freezing_level_data_preparation():
    plot_data = {}
    for loc in LOCATIONS:
        f = get_raw_forecasts(data, loc, "freezing_level")
        f_numeric = [freezing_level_to_numeric(x[1]) for x in f]
        dates = [x[0] for x in f]
        plot_data[loc] = (f_numeric, dates)
    return plot_data


def wind_data_preparation():
    plot_data = {}
    for loc in LOCATIONS:
        f = get_raw_forecasts(data, loc, "how_windy")
        f_numeric = [wind_to_numeric(x[1]) for x in f]
        dates = [x[0] for x in f]
        plot_data[loc] = (f_numeric, dates)
    return plot_data


def wind_direction_preparation():
    plot_data = {}
    for loc in LOCATIONS:
        f = get_raw_forecasts(data, loc, "how_windy")
        f_cat = [get_wind_direction(x[1]) for x in f]
        dates = [x[0] for x in f]
        plot_data[loc] = (f_cat, dates)
    return plot_data


def cloud_data_preparation():
    plot_data = {}
    for loc in LOCATIONS:
        f = get_raw_forecasts(data, loc, "chance_cloud_free")
        f_numeric = [cloud_to_numeric(x[1]) for x in f]
        dates = [x[0] for x in f]
        plot_data[loc] = (f_numeric, dates)
    return plot_data


def rain_data_preparation():
    plot_data = {}
    for loc in LOCATIONS:
        f = get_raw_forecasts(data, loc, "how_wet")
        f_numeric = [how_wet_to_numeric(x[1]) for x in f]
        dates = [x[0] for x in f]
        plot_data[loc] = (f_numeric, dates)
    return plot_data

def snow_data_preparation():
    plot_data = {}
    for loc in LOCATIONS:
        f = get_raw_forecasts(data, loc, "how_wet")
        f_numeric = [how_snowy_to_numeric(x[1]) for x in f]
        dates = [x[0] for x in f]
        plot_data[loc] = (f_numeric, dates)
    return plot_data




get_main_image()
