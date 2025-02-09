"""Support for IBM Watson TTS integration."""
import logging

import voluptuous as vol

from homeassistant.components.tts import PLATFORM_SCHEMA, Provider
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_URL = 'watson_url'
CONF_APIKEY = 'watson_apikey'
ATTR_CREDENTIALS = 'credentials'

DEFAULT_URL = 'https://stream.watsonplatform.net/text-to-speech/api'

CONF_VOICE = 'voice'
CONF_OUTPUT_FORMAT = 'output_format'
CONF_OUTPUT_AUDIO_RATE = 'output_audio_rate'
CONF_TEXT_TYPE = 'text'

# List from https://tinyurl.com/watson-tts-docs
SUPPORTED_VOICES = [
    "de-DE_BirgitVoice",
    "de-DE_BirgitV2Voice",
    "de-DE_DieterVoice",
    "de-DE_DieterV2Voice",
    "en-GB_KateVoice",
    "en-US_AllisonVoice",
    "en-US_AllisonV2Voice",
    "en-US_LisaVoice",
    "en-US_LisaV2Voice",
    "en-US_MichaelVoice",
    "en-US_MichaelV2Voice",
    "es-ES_EnriqueVoice",
    "es-ES_LauraVoice",
    "es-LA_SofiaVoice",
    "es-US_SofiaVoice",
    "fr-FR_ReneeVoice",
    "it-IT_FrancescaVoice",
    "it-IT_FrancescaV2Voice",
    "ja-JP_EmiVoice",
    "pt-BR_IsabelaVoice"
]

SUPPORTED_OUTPUT_FORMATS = [
    'audio/flac',
    'audio/mp3',
    'audio/mpeg',
    'audio/ogg',
    'audio/ogg;codecs=opus',
    'audio/ogg;codecs=vorbis',
    'audio/wav'
]

CONTENT_TYPE_EXTENSIONS = {
    'audio/flac': 'flac',
    'audio/mp3': 'mp3',
    'audio/mpeg': 'mp3',
    'audio/ogg': 'ogg',
    'audio/ogg;codecs=opus': 'ogg',
    'audio/ogg;codecs=vorbis': 'ogg',
    'audio/wav': 'wav',
}

DEFAULT_VOICE = 'en-US_AllisonVoice'
DEFAULT_OUTPUT_FORMAT = 'audio/mp3'


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_URL, default=DEFAULT_URL): cv.string,
    vol.Required(CONF_APIKEY): cv.string,
    vol.Optional(CONF_VOICE, default=DEFAULT_VOICE): vol.In(SUPPORTED_VOICES),
    vol.Optional(CONF_OUTPUT_FORMAT, default=DEFAULT_OUTPUT_FORMAT):
        vol.In(SUPPORTED_OUTPUT_FORMATS),
    vol.Optional(CONF_OUTPUT_AUDIO_RATE): cv.positive_int,
})


def get_engine(hass, config):
    """Set up IBM Watson TTS component."""
    from ibm_watson import TextToSpeechV1

    service = TextToSpeechV1(
        url=config[CONF_URL],
        iam_apikey=config[CONF_APIKEY]
    )

    supported_languages = list({s[:5] for s in SUPPORTED_VOICES})
    default_voice = config[CONF_VOICE]
    output_format = config[CONF_OUTPUT_FORMAT]
    output_audio_rate = config.get(CONF_OUTPUT_AUDIO_RATE, None)

    return WatsonTTSProvider(
        service, supported_languages, default_voice,
        output_format, output_audio_rate)


class WatsonTTSProvider(Provider):
    """IBM Watson TTS api provider."""

    def __init__(self,
                 service,
                 supported_languages,
                 default_voice,
                 output_format,
                 output_audio_rate):
        """Initialize Watson TTS provider."""
        self.service = service
        self.supported_langs = supported_languages
        self.default_lang = default_voice[:5]
        self.default_voice = default_voice
        self.output_format = output_format
        self.output_audio_rate = output_audio_rate
        self.name = 'Watson TTS'

    @property
    def supported_languages(self):
        """Return a list of supported languages."""
        return self.supported_langs

    @property
    def default_language(self):
        """Return the default language."""
        return self.default_lang

    @property
    def default_options(self):
        """Return dict include default options."""
        return {CONF_VOICE: self.default_voice}

    @property
    def supported_options(self):
        """Return a list of supported options."""
        return [CONF_VOICE]

    def get_tts_audio(self, message, language=None, options=None):
        """Request TTS file from Watson TTS."""
        output_format = self.output_format
        if self.output_audio_rate:
            output_format += f";rate={self.output_audio_rate}"

        response = self.service.synthesize(
            message, accept=output_format,
            voice=self.default_voice).get_result()

        return (CONTENT_TYPE_EXTENSIONS[self.output_format],
                response.content)
