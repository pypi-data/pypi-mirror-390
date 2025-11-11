# Wall

An invisible wall that interacts with the Dynamic Fog system.

The `zIndex` parameter for this item is treated specially see [Dynamic Fog](dynamic-fog.md#elevation) for a break down on how this works.

*Local Only:* this Item can only be added to the local scene using the `OBR.scene.local` API.

Extends [Item](item.md)

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| type | "WALL" | The type of item |
| points | [Vector2](vector2.md)\[\] | The list of points to for the wall |
| doubleSided | boolean | Whether this wall will produce shadows from both sides. If false the shadowed side of the wall will be determined by the winding of the `points` array |
| blocking | boolean | Whether this wall will stop lights (or anything a light is attached to) from moving through it |
