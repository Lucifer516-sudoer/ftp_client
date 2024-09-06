# import os
# import http.server
# import socketserver
# import urllib.parse
# import typer
# from urllib.parse import quote, unquote
# from rich.console import Console
# from rich.progress import Progress
# import socket

# # Rich console for better output
# console = Console()

# # HTML template for directory listing
# DIRECTORY_LISTING_TEMPLATE = """
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Directory listing for {path}</title>
#     <style>
#         body {{ font-family: Arial, sans-serif; padding: 20px; }}
#         table {{ width: 100%; border-collapse: collapse; }}
#         th, td {{ padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }}
#         th {{ background-color: #f4f4f4; }}
#         a {{ text-decoration: none; color: #007bff; }}
#         a:hover {{ text-decoration: underline; }}
#     </style>
# </head>
# <body>
#     <h2>Directory listing for {path}</h2>
#     <table>
#         <thead>
#             <tr>
#                 <th>Name</th>
#                 <th>Size</th>
#                 <th>Last Modified</th>
#             </tr>
#         </thead>
#         <tbody>
#             {files}
#         </tbody>
#     </table>
# </body>
# </html>
# """


# class EnhancedFileHandler(http.server.SimpleHTTPRequestHandler):
#     """HTTP request handler with improved large file handling capabilities and cleaner directory listings."""

#     def list_directory(self, path):
#         """Generate and send a directory listing in a cleaner format."""
#         try:
#             file_list = os.listdir(path)
#         except OSError:
#             self.send_error(403, "No permission to list directory")
#             return None

#         file_list.sort(key=lambda a: a.lower())
#         files_html = ""

#         # Generate file rows
#         for name in file_list:
#             fullname = os.path.join(path, name)
#             display_name = name
#             linkname = quote(name)  # URL encode for correct paths

#             if os.path.isdir(fullname):
#                 display_name = f"{name}/"
#                 linkname += "/"  # append / for directories
#                 size = "-"
#             else:
#                 size = f"{os.path.getsize(fullname)} bytes"
#             last_modified = self.date_time_string(os.path.getmtime(fullname))
#             files_html += f"""
#             <tr>
#                 <td><a href="{linkname}">{display_name}</a></td>
#                 <td>{size}</td>
#                 <td>{last_modified}</td>
#             </tr>
#             """

#         # Send response with custom HTML
#         self.send_response(200)
#         self.send_header("Content-Type", "text/html")
#         self.end_headers()
#         response = DIRECTORY_LISTING_TEMPLATE.format(
#             path=self.path, files=files_html
#         ).encode("utf-8")
#         self.wfile.write(response)

#     def do_GET(self):
#         """Serve a GET request with chunked file reading for large file support."""
#         path = self.translate_path(self.path)
#         path = unquote(path)

#         if os.path.isdir(path):
#             self.list_directory(path)
#             return

#         if not os.path.exists(path):
#             self.send_error(404, "File not found")
#             return

#         file_size = os.path.getsize(path)
#         self.send_response(200)
#         self.send_header("Content-Type", self.guess_type(path))
#         self.send_header("Content-Length", str(file_size))
#         # Add Content-Disposition to suggest file download
#         self.send_header(
#             "Content-Disposition", f'attachment; filename="{os.path.basename(path)}"'
#         )
#         self.end_headers()

#         # Send file in chunks to handle large files efficiently
#         with open(path, "rb") as f, Progress(
#             console=console, transient=True
#         ) as progress:
#             task = progress.add_task("[green]Sending file...", total=file_size)
#             chunk_size = 1024 * 1024 * 2  # 2 MB chunks
#             while chunk := f.read(chunk_size):
#                 self.wfile.write(chunk)
#                 progress.update(task, advance=len(chunk))

#     def do_POST(self):
#         """Handle file uploads with support for larger file sizes."""
#         content_length = int(self.headers["Content-Length"])
#         boundary = self.headers["Content-Type"].split("=")[1].encode()

#         # Read file data
#         line = self.rfile.readline()
#         if not line.startswith(b"--" + boundary):
#             self.send_error(400, "Invalid boundary start.")
#             return

#         while not self.rfile.readline().startswith(b"Content-Type:"):
#             pass
#         self.rfile.readline()  # Skip empty line

#         file_data = b""
#         while True:
#             line = self.rfile.readline()
#             if line.startswith(b"--" + boundary):
#                 break
#             file_data += line

