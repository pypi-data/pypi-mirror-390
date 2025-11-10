from typing import Annotated, Literal, TypeAlias
from pydantic import BaseModel, Field, TypeAdapter


class BasePluginEffect(BaseModel):
    """Base schema shared by plugin-based Nanoleaf effects.

    Fields:
    - animName: human-readable animation name
    - animType: must be 'plugin' for plugin effects
    - hexPalette: list of 6-digit uppercase hex colors (RRGGBB)
    """

    animName: str = Field(..., description="Human-readable name for the animation, e.g. 'Sunset breeze'.")
    animType: Literal["plugin"] = Field(..., description="Type of animation; should be the literal 'plugin'.")
    hexPalette: list[Annotated[str, Field(pattern=r"^[0-9A-F]{6}$", description="6-digit uppercase hex color (RRGGBB), no '#'")]] = Field(
        ..., description="Array of hex color strings (no '#')."
    )


class RacersTransTimeOption(BaseModel):
    """Option: transition time for the Racers effect (in ms)."""

    name: Literal["transTime"]
    value: Annotated[int, Field(..., ge=1, le=600, description="Transition time in milliseconds (1-600).")] = 450


class RacersEffect(BasePluginEffect):
    """Racers — colors race each other from one end to the other at different speeds."""

    pluginUuid: Literal["29929fc2-6905-41c0-a7d7-1582a8c11f17"]
    pluginType: Literal["color"] = Field(..., description="Effect type: 'color'.")
    pluginOptions: list[RacersTransTimeOption]


class BounceBlockSizeOption(BaseModel):
    """Option: block size for Bounce effect (number of panels grouped)."""

    name: Literal["blockSize"]
    value: Annotated[int, Field(..., ge=3, le=50, description="Block size (3-50).")] = 5


class BounceTransTimeOption(BaseModel):
    """Option: transition time for Bounce effect (in ms)."""

    name: Literal["transTime"]
    value: Annotated[int, Field(..., ge=1, le=600, description="Transition time in milliseconds (1-600).")] = 200


class BounceEffect(BasePluginEffect):
    """Bounce — colors overlap then bounce back and forth across the panels."""

    pluginUuid: Literal["db8ce916-88de-484f-bdbb-afd732053105"]
    pluginType: Literal["color"] = Field(..., description="Effect type: 'color'.")
    pluginOptions: list[BounceBlockSizeOption | BounceTransTimeOption]


class HighlightTransTimeOption(BaseModel):
    """Option: transition time for Highlight effect (in ms)."""

    name: Literal["transTime"]
    value: Annotated[int, Field(..., ge=1, le=600, description="Transition time in milliseconds (1-600).")] = 24


class HighlightDelayTimeOption(BaseModel):
    """Option: delay time between highlights (in ms)."""

    name: Literal["delayTime"]
    value: Annotated[int, Field(..., ge=0, le=600, description="Delay time in milliseconds (0-600).")] = 15


class HighlightMainColorProbOption(BaseModel):
    """Option: probability (percentage) to prefer the main palette color in Highlight."""

    name: Literal["delayTime"]
    value: Annotated[float, Field(..., ge=0, le=100, description="Probability percentage (0-100) to favor the main color.")] = 80


class HighlightEffect(BasePluginEffect):
    """Highlight — mostly shows the first palette color while other colors fade in periodically."""

    pluginUuid: Literal["70b7c636-6bf8-491f-89c1-f4103508d642"]
    pluginType: Literal["color"] = Field(..., description="Effect type: 'color'.")
    pluginOptions: list[
        HighlightTransTimeOption
        | HighlightDelayTimeOption
        | HighlightMainColorProbOption
    ]


class MeltTransTimeOption(BaseModel):
    """Option: transition time for Melt effect (in ms)."""

    name: Literal["transTime"]
    value: Annotated[int, Field(..., ge=1, le=600, description="Transition time in milliseconds (1-600).")] = 24


class MeltDelayTimeOption(BaseModel):
    """Option: delay time for Melt effect (in ms)."""

    name: Literal["delayTime"]
    value: Annotated[int, Field(..., ge=0, le=600, description="Delay time in milliseconds (0-600).")] = 0


class MeltLoopOption(BaseModel):
    """Option: whether Melt effect loops continuously."""

    name: Literal["loop"]
    value: bool = Field(True, description="If true, the effect loops continuously.")


class MeltEffect(BasePluginEffect):
    """Melt — softly fading colors that blur into each other (melting-like transitions)."""

    pluginUuid: Literal["30a017d4-e6a5-4647-8c41-5a7cd38ff907"]
    pluginType: Literal["color"] = Field(..., description="Effect type: 'color'.")
    pluginOptions: list[MeltTransTimeOption | MeltDelayTimeOption | MeltLoopOption]


