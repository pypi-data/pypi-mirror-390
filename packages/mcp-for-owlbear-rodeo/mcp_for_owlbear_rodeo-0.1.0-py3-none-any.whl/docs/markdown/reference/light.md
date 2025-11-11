# Light

An light that interacts with the Dynamic Fog system.

Outside of interacting with the fog system this item has no visuals.

The `zIndex` parameter for this item is treated specially see [Dynamic Fog](dynamic-fog.md#elevation) for a break down on how this works.

*Local Only:* this Item can only be added to the local scene using the `OBR.scene.local` API.

Extends [Item](item.md)

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| type | "LIGHT" | The type of item |
| attenuationRadius | number | The outer radius of affect for this light source in world coordinates |
| sourceRadius | number | The inner radius for this light in world coordinates. This affects how hard/soft the shadows of this light will be as well as the collision distance for blocking Walls |
| falloff | number | The falloff for the outer edge of the light. This is in normalized coordinates where 0 represents no falloff and 1 full falloff. This value can be driven above 1 for even greater falloff |
| innerAngle | number | The inner angle to constrain this light from a circle to a cone. For a hard shadowed cone the `innerAngle` and `outerAngle` should be the same. For soft shadowed the `innerAngle` should be less than the `outerAngle` |
| outerAngle | number | The outer angle to constrain this light from a circle to a cone. For a hard shadowed cone the `innerAngle` and `outerAngle` should be the same. For soft shadowed the `innerAngle` should be less than the `outerAngle` |
| lightType | "PRIMARY" \| "SECONDARY" \| "AUXILIARY" | The type of light. See [here](dynamic-fog.md#secondary-lighting) for more |
