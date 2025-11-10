# nanoleafeffects

Generate Nanoleaf effects using generative AI.

## Supported generators

Currently only supports Google GenAI. Be sure to create an API key in Google AI Studio.


## Example usage

```python
from nanoleafeffects.generator import GoogleAIGenerator
generator = GoogleAIGenerator(api_key="YOUR_API_KEY", model="gemini-2.5-flash")
effect_json = generator.generate_effect("A calming blue wave effect that slowly transitions between shades of blue")
print(effect_json)
```

```json
{
  "animName": "Calming Blue Wave",
  "animType": "plugin",
  "hexPalette": ["ADD8E6", "4169E1", "00008B"],
  "pluginUuid": "027842e4-e1d6-4a4c-a731-be74a1ebd4cf",
  "pluginType": "color",
  "pluginOptions": [
    {
      "name": "loop",
      "value": true
    },
    {
      "name": "transTime",
      "value": 500
    },
    {
      "name": "delayTime",
      "value": 100
    },
    {
      "name": "linDirection",
      "value": "right"
    }
  ]
}
```