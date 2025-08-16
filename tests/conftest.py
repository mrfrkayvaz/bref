from rich.console import Console
console = Console()

def pytest_sessionfinish(session, exitstatus):
    if exitstatus == 0:
        console.print("[bold green]✅ All bref parser tests passed![/bold green]")
    else:
        console.print("[bold red]❌ Some tests failed.[/bold red]")
