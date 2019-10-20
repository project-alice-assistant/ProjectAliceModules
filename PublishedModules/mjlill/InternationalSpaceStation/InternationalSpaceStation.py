import requests
from requests.exceptions import RequestException

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import Decorators


class InternationalSpaceStation(Module):
	"""
	Author: mjlill
	Description: Inquire information about the international space station
	"""

	_INTENT_ASTRONAUTS = Intent('Astronauts')
	_INTENT_ISS_POSITION = Intent('IssPosition')

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
			(self._INTENT_ASTRONAUTS, self.getAstronauts),
			(self._INTENT_ISS_POSITION, self.getIssPosition)
		]

		super().__init__(self._SUPPORTED_INTENTS)


	@staticmethod
	def queryApi(url: str, *args, **kargs) -> dict:
		response = requests.get(url=url.format(*args, **kargs))
		response.raise_for_status()
		return response.json()


	@Decorators.anyExcept(exceptions=(RequestException, KeyError), text='noServer', printStack=True)
	@Decorators.online
	def getIssPosition(self, session: DialogSession, **_kwargs):
		data = self.queryApi('http://api.open-notify.org/iss-now.json')
		latitude = float(data['iss_position']['latitude'])
		longitude = float(data['iss_position']['longitude'])

		oceanData = self.queryApi('http://api.geonames.org/oceanJSON?lat={latitude}&lng={longitude}&lang={language}&username=projectalice',
			latitude=latitude,
			longitude=longitude,
			language=self.activeLanguage()
		)
		place = oceanData.get('ocean', dict()).get('name')
		if place:
			# add correct article to ocean name since it has to say "is is over Germany" but "it is over the Atlantic Ocean"
			place = "{} {}".format(
				self.LanguageManager.getTranslations(
					module='InternationalSpaceStation',
					key='oceanArticle',
					toLang=self.LanguageManager.activeLanguage
				)[0],
				place
			)
		else:
			countryData = self.queryApi('http://api.geonames.org/countryCodeJSON?lat={latitude}&lng={longitude}&lang={language}&username=projectalice',
				latitude=latitude,
				longitude=longitude,
				language=self.activeLanguage()
			)
			place = countryData.get('countryName')
		
		textType = 'issPlacePosition' if place else 'issPosition'

		answer = self.randomTalk(text=textType, replace=[
			"<say-as interpret-as=\"ordinal\">{:.0f}</say-as>".format(latitude),
			"<say-as interpret-as=\"ordinal\">{:.0f}</say-as>".format(longitude),
			place
		])
		self.endDialog(sessionId=session.sessionId, text=answer)


	@Decorators.anyExcept(exceptions=(RequestException, KeyError), text='noServer', printStack=True)
	@Decorators.online
	def getAstronauts(self, session: DialogSession, **_kwarg):
		data = self.queryApi('http://api.open-notify.org/astros.json')
		amount = data['number']

		if not amount:
			answer = self.randomTalk(text='noAstronauts')
		elif amount == 1:
			answer = self.randomTalk(text='oneAstronaut', replace=[data['people'][0]['name']])
		else:
			answer = self.randomTalk(text='multipleAstronauts', replace=[
				', '.join(str(x['name']) for x in data['people'][:-1]),
				data['people'][-1]['name'],
				amount
			])
		self.endDialog(sessionId=session.sessionId, text=answer)
		
