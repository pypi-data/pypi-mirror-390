from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Input, Select, Static, Button, Switch
from textual.containers import ScrollableContainer
from textual.validation import Function
import subprocess
import os
import sys
import pwd
import argparse
import requests
import socket
import threading

HOSTNAME = 'localhost'
PORT = 10001
tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpServer.settimeout(0.2) # timeout for listening

global exit_programe_flag
exit_programe_flag = False

def wait_accept():
    global exit_programe_flag
    while(not exit_programe_flag):
        try: 
            (conn, (ip, port)) = tcpServer.accept() 
        except socket.timeout:
            pass
        except:
            exit_programe_flag = True

try:
    username = os.getlogin()
except OSError:
    username = os.getenv('USER', 'unknown_user')

class ReadonlyInput(Input):
    """A readonly Input widget that prevents user interaction."""

    def on_key(self, event) -> None:
        """Block all key inputs."""
        event.stop()  # Prevent any key events from being processed.

    def on_paste(self, event) -> None:
        """Block pasting into the input."""
        event.stop()  # Prevent pasting.

    def on_focus(self, event) -> None:
        """Deselect the input when it gets focus."""
        self.screen.set_focus(None)  # Remove focus to prevent user editing.

    def on_click(self, event) -> None:
        """Prevent clicks from focusing the input."""
        event.stop()  # Block click focus.

class ConfigureInstallerApp(App):
    TITLE = "Configure Installer"
    BINDINGS = [
        ("ctrl+q", "quit", "Quit application"),
    ]

    CSS = """
        Footer {
            text-align: left;
            align: left top; /* Horizontally center content */
        }
        Screen {
            layout: grid;
            grid-size: 1;
            grid-columns: 120; /* Two columns: 40 and 80 units wide */
            align: center top; /* Horizontally center content */
        }
        ScrollableContainer {
            layout: grid;
            grid-size: 2;
            grid-columns: 1fr 2fr; /* Two columns: 40 and 80 units wide */
            grid-rows: 3; /* Two columns: 40 and 80 units wide */
            grid-gutter: 1 1;    /* Gutter space between elements */
            align: center top;
            margin-top: 1;
        }
        Input.readonly {
            color: $text-muted;
        }
        .border-red {
            border: solid transparent;  /* Adds a red border */
        }
        .label-app {
            content-align: left middle; /* Centers the text vertically and horizontally */
            padding: 0 1;                 /* Adds padding */
        }
        #install-btn {
            width: 100%;
            column-span: 2;
            margin: 0 36;
        }

        Switch {
            background: transparent;
            border: solid transparent;  /* Removes the border */
        }

        .invalid-input {
            background: red;  /* Adds a red border */
        }

        .hidden {
            display: none;
        }

        .error-message {
            width: 100%;
            height: 1;
            content-align: left top;
            column-span: 2;
            margin: 0 0 1 42;
            color: red;
        }

    """

    def on_mount(self) -> None:
        self.theme = "gruvbox"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer(show_command_palette=False)
        yield ScrollableContainer(
            Static("Access key:", classes="border-red label-app"),
            Input(placeholder="Enter your access key", id="access-key-input", validators=[Function(self.access_key_validator, "Access key cannot be empty!")]),
            Static("Access key cannot be empty!", id="access-key-error", classes="error-message hidden"),  # Hidden error message
            Static("Install the latest app:", classes="border-red label-app"),
            Select(options=[("Release", "release"), ("Beta", "beta")], id="app-select", allow_blank=False),
            Static("Install the latest config:", classes="border-red label-app"),
            Select(options=[("Release", "release"), ("Beta", "beta")], id="config-select", allow_blank=False),
            Static("Install the latest web client:", classes="border-red label-app"),
            Select(options=[("Release", "release"), ("Beta", "beta")], id="web-client-select", allow_blank=False),
            Static("Install the web client only:", classes="border-red label-app"),
            Switch(value=False, id="web-only"),
            Static("Username:", classes="border-red label-app"),
            ReadonlyInput(placeholder="Username", value=username, id="username-input"),
            Static("Username cannot be empty!", id ="username-error", classes="error-message hidden"),      # Hidden error message
            Static("Installation Mode:", classes="border-red label-app"),
            Select(options=[("Normal mode", "normal"), ("Maintenance mode", "maintenance")], id="install-mode-select", value="normal", allow_blank=False),
            Button("Install", id="install-btn", variant="success"),
            id="config-installer"
        )

    def access_key_validator(self, x):
        """Validates access key input."""
        # error_widget = 
        if x.strip():
            self.query_one("#access-key-error", Static).add_class("hidden")
            return True
        else:
            self.query_one("#access-key-error", Static).remove_class("hidden")
            return False

    def username_validator(self, x):
        """Validates username input."""
        if x.strip():
            # self.query_one("#username-error").add_class("hidden")
            return True
        else:
            # self.query_one("#username-error").remove_class("hidden")
            return False

    @on(Input.Changed)
    def on_input_change(self, event: Input.Changed) -> None:
        """Handles input change event and checks if the input is not empty."""
        if event.input.id == "#access-key-input":
            error_widget = self.query_one("#access-key-error", Static)
            if not event.validation_result.is_valid:  # Check if input is empty
                error_widget.remove_class("hidden")  # Show error message
            else:
                error_widget.add_class("hidden")  # Hide error message
        elif event.input.id == "#username-input":
            error_widget = self.query_one("#username-error", Static)
            if not event.validation_result.is_valid:  # Check if input is empty
                error_widget.remove_class("hidden")  # Show error message
            else:
                error_widget.add_class("hidden")  # Hide error message

    @on(Switch.Changed)
    def switch_changed(self, event: Switch.Changed) -> None:
        if event.switch.value:
            self.query_one("#config-select", Select).disabled = True
            self.query_one("#app-select", Select).disabled = True
        else:
            self.query_one("#config-select", Select).disabled = False
            self.query_one("#app-select", Select).disabled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "install-btn":
            access_token_input_widget = self.query_one("#access-key-input", Input)
            access_token_error_widget = self.query_one("#access-key-error", Static)
            username_input_widget = self.query_one("#username-input", Input)
            username_error_widget = self.query_one("#username-error", Static)

            if not access_token_input_widget.value.strip():  # Check if input is empty
                access_token_error_widget.remove_class("hidden")  # Show error message
                access_token_input_widget.focus()
            elif not username_input_widget.value.strip():  # Check if input is empty
                # username_error_widget.remove_class("hidden")  # Show error message
                username_input_widget.focus()
            else:
                access_token_error_widget.add_class("hidden")  # Hide error message
                # username_error_widget.add_class("hidden")  # Hide error message
                reply ={}
                reply.update({"access_key": self.query_one("#access-key-input", Input).value})
                if self.query_one("#web-only", Switch).value:
                    reply.update({"app_version": "not-install"})
                    reply.update({"config_version": "not-install"})
                else:
                    reply.update({"app_version": self.query_one("#app-select", Select).value})
                    reply.update({"config_version": self.query_one("#config-select", Select).value})

                reply.update({"web_client_version": self.query_one("#web-client-select", Select).value})
                reply.update({"web_only": self.query_one("#web-only", Switch).value})
                reply.update({"app_only": False})
                reply.update({"username": self.query_one("#username-input", Input).value})
                reply.update({"install_mode": self.query_one("#install-mode-select", Select).value})
                self.exit(reply)

    def on_toggle_dark(self) -> None:
        self.dark = not self.dark

    def on_quit(self) -> None:
        self.exit()

