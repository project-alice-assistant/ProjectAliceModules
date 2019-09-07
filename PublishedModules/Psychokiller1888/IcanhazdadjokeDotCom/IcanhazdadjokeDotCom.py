import requests

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class IcanhazdadjokeDotCom(Module):
	_INTENT_TELL_A_JOKE = Intent('TellAJoke')


	def __init__(self):
		self._SUPPORTED_INTENTS = [
			self._INTENT_TELL_A_JOKE
		]

		super().__init__(self._SUPPORTED_INTENTS)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		if intent == self._INTENT_TELL_A_JOKE:
			url = 'https://icanhazdadjoke.com/'

			headers = {
				'Accept'    : 'text/plain',
				'User-Agent': 'Project Alice',
				'From'      : 'projectalice@projectalice.ch'
			}

			response = requests.get(url, headers=headers)
			if response is not None:
				self.endDialog(session.sessionId, text=response.text)
			else:
				self.endDialog(session.sessionId, self.TalkManager.getrandomTalk('noJoke'))

		return True
