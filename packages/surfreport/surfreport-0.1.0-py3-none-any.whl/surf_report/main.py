from surf_report.providers.surfline.surfline import SurflineAPI
from surf_report.providers.surfline.ui import (
    display_combined_spot_report,
    display_region_overview,
    display_regions,
    display_spot_forecast,
    get_user_choice,
)
from surf_report.utils.helpers import (
    parse_arguments,
    sort_regions,
)
from surf_report.utils.logger import setup_logger

logger = setup_logger()
surfline = SurflineAPI()


def handle_search(search: str, verbose=False):
    """Displays a list of search results from the user's query."""
    search_results = surfline.search_surfline(
        search
    )  # Returns a list of SurflineSearchResult objects

    if not search_results:
        print(f"No spots found for {search}")
        return None

    if len(search_results) == 1:
        result = search_results[0]
        breadcrumb_string = " > ".join(result.breadcrumbs)
        if verbose:
            print(f"{breadcrumb_string} ({result.type}) [ID: {result.id}]")
        else:
            print(f"{breadcrumb_string}")
        return result.id  # Return spot ID directly

    print("\nSelect a spot:")
    for i, result in enumerate(search_results):
        breadcrumb_string = " > ".join(result.breadcrumbs)
        if verbose:
            print(f"{i + 1}. {breadcrumb_string} ({result.type}) [ID: {result.id}]")
        else:
            print(f"{i + 1}. {breadcrumb_string}")

    print("0. Back to Main Menu")
    choice = get_user_choice(search_results)

    if choice == 0:
        return None

    selected_result = search_results[choice - 1]
    breadcrumb_string = " > ".join(selected_result.breadcrumbs)
    if verbose:
        print(
            f"\n{breadcrumb_string} ({selected_result.type}) [ID: {selected_result.id}]"
        )
    else:
        print(f"\n{breadcrumb_string}")

    return selected_result.id


def main():
    args = parse_arguments()

    if args.search:
        spot_id = handle_search(args.search_string)
        if spot_id is not None:
            spot_forecast = surfline.get_spot_forecast(spot_id, args.days)
            spot_report = surfline.get_spot_report(spot_id, args.days)
            # display_spot_forecast(spot_forecast)
            # display_spot_report(spot_report)
            display_combined_spot_report(spot_forecast, spot_report)
    else:
        current_region_id = "58f7ed51dadb30820bb38782"
        while True:
            region_data = surfline.get_region_list(current_region_id)

            if not region_data:  # Handle empty response
                print("Failed to fetch region data.")
                continue

            if isinstance(region_data, list):  # Now returns a list of Region objects
                regions = sort_regions(region_data)
            else:
                print("Unexpected region data format.")
                continue

            display_regions(regions, args.verbose)

            choice = get_user_choice(regions)
            if choice == 0:
                print("Returning to the previous region.")
                continue

            current_region = regions[choice - 1]

            if current_region.type == "subregion":
                region_overview = surfline.get_region_overview(current_region.subregion)
                if region_overview:
                    display_region_overview(region_overview)

            current_region_id = current_region.id

            if current_region.type == "spot":
                spot_forecast = surfline.get_spot_forecast(current_region.spot)
                if spot_forecast:
                    display_spot_forecast(spot_forecast)


if __name__ == "__main__":
    main()