#         with open("uploaded_file", "wb") as f:
#             f.write(file_data)

#         self.send_response(200)
#         self.end_headers()
#         self.wfile.write(b"File uploaded successfully.")


# def run_server(addr: str = "0.0.0.0", port: int = 8000):
#     """Run the HTTP server with specified address and port."""
#     handler_class = EnhancedFileHandler
#     server_address = (addr, port)
#     httpd = http.server.HTTPServer(server_address, handler_class)
#     console.print(
#         f"Starting HTTP server on [underline bold italic cyan]http://{addr}:{port}[/] ..."
#     )
#     try:
#         httpd.serve_forever()
#     except KeyboardInterrupt:
#         console.print("[red]Server stopped by user[/red].")


# def get_network_url() -> str:
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     s.settimeout(0)
#     try:
#         # doesn't even have to be reachable
#         s.connect(("10.254.254.254", 1))
#         IP = s.getsockname()[0]
#     except Exception:
#         IP = "127.0.0.1"
#     finally:
#         s.close()
#     return IP


# # Typer CLI app
# app = typer.Typer()


# @app.command()
# def start(
#     address: str = typer.Option(
#         get_network_url(), help="The IP address to bind the server."
#     ),
#     port: int = typer.Option(8000, help="The port to run the server on."),
# ):
#     """Starts the HTTP server."""
#     run_server(address, port)


# if __name__ == "__main__":
#     app()
import os
import http.server
from pathlib import Path
import socketserver
import urllib.parse
import typer
from urllib.parse import quote, unquote
from rich.console import Console
from rich.progress import Progress
import socket
import humanize
import logging  # For logging setup
from rich.logging import RichHandler  # RichHandler for neat logging

# Set up logging with RichHandler
logging.basicConfig(level=logging.INFO, handlers=[RichHandler()], format="%(message)s")
logger = logging.getLogger("Server")

# Rich console for additional output features
console = Console()

