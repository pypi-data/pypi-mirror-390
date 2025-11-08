import typer

from .server import run_sse, run_stdio, run_streamable_http

app = typer.Typer(help="Excel MCP Server")

@app.command()
def sse():
    """Start Excel MCP Server in SSE mode"""
    try:
        run_sse()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Service stopped.")

@app.command()
def streamable_http():
    """Start Excel MCP Server in streamable HTTP mode"""
    try:
        run_streamable_http()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Service stopped.")

@app.command()
def stdio():
    """Start Excel MCP Server in stdio mode"""
    import sys
    import logging

    # In stdio mode, we MUST NOT write anything to stdout except MCP messages
    # All errors should go to stderr or log file
    try:
        run_stdio()
    except KeyboardInterrupt:
        # Log to stderr instead of stdout
        sys.stderr.write("\nShutting down server...\n")
        sys.stderr.flush()
    except Exception as e:
        # Log errors to stderr
        sys.stderr.write(f"\nError: {e}\n")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()

if __name__ == "__main__":
    app() 