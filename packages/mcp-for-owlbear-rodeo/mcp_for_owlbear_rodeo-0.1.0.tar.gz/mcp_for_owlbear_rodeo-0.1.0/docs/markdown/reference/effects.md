# Effects

[Effects](effect.md) allow you to create custom shaders that can generate pixels that will be shown in an Owlbear Rodeo Scene.

Effects are written in SkSL which is the shading language used by Skia (the renderer used in Owlbear Rodeo).

It is similar to OpenGL/WebGL's GLSL but with a few differences.

The main function takes in a `float2` coordinate that is in pixel units and it returns a `half4` for the color of the pixel.

For example here is a UV gradient written in SkSL.

uv.frag

``` prism-code
uniform vec2 size;

half4 main(float2 coord) {
  vec2 p = coord / size;
  return half4(p, 0.0, 1.0);
}
```

This could then be used in an Owlbear Rodeo extension:

``` prism-code
import OBR, { buildEffect } from "@owlbear-rodeo/sdk";

const sksl = `
uniform vec2 size;

half4 main(float2 coord) {
  vec2 p = coord / size;
  return half4(p, 0.0, 1.0);
}
`;

const effect = buildEffect()
  .effectType("STANDALONE")
  .width(300)
  .height(300)
  .sksl(sksl)
  .build();

OBR.scene.local.addItems([effect]);
```

This will result in a 300x300 square with a UV gradient.

note

Because of the `coord` input this UV gradient starts in the top left compared to the bottom left coordinate system found in WebGL.

## Built-In Uniforms

Above we use the `size` uniform to convert the pixel coordinate `coord` input into a 0-1 range. Alongside this there are a few more uniforms provided by default to an Effect.

|   NAME    |  TYPE  | DESCRIPTION                                           |
|:---------:|:------:|:------------------------------------------------------|
|   size    |  vec2  | The current size in pixels of the Effect              |
| position  |  vec2  | The current position of the item in world coordinates |
|   scale   |  vec2  | The current scale of the item                         |
| rotation  | number | The current rotation of the item in degrees           |
|   model   |  mat3  | The local transform of the item                       |
|   view    |  mat3  | The viewport transform                                |
| modelView |  mat3  | The full transform of the item                        |
|   time    | float  | The current unix time of the computer in seconds      |

**Example**

A UV gradient changing with the `time` uniform.

``` prism-code
import OBR, { buildEffect } from "@owlbear-rodeo/sdk";

const sksl = `
uniform vec2 size;
uniform float time;

half4 main(float2 coord) {
  vec2 p = coord / size;
  return half4(p, abs(sin(time)), 1.0);
}
`;

const effect = buildEffect()
  .effectType("STANDALONE")
  .width(300)
  .height(300)
  .sksl(sksl)
  .build();

OBR.scene.local.addItems([effect]);
```

UV gradient changing over time

## Custom Uniforms

An effect can define custom uniforms that will be passed into the shader.

**Example**

Defining two colors as [Vector3](vector3.md)'s.

``` prism-code
import OBR, { buildEffect } from "@owlbear-rodeo/sdk";

const sksl = `
uniform vec2 size;
uniform vec3 colorA;
uniform vec3 colorB;

half4 main(float2 coord) {
  vec2 p = coord / size;
  return half4(mix(colorA, colorB, p.x), 1.0);
}
`;

const effect = buildEffect()
  .effectType("STANDALONE")
  .uniforms([
    { name: "colorA", value: { x: 0.72, y: 0.17, z: 0.15 } },
    { name: "colorB", value: { x: 0.08, y: 0.39, z: 0.75 } },
  ])
  .width(300)
  .height(300)
  .sksl(sksl)
  .build();

OBR.scene.local.addItems([effect]);
```

## Effect Type

Effects come in three types "STANDALONE" \| "ATTACHMENT" \| "VIEWPORT".

Standalone Effects take the width, height and position values of the item and draw a rectangle in the scene. Attachment Effects fill the bounds of the item their attached to with the `attachedTo` value on the item. Viewport Effects fill the viewport.

**Example**

A vignette viewport effect that darkens the edges of the viewport.

``` prism-code
import OBR, { buildEffect } from "@owlbear-rodeo/sdk";

const sksl = `
uniform vec2 size;
uniform mat3 view;

half4 main(float2 coord) {
  // Convert to screen-space coordinates
  vec2 viewCoord = (vec3(coord, 1) * view).xy;
  vec2 p = viewCoord / size;
  // Center p
  p = p * 2.0 - 1.0;
  // Convert p to a circle
  float d = length(p);
  // Use d as an alpha mask
  return half4(vec3(0.0), d);
}
`;

const effect = buildEffect().effectType("VIEWPORT").sksl(sksl).build();

OBR.scene.local.addItems([effect]);
```

## Post Process

When an Effect is placed on the "POST_PROCESS" layer it has access to a new uniform called `scene`. This uniform is of type `shader` and allows this Effect to query the current color value of the Scene.

**Example**

Invert the red and blue channels of everything covered by the attached item.

``` prism-code
import OBR, { buildEffect } from "@owlbear-rodeo/sdk";

const sksl = `
uniform shader scene;
uniform mat3 modelView;

half4 main(float2 coord) {
  vec2 uv = (vec3(coord, 1) * modelView).xy;
  return scene.eval(uv).bgra;
}
`;

// Replace this with the item ID you would like to attach to
const attachedToId = "123";

const effect = buildEffect()
  .effectType("ATTACHMENT")
  .sksl(sksl)
  .locked(true)
  .disableHit(true)
  .layer("POST_PROCESS")
  .attachedTo(attachedToId)
  .build();

OBR.scene.local.addItems([effect]);
```