# HTML template for directory listing with dark mode toggle
DIRECTORY_LISTING_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Directory listing for {path}</title>
    <style id="theme-style">
        body {{ font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4; color: #333; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }}
        th {{ background-color: #eaeaea; }}
        a {{ text-decoration: none; color: #007bff; }}
        a:hover {{ text-decoration: underline; }}
        #toggle-button {{ padding: 10px 20px; margin-bottom: 20px; cursor: pointer; }}
    </style>
</head>
<body>
    <button id="toggle-button">Toggle Dark Mode</button>
    <h2>Directory listing for {path}</h2>
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Size</th>
                <th>Last Modified</th>
            </tr>
        </thead>
        <tbody>
            {files}
        </tbody>
    </table>

    <script>
        // JavaScript to toggle between dark and light mode
        document.getElementById('toggle-button').addEventListener('click', function() {{
            const style = document.getElementById('theme-style');
            if (style.innerHTML.includes('background-color: #f4f4f4;')) {{
                style.innerHTML = `
                    body {{ font-family: Arial, sans-serif; padding: 20px; background-color: #333; color: #f4f4f4; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    th, td {{ padding: 10px; border-bottom: 1px solid #555; text-align: left; }}
                    th {{ background-color: #444; }}
                    a {{ text-decoration: none; color: #66b2ff; }}
                    a:hover {{ text-decoration: underline; }}
                    #toggle-button {{ padding: 10px 20px; margin-bottom: 20px; cursor: pointer; color: #f4f4f4; background-color: #444; border: none; }}
                `;
            }} else {{
                style.innerHTML = `
                    body {{ font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4; color: #333; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    th, td {{ padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }}
                    th {{ background-color: #eaeaea; }}
                    a {{ text-decoration: none; color: #007bff; }}
                    a:hover {{ text-decoration: underline; }}
                    #toggle-button {{ padding: 10px 20px; margin-bottom: 20px; cursor: pointer; }}
                `;
            }}
        }});
    </script>
</body>
</html>
"""


class EnhancedFileHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with improved large file handling capabilities and cleaner directory listings."""

    def list_directory(self, path):
        """Generate and send a directory listing in a cleaner format."""
        try:
            file_list = os.listdir(path)
        except OSError:
            self.send_error(403, "No permission to list directory")
            return None

        file_list.sort(key=lambda a: a.lower())
        files_html = ""

        # Generate file rows
        for name in file_list:
            fullname = os.path.join(path, name)
            display_name = name
            linkname = quote(name)  # URL encode for correct paths

            if os.path.isdir(fullname):
                display_name = f"{name}/"
                linkname += "/"  # append / for directories
                size = "-"
            else:
                size = humanize.naturalsize(
                    os.path.getsize(fullname)
                )  # Human-readable size
            last_modified = self.date_time_string(os.path.getmtime(fullname))
            files_html += f"""
            <tr>
                <td><a href="{linkname}">{display_name}</a></td>
                <td>{size}</td>
                <td>{last_modified}</td>
            </tr>
            """

        # Send response with custom HTML
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        response = DIRECTORY_LISTING_TEMPLATE.format(
            path=self.path, files=files_html
        ).encode("utf-8")
        self.wfile.write(response)

    def log_message(self, format: str, *args) -> None:
        logger.info(f"{self.address_string()} {format % args}")

        # return super().log_message(format, *args)

    def do_GET(self):
        """Serve a GET request with chunked file reading for large file support."""
        path = self.translate_path(self.path)
        path = unquote(path)

        if os.path.isdir(path):
            self.list_directory(path)
            return

        if not os.path.exists(path):
            self.send_error(404, "File not found")
            return

        file_size = os.path.getsize(path)
        self.send_response(200)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Length", str(file_size))
        # Add Content-Disposition to suggest file download
        self.send_header(
            "Content-Disposition", f'attachment; filename="{os.path.basename(path)}"'
        )
        self.end_headers()

        # Send file in chunks to handle large files efficiently
        with open(path, "rb") as f, Progress(
            console=console, transient=True
        ) as progress:
            task = progress.add_task("[green]Sending file...", total=file_size)
            chunk_size = getattr(
                self.server, "chunk_size", 1024 * 1024 * 2
            )  # Default to 2 MB if not set
            while chunk := f.read(chunk_size):
                self.wfile.write(chunk)
                progress.update(task, advance=len(chunk))

    def do_POST(self):
        """Handle file uploads with support for larger file sizes."""
        content_length = int(self.headers["Content-Length"])
        boundary = self.headers["Content-Type"].split("=")[1].encode()

        # Read file data
        line = self.rfile.readline()
        if not line.startswith(b"--" + boundary):
            self.send_error(400, "Invalid boundary start.")
            return

        while not self.rfile.readline().startswith(b"Content-Type:"):
            pass
        self.rfile.readline()  # Skip empty line

        file_data = b""
        while True:
            line = self.rfile.readline()
            if line.startswith(b"--" + boundary):
                break
            file_data += line

        with open("uploaded_file", "wb") as f:
            f.write(file_data)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"File uploaded successfully.")


def run_server(
    addr: str = "0.0.0.0",
    port: int = 8000,
    folder_path: str = ".",
    chunk_size: int = 1024 * 1024 * 2,
):
    """Run the HTTP server with specified address, port, folder path, and chunk size."""
    handler_class = EnhancedFileHandler
    server_address = (addr, port)
    folder_path_as_path = Path(folder_path).absolute()

    os.chdir(folder_path)  # Change the working directory to the user-specified folder

    httpd = http.server.HTTPServer(server_address, handler_class)
    httpd.chunk_size = chunk_size  # Set the chunk size for large file transfers
    # logger.info(
    #     f"Starting HTTP server on http://{addr}:{port} serving folder: {folder_path_as_path} ..."
    # )
    logger.info(f"Serving folder: {folder_path_as_path}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user.")


def get_network_url() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(("10.254.254.254", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


# Command-line interface using Typer
app = typer.Typer()


@app.command()
def serve(
    addr: str = typer.Option(
        "0.0.0.0", "--addr", "-a", help="Address to run the server on."
    ),
    port: int = typer.Option(8000, "--port", "-p", help="Port to run the server on."),
    folder_path: str = typer.Option(
        ".", "--folder", "-f", help="Folder to serve files from."
    ),
    chunk_size: int = typer.Option(
        1024 * 1024 * 2, "--chunk-size", "-c", help="Chunk size for file transfers."
    ),
):
    """Command to start the HTTP server with specified options."""
    logger.info("Fetching your network URL. Please wait...")
    network_url = get_network_url()
    logger.info(
        f"Network URL: http://{network_url}:{port} (for other devices on your network to access)"
    )
    run_server(addr, port, folder_path, chunk_size)


if __name__ == "__main__":
    app()