def download_file_from_gitlab(access_token:str, project_id:str, src_path: str, dest_path:str, branch_name:str) -> int:
    os.system("rm -f %s*" % dest_path)
    url = f"https://gitlab.com/api/v4/projects/{project_id}/repository/files/{src_path.replace('/', '%2F')}/raw?ref={branch_name}"
    response = requests.get(url, headers={"PRIVATE-TOKEN": access_token})
    if response.status_code == 200:
        try:
            # Save the file locally
            with open(f"{dest_path}", "wb") as file:
                file.write(response.content)
            # print(f"File downloaded successfully as {dest_path}")
            return 0 # Success
        except Exception as e:
            print(f"An error occurred while saving the file: {e}")
            return 1 # Error
    else:
        print(f"Invalid Access Token: {access_token}, error code: {response.status_code}")
        return -1 # Invalid Access Token

def get_cmd(config:dict, install_ai_branch_suffix:str) -> str:
    # Extract access_key from reply
    ACCESS_TOKEN = config["access_key"]
    DEPLOY_PRJ_ID = "65233883"
    USERNAME = config["username"]

    # Get Home directory
    HOME_DIR = pwd.getpwnam(USERNAME).pw_dir

    os.system(f"sudo groupadd {USERNAME}")
    os.system(f"sudo usermod -aG {USERNAME} {USERNAME}")
    os.system(f"sudo -u {USERNAME} mkdir -p {HOME_DIR}/Software")

    # Download encrypted SOFTWARE folder
    INSTALL_AI_SH_BRANCH = "install-file-" + install_ai_branch_suffix
    if not (config["web_only"] and config["app_only"]):
        if download_file_from_gitlab(access_token=ACCESS_TOKEN,
                                    project_id=DEPLOY_PRJ_ID,
                                    src_path="FHVGVIR.txt",
                                    dest_path=f"{HOME_DIR}/FHVGVIR.txt",
                                    branch_name="software-dir-" + ("main" if config["app_version"]=="released" else "dev")) == 0:
            subprocess.run(["chown", f"{USERNAME}:{USERNAME}", f"{HOME_DIR}/FHVGVIR.txt"], check=True)

    # Download encrypted webclient folder
    if (not config["app_only"]) or config["web_only"]:
        if download_file_from_gitlab(access_token=ACCESS_TOKEN,
                                    project_id=DEPLOY_PRJ_ID,
                                    src_path="GUR_PENML_XRL_VF_ZL_FRPERG_CBFG.txt",
                                    dest_path=f"{HOME_DIR}/Software/GUR_PENML_XRL_VF_ZL_FRPERG_CBFG.txt",
                                    branch_name="web-client-" + ("main" if config["web_client_version"]=="released" else "dev")) == 0:
            subprocess.run(["chown", f"{USERNAME}:{USERNAME}", f"{HOME_DIR}/Software/GUR_PENML_XRL_VF_ZL_FRPERG_CBFG.txt"], check=True)

    # Download install_ai.sh
    INSTALL_AI_SH_BRANCH = "install-file-" + install_ai_branch_suffix
    if download_file_from_gitlab(access_token=ACCESS_TOKEN,
                                    project_id=DEPLOY_PRJ_ID,
                                    src_path="install_ai.sh",
                                    dest_path="install_ai.sh",
                                    branch_name=INSTALL_AI_SH_BRANCH) == 0:
        subprocess.run(["chmod", "+x", "install_ai.sh"], check=True)
        subprocess.run(["chown", f"{USERNAME}:{USERNAME}", f"install_ai.sh"], check=True)
        try:
            install_cmd = f"sudo bash ./install_ai.sh -u {config['username']}"
            install_cmd = install_cmd + " " + ('-m' if config['install_mode']=='maintenance' else '')
            install_cmd = install_cmd + " " + ('-wo' if config['web_only'] else '')
            install_cmd = install_cmd + " " + ('-ao' if config['app_only'] else '')
            install_cmd = install_cmd + " " + ('-go' if config['agent_only'] else '')
            install_cmd = install_cmd + " " + ('-ad' if config['app_version']=='beta' else '')
            install_cmd = install_cmd + " " + ('-cd' if config['config_version']=='beta' else '')
            return install_cmd
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

