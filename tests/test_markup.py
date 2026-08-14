import unittest

from nastech_tts.markup import NastechMarkupError, parse_nastechml
from nastech_tts.types import SpanKind


class NastechMarkupTests(unittest.TestCase):
    def test_parses_emotion_sound_pause_and_speech(self):
        markup = """
        <speak voice="tara">
          <emotion name="angry" intensity="0.8">Stop that.</emotion>
          <sound type="cough" />
          <pause ms="300" />
          <emotion name="sad">I am sorry.</emotion>
        </speak>
        """
        voice, spans = parse_nastechml(markup)
        self.assertEqual(voice, "tara")
        self.assertEqual(
            [span.kind for span in spans],
            [
                SpanKind.SPEECH,
                SpanKind.SOUND,
                SpanKind.PAUSE,
                SpanKind.SPEECH,
            ],
        )
        self.assertEqual(spans[0].style.emotion, "angry")
        self.assertEqual(spans[0].style.intensity, 0.8)
        self.assertEqual(spans[1].value, "cough")
        self.assertEqual(spans[2].value, 300)
        self.assertEqual(spans[3].style.emotion, "sad")

    def test_rejects_unknown_sound(self):
        with self.assertRaises(NastechMarkupError):
            parse_nastechml('<speak><sound type="applause" /></speak>')

    def test_rejects_non_english_characters(self):
        with self.assertRaises(NastechMarkupError):
            parse_nastechml("<speak>Bonjour, café.</speak>")


if __name__ == "__main__":
    unittest.main()
