from usr import Settings2
from typing import List
import datetime


class obj():
    # last_used: datetime.datetime

    # session_id: str
    # _globus_id: str

    # Since the session variable only gets updated per full page refresh (via cookies)
    # We need an update mechanism that updates more frequently for our server side updates
    # During upload. So we store our ID via the app.msgs_for_client variable.
    # The synapse_session_object is tied to the app rather than session.
    msg_for_client: str = ''

    usr_settings_path: str
    settings: Settings2

    def __init__(self, session_id: str, user_settings_path: str):
        self._globus_id = ''
        self.session_id = session_id
        self.last_used = datetime.datetime.now()
        self.usr_settings_path = user_settings_path
        self.settings = Settings2('')

    @property
    def globus_id(self) -> str:
        return self._globus_id

    def set_globus_id(self, globus_id: str):
        self._globus_id = globus_id
        self.load_settings()

    def save_settings(self):
        self.settings.save(self.usr_settings_path)

    def load_settings(self) -> Settings2:
        self.settings = Settings2.load(
            self.usr_settings_path, self.globus_id)
        return self.settings
