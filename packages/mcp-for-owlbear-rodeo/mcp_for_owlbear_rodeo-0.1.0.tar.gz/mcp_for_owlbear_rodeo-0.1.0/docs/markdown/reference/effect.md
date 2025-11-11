# Effect

An custom shader that is run on the GPU.

*Local Only:* this Item can only be added to the local scene using the `OBR.scene.local` API.

*Experimental:* this Item is currently experimental and the API is likely to change.

Extends [Item](item.md)

|  TYPE  |
|:------:|
| object |

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| type | "EFFECT" | The type of item |
| width | number | The width of effect when set to "STANDALONE" |
| height | number | The height of effect when set to "STANDALONE" |
| effectType | "STANDALONE" \| "ATTACHMENT" \| "VIEWPORT" | The type of effect. See [here](effects.md#effect-type) for more |
| sksl | string | The shader code to use in the Skia shading language. See [here](effects.md) for more |
| uniforms | [Uniform](#uniform%5D) | The current uniforms to pass into the effect. See [here](effects.md#custom-uniforms) for more |
| blendMode | [BlendMode](#blendmode) | The blend mode to use for the effect |

## Type Definitions

### Uniform

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| name | string | The name of the uniform. This must match the name in the shader |
| value | number \| [Vector2](vector2.md) \| [Vector3](vector3.md) \| [Matrix](matrix.md) | The value of the uniform. This must match the type in the shader |

### BlendMode

| TYPE | values |
|:--:|:---|
| string | "CLEAR" \| "SRC" \| "DST" \| "SRC_OVER" \| "DST_OVER" \| "SRC_IN" \| "DST_IN" \| "SRC_OUT" \| "DST_OUT" \| "SRC_ATOP" \| "DST_ATOP" \| "XOR" \| "PLUS" \| "MODULATE" \| "SCREEN" \| "OVERLAY" \| "DARKEN" \| "LIGHTEN" \| "COLOR_DODGE" \| "COLOR_BURN" \| "HARD_LIGHT" \| "SOFT_LIGHT" \| "DIFFERENCE" \| "EXCLUSION" \| "MULTIPLY" \| "HUE" \| "SATURATION" \| "COLOR" \| "LUMINOSITY" |
