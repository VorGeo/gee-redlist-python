"""Example usage of the map.py module to create country maps."""

from gee_redlist.map import create_country_map


def main():
    """Generate example maps for different countries."""

    # # Example 1: Singapore (small island nation)
    # print("Creating map of Singapore...")
    # singapore_path = create_country_map('Singapore', 'singapore_example.png')
    # print(f"✓ Singapore map saved to: {singapore_path}")

    # Example 2: Myanmar (Asian country)
    print("\nCreating map of Myanmar...")
    myanmar_path = create_country_map('Myanmar', 'myanmar_example.png')
    print(f"✓ Myanmar map saved to: {myanmar_path}")

    # # Example 3: Brazil (large South American country)
    # print("\nCreating map of Brazil...")
    # brazil_path = create_country_map('Brazil', 'brazil_example.png')
    # print(f"✓ Brazil map saved to: {brazil_path}")

    # # Example 4: Japan (island nation)
    # print("\nCreating map of Japan...")
    # japan_path = create_country_map('Japan', 'japan_example.png')
    # print(f"✓ Japan map saved to: {japan_path}")

    # # Example 5: Kenya (African country)
    # print("\nCreating map of Kenya...")
    # kenya_path = create_country_map('Kenya', 'kenya_example.png')
    # print(f"✓ Kenya map saved to: {kenya_path}")

    print("\n" + "="*50)
    print("All example maps created successfully!")
    print("="*50)


if __name__ == "__main__":
    main()
