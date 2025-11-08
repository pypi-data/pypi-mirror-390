import subprocess
import requests
import tempfile
import os
import platform
from typing import Optional


class FreedomConnect:
    DEFAULT_CONFIG_URL = "https://assets.bcworks.in.net/configs/wp0-client.conf"

    def __init__(
        self,
        config_url: Optional[str] = None,
        timeout: int = 10,
        interface_name: Optional[str] = None,
        persist: bool = False,
        verify_ssl: bool = True,
    ):
        self.config_url = config_url or self.DEFAULT_CONFIG_URL
        self.timeout = timeout
        self.interface_name = interface_name
        self.persist = persist
        self.verify_ssl = verify_ssl
        self.config_path = None
        self._is_windows = platform.system() == "Windows"

    def _get_wg_quick_command(self) -> str:
        if self._is_windows:
            return "wg-quick.exe"
        return "wg-quick"

    def _check_wg_installed(self) -> bool:
        wg_command = self._get_wg_quick_command()
        try:
            subprocess.run(
                [wg_command, "--version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def show_wg_requirement(self):
        if not self._check_wg_installed():
            print("\n" + "="*60)
            print("IMPORTANT: WireGuard is required but not found!")
            print("="*60)
            if self._is_windows:
                print("\nDownload WireGuard for Windows:")
                print("https://www.wireguard.com/install/")
            else:
                print("\nDownload WireGuard:")
                print("https://www.wireguard.com/install/")
            print("\nPlease install WireGuard before continuing.")
            print("="*60 + "\n")
            return False
        return True

    def download_config(self) -> str:
        try:
            response = requests.get(
                self.config_url,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise Exception(f"Failed to download config from {self.config_url}: {e}")

    def _create_config_file(self, config_data: str) -> str:
        if self.persist and self.interface_name:
            config_dir = os.path.expanduser("~/.config/wireguard")
            os.makedirs(config_dir, exist_ok=True)
            config_path = os.path.join(config_dir, f"{self.interface_name}.conf")
            with open(config_path, "w") as f:
                f.write(config_data)
            return config_path
        else:
            tmp = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".conf",
                mode="w"
            )
            tmp.write(config_data)
            tmp.close()
            return tmp.name

    def connect(self) -> bool:
        if not self.show_wg_requirement():
            raise Exception("WireGuard is not installed. Please install it from https://www.wireguard.com/install/")
        
        try:
            config_data = self.download_config()
            print(f"Downloaded config from {self.config_url}")

            self.config_path = self._create_config_file(config_data)
            print(f"Created config file at {self.config_path}")

            wg_command = self._get_wg_quick_command()
            subprocess.run(
                [wg_command, "up", self.config_path],
                check=True,
                capture_output=True,
                text=True
            )
            print("Successfully connected to VPN")

            return True

        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to connect WireGuard: {e.stderr if e.stderr else str(e)}"
            self._cleanup()
            raise Exception(error_msg)

        except Exception as e:
            self._cleanup()
            raise

        finally:
            if not self.persist and self.config_path:
                self._cleanup()

    def disconnect(self, interface: Optional[str] = None) -> bool:
        try:
            wg_command = self._get_wg_quick_command()
            
            if interface:
                target = interface
            elif self.interface_name:
                target = self.interface_name
            elif self.config_path:
                target = self.config_path
            else:
                raise Exception("No interface specified for disconnection")

            subprocess.run(
                [wg_command, "down", target],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"Successfully disconnected from VPN")

            self._cleanup()

            return True

        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to disconnect: {e.stderr if e.stderr else str(e)}"
            raise Exception(error_msg)

    def _cleanup(self):
        if not self.persist and self.config_path and os.path.exists(self.config_path):
            try:
                os.remove(self.config_path)
                print(f"Cleaned up config file")
            except OSError:
                pass

    def get_status(self) -> dict:
        try:
            wg_command = "wg" if not self._is_windows else "wg.exe"
            result = subprocess.run(
                [wg_command, "show"],
                capture_output=True,
                text=True,
                check=True
            )
            return {
                "connected": bool(result.stdout.strip()),
                "details": result.stdout
            }
        except subprocess.CalledProcessError:
            return {
                "connected": False,
                "details": None
            }
