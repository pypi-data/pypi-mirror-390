import asyncio
import base64
import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from multiprocessing import Queue
from typing import Any, cast

import httpx
import websockets
from dotenv import load_dotenv

from evipy.model_device_page import EviqoDevicePageModel
from evipy.model_device_query import Docs as device_docs
from evipy.model_device_query import EviqoDeviceQueryModel
from evipy.model_user import EviqoUserModel

WS_URL = "wss://app.eviqo.io/dashws"

logger = logging.getLogger(__name__)


@dataclass
class WidgetUpdate:
    widget_id: str
    widget_name: str
    device_id: str
    widget_value: str
    time: datetime


def calculate_hash(user: str, password: str) -> str:
    # Encode and hash the first string (lowercase)
    first_hash = hashlib.sha256(user.lower().encode("utf-8")).digest()

    # Concatenate second string with first hash, then hash again
    combined = password.encode("utf-8") + first_hash
    final_hash = hashlib.sha256(combined).digest()

    # Base64 encode and return
    return base64.b64encode(final_hash).decode("ascii")


class EviqoWebsocketConnection:
    def __init__(
        self,
        url: str,
        session_id: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> None:
        self.url = url
        self.session_id = session_id
        self.username = user
        self.password = password
        self.ws = None  # type: None | websockets.ClientConnection
        self.widget_id_to_name = {}  # type: dict[int, str]
        self.widget_name_to_id = {}  # type: dict[str, int]
        self.user = None  # type: None | EviqoUserModel
        self.devices = []  # type: list[device_docs]
        self.device_pages = []  # type: list[EviqoDevicePageModel]
        self.message_counter = 0
        self.widget_id_map = {}  # type: dict[int, dict[str, str]]
        self.keepalive_timer = datetime.now()
        self.update_queue = Queue(maxsize=30)  # type: Queue[WidgetUpdate]

    async def connect(self, http_client: httpx.AsyncClient | None = None) -> bool:
        """Connect to WebSocket with session cookie"""
        try:
            logger.debug(f"Connecting to {self.url}...")
            """
            OPEN DEVICE PAGE:
            0x00490097<DEVICE_ID_ASCII>
            RESP:
            0x00000097 0x000000C8

            OPEN DEVICE PAGE:
            0x01040098{"pageId":"...","deviceId":"...","dashboardPageId":null}
            RESP:
            0x01040098<model_device.DevicePage>

            """
            # Make HTTP request to login page to capture cookies
            login_url = "https://app.eviqo.io/dashboard/login"
            if http_client is None:
                http_client = httpx.AsyncClient()
            response = await http_client.get(login_url)
            await http_client.aclose()

            # Parse cookies from response
            cookie_header = ""
            if response.cookies:
                cookie_parts = []
                for cookie_name, cookie_value in response.cookies.items():
                    cookie_parts.append(f"{cookie_name}={cookie_value}")
                    logger.debug(f"Setting cookie {cookie_name}")
                cookie_header = "; ".join(cookie_parts)

            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/140.0.0.0 Safari/537.36"
                ),
                "Origin": "https://app.eviqo.io",
            }

            # Append cookies to headers if we have any
            if cookie_header:
                headers["Cookie"] = cookie_header

            self.ws = await websockets.connect(self.url, additional_headers=headers)

            logger.debug("Connected successfully!")
            return True

        except Exception as e:
            logger.exception(f"Connection failed: {e}")
            return False

    async def keepalive(self) -> None:
        # 00 06 00 <COUNTER>
        logger.debug("Keepalive check")
        if datetime.now() >= (self.keepalive_timer + timedelta(seconds=15)):
            logger.info("Issue keepalive")
            self.keepalive_timer = datetime.now()
            await self.send_message(None, byte2=0x06, description="KEEPALIVE")
            await self.listen()

    async def issue_initialization(self) -> None:
        """Send initialization message with clientType, version, and locale"""
        logger.debug("Sending initialization message...")

        init_payload = {"clientType": "web", "version": "0.98.2", "locale": "en_US"}

        # Header: 0x01300001
        # byte1=0x01, byte2=0x30, byte3=0x00, byte4=0x01
        await self.send_message(
            init_payload, byte1=0x01, byte2=0x30, description="INIT"
        )
        header, payload = await self.listen()
        if payload is None:
            raise ValueError("Init message failed")

    async def query_devices(self) -> None:
        logger.debug("Sending device query message...")

        await self.send_message(
            {
                "docType": "DEVICE",
                "mode": "MATCH_ALL",
                "viewType": "LIST",
                "filters": [
                    {
                        "type": "SUB_SEGMENT",
                        "filters": [],
                        "mode": "MATCH_ANY",
                        "isCurrent": True,
                    }
                ],
                "offset": 0,
                "limit": 17,
                "order": "ASC",
                "sortBy": "Name",
            },
            byte1=0x01,
            byte2=0x1B,
            byte3=0x00,
            description="DEVICE QUERY",
        )
        header, payload = await self.listen()
        device_response = EviqoDeviceQueryModel.model_validate(payload)

        for device in device_response.docs:
            device_details = cast(device_docs, device[1])
            self.devices.append(device_details)
            logger.info(
                f"Found device {device_details.name=} {device_details.deviceId=}"
            )

    async def login(self) -> None:
        """Send the login message by hashing the password.

        AUTH:
        0x00020003{"email":"<EMAIL>","hash":"<B64_HASH>","clientType":"web","version":"0.98.2","locale":"en_US"}
        RESP:
        0x00020003<model_user.EviqoUserModel>
        """
        logger.debug("Sending login message...")

        if self.username is None or self.password is None:
            raise ValueError("User and password must be set")

        await self.send_message(
            {
                "email": self.username,
                "hash": calculate_hash(self.username, self.password),
                "clientType": "web",
                "version": "0.98.2",
                "locale": "en_US",
            },
            0x00,
            0x02,
            0x00,
            None,
            description="LOGIN",
        )

        header, payload = await self.listen()
        if payload is None:
            raise ValueError("Did not get back user payload")
        self.user = EviqoUserModel.model_validate(payload)

    async def request_charging_status(self, device_id: int) -> EviqoDevicePageModel:
        """Request charging status for a device"""
        if self.ws is None:
            raise RuntimeError(
                "Cannot request charging status before websocket is created"
            )

        page_id = "17948"  # some magic number

        logger.debug("Requesting charging status...")

        await self.send_message(
            str(device_id),
            byte1=0x00,
            byte2=0x49,
            byte3=0x01,
            description="DEVICE NUMBER",
        )
        # expect one message
        header, payload = await self.listen()
        logger.debug(header)
        logger.debug(payload)

        await self.send_message(
            {
                "pageId": page_id,
                "deviceId": str(device_id),
                "dashboardPageId": None,
            },
            byte1=0x01,
            byte2=0x04,
            byte3=0x01,
            description="DEVICE PAGE",
        )
        header, payload = await self.listen()
        return cast(EviqoDevicePageModel, EviqoDevicePageModel.model_validate(payload))

    def get_timestamp(self) -> str:
        """Get formatted timestamp"""
        return datetime.now().strftime("%H:%M:%S")

    def extract_widget_mappings(
        self, device_idx: int, device_page: EviqoDevicePageModel
    ) -> None:
        """Extract widget ID to name mappings from dashboard JSON"""
        dashboard = device_page.dashboard
        widgets = dashboard.widgets

        device_widget_id_map = self.widget_id_map.setdefault(device_idx, {})

        for widget in widgets:
            modules = widget.modules
            for module in modules:
                display_data_streams = module.displayDataStreams
                for stream in display_data_streams:
                    device_widget_id_map[str(stream.id)] = stream.name
        if device_widget_id_map:
            for wid, name in sorted(
                device_widget_id_map.items(),
                key=lambda x: int(x[0]) if x[0].isdigit() else 0,
            ):
                logger.debug(f"  ID {wid}: {name}")

    def parse_binary_message(
        self, data: bytes
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | str | None]:
        """Parse binary message with 4-byte header"""
        if len(data) < 4:
            return None, None

        # Extract header bytes
        byte1 = data[0]
        byte2 = data[1]
        byte3 = data[2]
        byte4 = data[3]

        has_payload = len(data) > 4

        header_info = {
            "byte1": byte1,
            "byte2": byte2,
            "byte3": byte3,
            "byte4": byte4,
            "has_payload": has_payload,
            "header_hex": data[:4].hex(),
            "total_length": len(data),
        }

        # Try to extract payload if present
        payload_str = None  # type: None | str
        payload_dict = None  # type: None | dict[str, Any]
        payload_type = None

        if has_payload:
            payload_data = data[4:]

            # Check if this is a widget update message (0x0140E_)
            if byte2 == 0x14:
                payload_type = "widget_update"
                payload_dict = self.parse_widget_update(payload_data)
            else:
                # Try JSON first
                try:
                    payload_dict = json.loads(payload_data.decode("utf-8"))
                    payload_type = "json"
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Try as ASCII text
                    try:
                        payload_str = payload_data.decode("ascii")
                        payload_type = "ascii"
                        # Check if it's printable
                        if not payload_str.isprintable():
                            # Try UTF-8
                            try:
                                payload_str = payload_data.decode("utf-8")
                                payload_type = "text"
                                if not payload_str.isprintable():
                                    raise UnicodeDecodeError(
                                        "utf-8", b"", 0, 0, "not printable"
                                    )
                            except UnicodeDecodeError:
                                payload_type = "binary"
                                payload_dict = {
                                    "hex": payload_data.hex(),
                                    "length": len(payload_data),
                                    "preview": payload_data[:50].hex()
                                    if len(payload_data) > 50
                                    else payload_data.hex(),
                                }
                    except UnicodeDecodeError:
                        # Pure binary data
                        payload_type = "binary"
                        payload_dict = {
                            "hex": payload_data.hex(),
                            "length": len(payload_data),
                            "preview": payload_data[:50].hex()
                            if len(payload_data) > 50
                            else payload_data.hex(),
                        }

        header_info["payload_type"] = payload_type
        if payload_dict is not None:
            logger.debug("Received dictionary")
            return header_info, payload_dict
        elif payload_str is not None:
            logger.debug("Received ascii")
            return header_info, payload_str
        else:
            return header_info, None

    def parse_widget_update(self, payload_data: bytes) -> dict[str, Any]:
        """Parse widget update message format"""
        logger.debug("BEGIN: parse_widget_update")
        try:
            # HEADER: <0x00><0x14>MC
            # PAYLOAD: 89349<0x00>vw<0x00>5<0x00>241.29
            # Format: widget_id \x00 device_id \x00 widget_value
            parts = payload_data.split(b"\x00")

            if len(parts) < 2:
                return {
                    "error": "Insufficient null terminators",
                    "raw_hex": payload_data.hex(),
                }

            # First part should be widget ID (numeric)
            device_id = parts[0].decode("ascii", errors="ignore")
            widget_id = (
                parts[2].decode("ascii", errors="ignore") if len(parts) > 1 else ""
            )
            widget_value = (
                parts[3].decode("ascii", errors="replace") if len(parts) > 2 else ""
            )

            # Look up widget name if we have the mapping
            device_widget_id_map = self.widget_id_map.get(0, {})
            widget_name = device_widget_id_map.get(widget_id, "Unknown")
            self.update_queue.put(
                WidgetUpdate(
                    widget_id=widget_id,
                    widget_name=widget_name,
                    device_id=device_id,
                    widget_value=widget_value,
                    time=datetime.now(tz=UTC),
                ),
                block=False,
            )

            return {
                "widget_id": widget_id,
                "widget_name": widget_name,
                "device_id": device_id,
                "widget_value": widget_value,
            }

        except Exception as e:
            return {
                "error": f"Failed to parse widget update: {e}",
                "raw_hex": payload_data.hex(),
            }

    def create_binary_message(
        self,
        payload: dict[str, Any] | str | None = None,
        byte1: int = 0x00,
        byte2: int = 0x00,
        byte3: int = 0x00,
        byte4: int = 0x00,
    ) -> bytes:
        """Create binary message with full control over all 4 header bytes"""
        # Build header with custom byte3
        header = bytes([byte1, byte2, byte3, byte4])

        # Add payload if present
        if isinstance(payload, str):
            payload_bytes = payload.encode("utf-8")
            return header + payload_bytes
        elif payload is not None:
            payload_bytes = json.dumps(payload).encode("utf-8")
            return header + payload_bytes

        return header

    async def listen(
        self, duration: int = 10
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | str | None]:
        """Listen for incoming messages"""
        logger.debug(f"Listening for messages for {duration} seconds...")
        if self.ws is None:
            logger.error("Cannot listen, websocket not created")
            return None, None

        try:
            async with asyncio.timeout(duration):
                while True:
                    message = await self.ws.recv()
                    if isinstance(message, bytes):
                        logger.debug(f"RECEIVED BINARY ({len(message)} bytes):")
                        header, payload = self.parse_binary_message(message)
                        if header and header["payload_type"] == "widget_update":
                            logger.info(payload)
                        return header, payload

        except TimeoutError:
            logger.debug("Listening period ended")
            return None, None
        except Exception as e:
            logger.error(f"Error while listening: {e}")
            return None, None

    async def send_message(
        self,
        payload: None | str | dict[str, Any] = None,
        byte1: int = 0x00,
        byte2: int = 0x00,
        byte3: int = 0x00,
        byte4: int | None = None,
        description: str = "",
    ) -> None:
        """Send a binary message to the WebSocket"""
        if self.ws is None:
            logger.error("Error sending, websocket not created")
            return
        try:
            if byte4 is None:
                byte4 = self.message_counter
                byte4 += 1
            message = self.create_binary_message(payload, byte1, byte2, byte3, byte4)
            logger.debug(f"SENDING {description}")
            await self.ws.send(message)

        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def run(self, just_scan: bool = False) -> None:
        """Main exploration routine"""
        if not await self.connect():
            return

        try:
            await self.issue_initialization()
            await self.login()
            await self.query_devices()
            if not self.devices:
                raise ValueError("No devices found")
            # just first device for now
            device = self.devices[0]
            if device.deviceId is None:
                raise ValueError("Device ID was not set")
            self.device_pages.append(
                await self.request_charging_status(device.deviceId)
            )
            self.extract_widget_mappings(0, self.device_pages[0])
            await self.keepalive()

            # Continue listening for any other messages
            while True and not just_scan:
                await self.keepalive()
                header, payload = await self.listen(duration=20)
        finally:
            if self.ws:
                await self.ws.close()
                logger.debug("Connection closed")


async def main() -> None:
    # Load environment variables
    load_dotenv()
    session_id = os.getenv("SESSION_ID")
    eviqo_email = os.getenv("EVIQO_EMAIL")
    eviqo_password = os.getenv("EVIQO_PASSWORD")

    if not eviqo_password and not eviqo_email:
        assert session_id, (
            "SESSION_ID required if not using EVIQO_EMAIL and EVIQO_PASSWORD"
        )
    explorer = EviqoWebsocketConnection(WS_URL, session_id, eviqo_email, eviqo_password)
    await explorer.run()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s",
        datefmt="%H:%M:%S",
    )
    asyncio.run(main())
