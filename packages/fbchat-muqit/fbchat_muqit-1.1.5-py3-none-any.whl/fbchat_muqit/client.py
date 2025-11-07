# fbchat_muqit/client.py 
# main client
from __future__ import annotations

from msgspec.json import Decoder

from fbchat_muqit.models.mqtt_response.response import LSResp

__all__ = ["Client"]


import asyncio
import sys
from typing import Optional

# Base Classes
from .facebook.client import FacebookClient
from .messenger.client import MessengerClient
from .state import State
from .muqit import Mqtt
from .realtime import FacebookRealtime
from .events.dispatcher import EventDispatcher, EventType

from .logging.logger import FBChatLogger, setup_logger, disable_logging
from .exception.errors import FBChatError
from .models.deltas.parser import MessageParser, ParsedEvent

class Client(EventDispatcher, FacebookClient, MessengerClient):
        
    def __init__(
            self,
            cookies_file_path: str,
            userAgent: Optional[str] = None,
            proxy: Optional[str] = None,
            log_level = "INFO",
            disable_logs = False,
            online = True
            ):
        
        self._setup_windows_compatibility()
        super().__init__()

        self._state: Optional[State] = None
        self._uid: str = ""
        self._name: str = ""
        self._mqtt: Optional[Mqtt] = None
        self._parser = MessageParser(self.logger)
        self._realtime: Optional[FacebookRealtime] = None
        self._events_queue: asyncio.Queue[ParsedEvent] = asyncio.Queue(maxsize=1000)

        
        self._cookies_file_path = cookies_file_path
        self._userAgent = userAgent
        self._proxy = proxy
        self._online = online
        self.logger: FBChatLogger = setup_logger(log_level)

        self._listening: bool = False 
        
        if disable_logs:
            disable_logging()

    @property
    def uid(self):
        """The Facebook user ID of the client."""
        return self._uid
    @property
    def name(self):
        """The Facebook name of the client."""
        return self._name

    async def __aenter__(self):
     # Reopen session if it was closed
        if not self._state:
            state: State = await State.from_json_cookies(self._cookies_file_path, self._userAgent ,self._proxy)
            self._state = state 
        # Refresh every 1 hour
        # self._state.enable_auto_refresh(interval=3600)
        # self.logger.debug("Started auto state refresh")
        self._uid = self._state.user_id
        self._name = self._state.user_name

        self._parser = MessageParser(self.logger)
        self._parse_ls_resp = Decoder(type=LSResp, strict=False)

        # Ensure logged in
        if not self._state._is_logged:
            self.logger.info("User is not logged in!")

        if self._state.user_name:
            self.logger.info(f"Logged in as {self.name} ({self.uid})")
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._state:
            await self._state.close()
            self._state = None 

        await self.stop_listening()

    @staticmethod
    def _setup_windows_compatibility():
        # Setup Windows asyncio compatibility
        if sys.platform == 'win32':
            try:
                # Check current policy
                current_policy = asyncio.get_event_loop_policy()
                # Switch to SelectorEventLoop if using ProactorEventLoop
                if hasattr(asyncio, 'WindowsProactorEventLoopPolicy') and \
                   isinstance(current_policy, asyncio.WindowsProactorEventLoopPolicy):
                    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
                # Ensure event loop exists
                try:
                    asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except Exception:
                pass

    async def start_listening(self):
        """Start listening from an external event loop.
        
        Raises:
            FBchatException: If request failed
        """
        if not self._state:
            raise FBChatError("Failed to get session")
        
        self._mqtt = await Mqtt.connect(
                state=self._state,
                chat_on=self._online,
                foreground=self._online,
                message_handler=self._handle_mqtt_messages
            )

        self._realtime = await FacebookRealtime.connect(self._state, self._handle_realtime_messages)

        if self._online:
            await self._mqtt.set_chat_on(self._online)
            await self._mqtt.set_foreground(self._online)
        self._listening = True
        # starting dispatcher
        asyncio.create_task(self._dispatch_mqtt_message())


    async def stop_listening(self):
        """Stop the listening mqtt and realtime loop."""
        if self._mqtt:
            await self._mqtt.stop()
        if self._realtime:
            await self._realtime.stop()

        self._listening = False
        self._mqtt = None
        self._realtime = None


    async def listen(self): 
        """Starts listening to events Blockingly"""
        await self.start_listening()

        await self.dispatch(EventType.LISTENING)

        try:
            while self._listening:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            self.logger.debug("Client stopped listening!")
            raise 

        except Exception as e:
            self.logger.error(f"Error in listen loop: {e}")
            raise FBChatError("Listening failed", original_exception=e)

    
    async def _dispatch_mqtt_message(self):
        """Dispatches Parsed Event data from Queue"""
        while self._listening:
            parsedEvent = await self._events_queue.get()
            try:
                await self.dispatch(parsedEvent.eventType, *parsedEvent.args)
            except Exception as e:
                self.logger.error(f"Failed to dispatch Event ", exc_info=e)

            finally:
                self._events_queue.task_done()

    
    async def _handle_mqtt_messages(self, topic: str, payload: bytes):
        """Handles and Parses incoming payloads and putting them in Queue"""
        try:
            if topic == "/ls_resp":
                # only received payloads if any payloads were published to /ls_req
                data = self._parse_ls_resp.decode(payload)
                fut = self._pending_requests.pop(data.request_id, None)
                if fut and not fut.done():
                    fut.set_result(data)
                return

            elif topic == "/t_ms" and b'deltas' in payload:
                try:
                    eventData = self._parser.parse_t_ms(payload)
                    for e in eventData:
                        if e:
                            await self._events_queue.put(e)
                except Exception as e:
                    self.logger.error(f"Failed to parse /t_ms deltas: {e}")

            else:
                eventdata = self._parser.parse_all(topic, payload)
                if eventdata:
                    await self._events_queue.put(eventdata)
        except Exception as e:
                self.logger.error(f"Failed to parse payloads ftom Topic: {topic} payload: {payload}", exc_info=e)
    


    async def _handle_realtime_messages(self, topic, payload):
        pass 

    async def start(self):
        """Initiates `Client` class and logins to account. But doesn't listens to event. To listen to events call `listen()` method."""
        await self.__aenter__()

    async def close(self):
        """Closes and clears all connections of Client"""
        await self.__aexit__(None, None, None)


    def run(self):
        """Blocking Call listens to incoming events"""
        try:
            asyncio.run(self._runner())
        except KeyboardInterrupt:
            self.logger.info("Interrupted By the User!")
        except Exception as e:
            self.logger.exception(e)

    async def _runner(self):
        await self.start()
        try:
            await self.listen()
        finally:
            await self.close()



    async def download(self, url: str, filename: str):
        """
        Download a image, video sent from messenger.

        Args:
            url: Url of the image, video.
            filename: name of the file.
        """
        if self._state:
            await self._state.download_file(url, filename)
