import pandas as pd
from rich.console import Console
from rich.table import Table
import os

console = Console()

def render_file(path, sheet=None, max_rows=50):
    ext = os.path.splitext(path)[1].lower()

    # Load the data
    if ext in [".xls", ".xlsx"]:
        if sheet:
            df = pd.read_excel(path, sheet_name=sheet)
        else:
            # Read all sheets; take the first one by default
            all_sheets = pd.read_excel(path, sheet_name=None)
            first_sheet_name = list(all_sheets.keys())[0]
            df = all_sheets[first_sheet_name]
            console.print(f"[cyan]Displaying first sheet:[/cyan] [bold]{first_sheet_name}[/bold]")
    elif ext == ".csv":
        df = pd.read_csv(path)
    else:
        console.print(f"[red]Unsupported file type: {ext}[/red]")
        return

    # Limit rows
    df = df.head(max_rows)

    # Render using rich
    table = Table(show_header=True, header_style="bold magenta")
    for col in df.columns:
        table.add_column(str(col))

    for _, row in df.iterrows():
        table.add_row(*[str(x) for x in row.values])

    console.print(table)