class PulseTransTimeOption(BaseModel):
    """Option: transition time for Pulse effect (in ms)."""

    name: Literal["transTime"]
    value: Annotated[int, Field(..., ge=1, le=600, description="Transition time in milliseconds (1-600).")] = 24


class PulseDelayTimeOption(BaseModel):
    """Option: delay time between pulses (in ms)."""

    name: Literal["delayTime"]
    value: Annotated[int, Field(..., ge=0, le=600, description="Delay time in milliseconds (0-600).")] = 0


class PulseLoopOption(BaseModel):
    """Option: whether Pulse effect loops continuously."""

    name: Literal["loop"]
    value: bool = Field(True, description="If true, the effect loops continuously.")


class PulseEffect(BasePluginEffect):
    """Pulse — colors pulse in and out like a soft heartbeat for a soothing effect."""

    pluginUuid: Literal["0794a6b3-f6cc-452d-a900-30081604b7ec"]
    pluginType: Literal["color"] = Field(..., description="Effect type: 'color'.")
    pluginOptions: list[PulseTransTimeOption | PulseDelayTimeOption | PulseLoopOption]

# --- Additional effects from the Motion Appendix ---

# NOTE: rhythm-type effects (Streaking Notes, Sound Bar) were intentionally
# removed from the schema. If you need them later, re-add with pluginType
# == "rhythm" and appropriate pluginOptions.


class WheelLoopOption(BaseModel):
    name: Literal["loop"]
    value: bool = Field(True, description="If true, the effect loops continuously.")


class WheelTransTimeOption(BaseModel):
    name: Literal["transTime"]
    value: Annotated[int, Field(..., ge=1, le=600, description="Transition time in milliseconds (1-600).")] = 24


class WheelNColorsPerFrameOption(BaseModel):
    name: Literal["nColorsPerFrame"]
    value: Annotated[int, Field(..., ge=1, description="Number of palette colors shown per frame.")] = 1


class WheelEffect(BasePluginEffect):
    """Wheel — continuous moving gradient created from the palette (rotating color wheel)."""

    pluginUuid: Literal["6970681a-20b5-4c5e-8813-bdaebc4ee4fa"]
    pluginType: Literal["color"] = Field(..., description="Effect type: 'color'.")
    pluginOptions: list[WheelLoopOption | WheelTransTimeOption | WheelNColorsPerFrameOption]


class IntertwineBlockSizeOption(BaseModel):
    name: Literal["blockSize"]
    value: Annotated[int, Field(..., ge=1, le=20, description="Block size (1-20).")] = 1


class IntertwineFadeOutOption(BaseModel):
    name: Literal["fadeOut"]
    value: Annotated[int, Field(..., ge=0, le=20, description="Fade-out amount (0-20).")] = 1


class IntertwineEffect(BasePluginEffect):
    """Intertwine — colors appear from both sides and weave together as they overlap."""

    pluginUuid: Literal["5c4d343f-8eca-47e9-8c01-92662dff4eb6"]
    pluginType: Literal["color"] = Field(..., description="Effect type: 'color'.")
    pluginOptions: list[IntertwineBlockSizeOption | IntertwineFadeOutOption]


class FadeLoopOption(BaseModel):
    name: Literal["loop"]
    value: bool = Field(True, description="If true, the effect loops continuously.")


class FadeTransTimeOption(BaseModel):
    name: Literal["transTime"]
    value: Annotated[int, Field(..., ge=1, le=600, description="Transition time in milliseconds (1-600).")] = 24


class FadeDelayTimeOption(BaseModel):
    name: Literal["delayTime"]
    value: Annotated[int, Field(..., ge=0, le=600, description="Delay time in milliseconds (0-600).")] = 0


class FadeEffect(BasePluginEffect):
    """Fade — light panels cycle through your palette colors together."""

    pluginUuid: Literal["b3fd723a-aae8-4c99-bf2b-087159e0ef53"]
    pluginType: Literal["color"] = Field(..., description="Effect type: 'color'.")
    pluginOptions: list[FadeLoopOption | FadeTransTimeOption | FadeDelayTimeOption]


class RollerCoasterTransTimeOption(BaseModel):
    name: Literal["transTime"]
    value: Annotated[int, Field(..., ge=1, le=10000, description="Transition time in milliseconds.")] = 500


class RollerCoasterBgOption(BaseModel):
    name: Literal["enableBackgroundColor"]
    value: bool = Field(False, description="When true, a background color is used.")


