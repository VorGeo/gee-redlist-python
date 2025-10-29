import sys
from ee_auth import print_authentication_status


def main():
    """Main entry point for gee-redlist-python CLI."""
    print("Hello from gee-redlist-python!")

    # If --test-auth flag is provided, test Earth Engine authentication
    if len(sys.argv) > 1 and sys.argv[1] == '--test-auth':
        print("\nTesting Earth Engine authentication...")
        print_authentication_status()
        return

    print("\nUsage:")
    print("  python main.py --test-auth    Test Earth Engine authentication")


if __name__ == "__main__":
    main()
