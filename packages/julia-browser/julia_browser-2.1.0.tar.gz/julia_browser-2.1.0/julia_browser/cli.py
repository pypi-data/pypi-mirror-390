"""
Julia Browser CLI Entry Point
"""

import sys
import os

# Add the current package to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main CLI functionality
from cli_interface import CLIBrowser, console

def main():
    """Main entry point for Julia Browser CLI"""
    try:
        import click
        
        @click.group()
        @click.version_option(version="1.5.0", prog_name="Julia Browser")
        def cli():
            """🌐 Julia Browser - A Python-based command-line web browser with JavaScript support"""
            pass

        @cli.command()
        @click.argument('url')
        @click.option('--format', default='markdown', help='Output format (markdown, html, json)')
        @click.option('--javascript/--no-javascript', default=True, help='Enable/disable JavaScript execution')
        def browse(url, format, javascript):
            """Browse to a URL and display content"""
            browser = CLIBrowser()
            if format == 'json':
                result = browser.sdk.render_to_markdown(url, execute_js=javascript)
                import json
                console.print_json(json.dumps(result, indent=2))
            else:
                browser.browse_url_enhanced(url)

        @cli.command()
        @click.argument('url')
        @click.option('--format', default='markdown', help='Output format (markdown, html, json)')
        def render(url, format):
            """Render a URL to specified format"""
            browser = CLIBrowser()
            result = browser.sdk.render_to_markdown(url)
            
            if format == 'html':
                console.print(result.get('raw_html', ''), markup=False)
            elif format == 'json':
                import json
                console.print_json(json.dumps(result, indent=2))
            else:
                console.print(result.get('markdown', ''), markup=False)

        @cli.command()
        def interactive():
            """Start interactive browsing mode"""
            browser = CLIBrowser()
            browser.start_interactive_mode()

        # Run the CLI
        cli()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Julia Browser session interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()