class RollerCoasterEffect(BasePluginEffect):
    """Roller Coaster — fast, sweeping color motion designed to feel like a ride."""

    pluginUuid: Literal["e2eb1818-07ac-495f-a10d-7c192d7df705"]
    pluginType: Literal["color"] = Field(..., description="Effect type: 'color'.")
    pluginOptions: list[RollerCoasterTransTimeOption | RollerCoasterBgOption]


class BurstLoopOption(BaseModel):
    name: Literal["loop"]
    value: bool = Field(True, description="If true, the effect loops continuously.")


class BurstTransTimeOption(BaseModel):
    name: Literal["transTime"]
    value: Annotated[int, Field(..., ge=1, le=600, description="Transition time in milliseconds (1-600).")] = 24


class BurstDelayTimeOption(BaseModel):
    name: Literal["delayTime"]
    value: Annotated[int, Field(..., ge=0, le=600, description="Delay time in milliseconds (0-600).")] = 0


class BurstEffect(BasePluginEffect):
    """Burst — palette colors radiate outward from the center of the panels."""

    pluginUuid: Literal["713518c1-d560-47db-8991-de780af71d1e"]
    pluginType: Literal["color"] = Field(..., description="Effect type: 'color'.")
    pluginOptions: list[BurstLoopOption | BurstTransTimeOption | BurstDelayTimeOption]


class RandomTransTimeOption(BaseModel):
    name: Literal["transTime"]
    value: Annotated[int, Field(..., ge=1, le=600, description="Transition time in milliseconds (1-600).")] = 24


class RandomDelayTimeOption(BaseModel):
    name: Literal["delayTime"]
    value: Annotated[int, Field(..., ge=0, le=600, description="Delay time in milliseconds (0-600).")] = 0


class RandomEffect(BasePluginEffect):
    """Random — palette colors animate randomly across the panels."""

    pluginUuid: Literal["ba632d3e-9c2b-4413-a965-510c839b3f71"]
    pluginType: Literal["color"] = Field(..., description="Effect type: 'color'.")
    pluginOptions: list[RandomTransTimeOption | RandomDelayTimeOption]


class OrganicScaleOption(BaseModel):
    name: Literal["scale"]
    value: Annotated[float, Field(..., ge=0.01, le=5, description="Scale factor for organic clusters.")] = 1.0


class OrganicLinDirectionOption(BaseModel):
    name: Literal["linDirection"]
    value: Literal["left", "right", "up", "down"] = Field(
        "left", description="Preferred linear direction for organic flow (left/right/up/down)."
    )


class OrganicEffect(BasePluginEffect):
    """Organic — soft clusters of light appear, float and dissolve in natural-feeling forms."""

    pluginUuid: Literal["1dab05d3-07bf-4648-9d48-db8dd196ed28"]
    pluginType: Literal["color"] = Field(..., description="Effect type: 'color'.")
    pluginOptions: list[OrganicScaleOption | OrganicLinDirectionOption]


class FlowLoopOption(BaseModel):
    name: Literal["loop"]
    value: bool = Field(True, description="If true, the effect loops continuously.")


class FlowTransTimeOption(BaseModel):
    name: Literal["transTime"]
    value: Annotated[int, Field(..., ge=1, le=600, description="Transition time in milliseconds (1-600).")] = 24


class FlowDelayTimeOption(BaseModel):
    name: Literal["delayTime"]
    value: Annotated[int, Field(..., ge=0, le=600, description="Delay time in milliseconds (0-600).")] = 0


class FlowLinDirectionOption(BaseModel):
    name: Literal["linDirection"]
    value: Literal["left", "right", "up", "down"] = Field(
        "left", description="Direction for flow (left/right/up/down)."
    )


class FlowEffect(BasePluginEffect):
    """Flow — colors pour/flow across panels in a chosen direction."""

    pluginUuid: Literal["027842e4-e1d6-4a4c-a731-be74a1ebd4cf"]
    pluginType: Literal["color"] = Field(..., description="Effect type: 'color'.")
    pluginOptions: list[FlowLoopOption | FlowTransTimeOption | FlowDelayTimeOption | FlowLinDirectionOption]


# Update Effect union to include all
Effect: TypeAlias = (
    RacersEffect
    | BounceEffect
    | HighlightEffect
    | MeltEffect
    | PulseEffect
    # (rhythm effects removed)
    | WheelEffect
    | IntertwineEffect
    | FadeEffect
    | RollerCoasterEffect
    | BurstEffect
    | RandomEffect
    | OrganicEffect
    | FlowEffect
)

effect_json_schema = TypeAdapter(Effect).json_schema()
