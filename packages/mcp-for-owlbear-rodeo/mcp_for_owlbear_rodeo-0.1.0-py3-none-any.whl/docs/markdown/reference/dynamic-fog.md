# Dynamic Fog

The Dynamic Fog system is controlled with the [Light](light.md) and [Wall](wall.md) items.

Lights support soft edges with the `falloff` parameter and soft shadows with the `sourceRadius` parameter. Walls support single sided shadows by disabling the `doubleSided` parameter and collision with lights and tokens with the `blocking` parameter.

### Elevation

The Dynamic Fog takes over the `zIndex` parameter for both wall and lights to control how each is processed.

For wall and lights the `zIndex` is used to filter which walls affect which lights. For example a light with a `zIndex` of 1 will only be affected by a wall with a `zIndex` of 1 or greater. This can be used to create multiple elevated surfaces for multiple storied maps.

Secondly the `zIndex` value is used to determine whether the dynamic fog is drawn below or above the static fog in a Scene. Any `zIndex` value below 0 will cause the dynamic lighting to be drawn below static fog while any `zIndex` equal or greater to 0 will be drawn above. This means any positive `zIndex` will cut away from existing fog while negative `zIndex` values will be hidden by existing fog. This property also interacts with elevation where the absolute value of the zIndex is used to create each elevation. So a light with a `zIndex` of -1 will only be affected by a wall with a `zIndex` of -1 or less.

### Secondary Lighting

Each light can be of `lightType` `PRIMARY`, `SECONDARY` or `AUXILIARY` a primary light is a regular shadow casting light that when visible will always cut away from the fog. A secondary light however only effects fog that can be seen by a primary light. For example setting a light above the enemies campfire as secondary will mean that the camp will only be visible once a player with a primary light gains line of sight to that fire. An auxiliary light will cast shadows like a primary light but it will not trigger any secondary lights.

### Performance

The Dynamic Fog is processed on the GPU using various vertex and fragment shaders then composited back into the OBR Scene. The performance of the Dynamic Fog depends on how many walls/lights are used but also on what parameters are used for each item.

There are two rendering paths implemented depending on what parameters are used for the lights and walls in a Scene. The faster rendering path will be used for any light that has a `sourceRadius` of 0. This will disable the soft shadows but can handle many more lights before potential performance issues occur. It is recommended if you are going to add many lights (more than a few dozen) to a Scene that those lights use a `sourceRadius` of 0. In a single Scene you can mix soft shadowed and hard shadowed lights. For example you can use soft shadowed lights for key character lights but fallback to hard shadowed lights for environment objects. A caveat to this exists with the `doubleSided` parameter for walls. Currently enabling this parameter on any wall in a Scene will force all lights to use the soft shadowed rendering path no matter on the `sourceRadius` of the light.

If a secondary light is on screen then a second shadow pass needs to be done. This secondary pass will need to render all primary lights a second time (even those off screen). This will possibly 2x the render time for dynamic fog so we recommend using secondary lighting in smaller Scenes or those with cheaper lighting.
