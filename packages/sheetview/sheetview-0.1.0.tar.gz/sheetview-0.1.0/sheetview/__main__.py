from .viewer import render_file

def main():
    import argparse
    parser = argparse.ArgumentParser(description="View CSV/XLSX files in terminal")
    parser.add_argument("path", help="Path to file (CSV or XLSX)")
    parser.add_argument("--sheet", help="Sheet name (for XLSX files)", default=None)
    parser.add_argument("--max-rows", type=int, help="Max rows to display", default=50)
    args = parser.parse_args()

    render_file(args.path, args.sheet, args.max_rows)

if __name__ == "__main__":
    main()
