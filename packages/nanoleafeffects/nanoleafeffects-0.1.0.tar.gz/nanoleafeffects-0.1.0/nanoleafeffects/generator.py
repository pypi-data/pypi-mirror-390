from google import genai
from nanoleafeffects.schema import Effect

class GoogleAiGenerator:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash") -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model


    def generate_effect(self, description: str) -> str:
        """Generate a Nanoleaf Essentials Outdoor String Lights effect JSON based on the provided description."""
        prompt = f"""
        Generate a Nanoleaf Essentials Outdoor String Lights AI Effect JSON adhering to the following specification between specification tags:
        <specification>
        {description}
        </specification>
        The effect should loop indefinitely. Adhere to the JSON schema provided exactly, taking care to use valid values for all fields.
        """
        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": Effect,
            },
        )
        assert response.text
        return response.text


if __name__ == "__main__":
    import os
    import sys
    generator = GoogleAiGenerator(api_key=os.environ["GEMINI_API_KEY"])
    description = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "A soothing color wave effect that transitions smoothly between pastel colors."
    effect_json = generator.generate_effect(description)
    print(effect_json)