def run():
    try:
        global exit_programe_flag
        try:
            tcpServer.bind((HOSTNAME, PORT))
            tcpServer.listen(1)
        except OSError:
            print("Other process is running")
            exit(1)

        t_socket = threading.Thread(target=wait_accept)
        t_socket.start()

        parser = argparse.ArgumentParser(description="My script")
        parser.add_argument("--branch", "-b", type=str, default="main", help="The branch to use (default: main for `install-file-main`)")
        parser.add_argument("--cli", action='store_true', help="Run in CLI mode")
        parser.add_argument("--access-token", "-t", default="", help="Input Access Token")
        parser.add_argument("--app-dev", "-ad", action='store_true', help="Run app in dev mode")
        parser.add_argument("--app-only", "-ao", action='store_true', help="Only install the latest app")
        parser.add_argument("--cfg-dev", "-cd", action='store_true', help="Run config in dev mode")
        parser.add_argument("--web-dev", "-wd", action='store_true', help="Run web client in dev mode")
        parser.add_argument("--web-only", "-wo", action='store_true', help="Only install web client")
        parser.add_argument("--agent-only", "-go", action='store_true', help="Only update agent server")
        parser.add_argument("--installer-dev", "-id", action='store_true', help="Download Installer from dev branch")
        parser.add_argument("--maintenance", "-m", action='store_true', help="Run installer in maintenance mode")
        parser.add_argument("--username", "-u", default="", help="username $(whoami)")
        args = parser.parse_args()

        if args.cli:
            reply = {}
            reply.update({"access_key": args.access_token})
            reply.update({"app_only": args.app_only})
            reply.update({"app_version":"beta" if args.app_dev else "released"})
            reply.update({"config_version":"beta" if args.cfg_dev else "released"})
            reply.update({"web_only": args.web_only})
            reply.update({"web_client_version": "beta" if args.web_dev else "released"})
            reply.update({"agent_only": args.agent_only})
            reply.update({"username": args.username if args.username else username})
            reply.update({"install_mode": "maintenance" if args.maintenance else "normal"})
        else:
            # app = ConfigureInstallerApp()
            # reply = app.run()
            exit_programe_flag = True
            tcpServer.close()
            t_socket.join(); print("stop t_socket")
            sys.exit(1)

        if reply:
            cmd = get_cmd(reply, ("dev" if args.installer_dev else args.branch))
            if cmd:
                os.system(cmd)
            else:
                import sys
                exit_programe_flag = True
                tcpServer.close()
                t_socket.join(); print("stop t_socket")
                sys.exit(1)
                
        exit_programe_flag = True
        tcpServer.close()
        t_socket.join()
    finally:
        tcpServer.close()
        # print("stop t_socket")

if __name__ == "__main__":
    run()

# python3 -m pip install textual==0.89.1 textual-dev==1.7.0
