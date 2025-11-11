# Label

A text label with a colored background

Labels are scaled in screen-space. This means that they will stay the same size independent to the zoom level of the scene.

Labels do not support rich text or user editing.

Extends [Item](item.md)

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME  |              TYPE              | DESCRIPTION                     |
|:-----:|:------------------------------:|:--------------------------------|
| type  |            "LABEL"             | The type of item                |
| text  | [TextContent](text-content.md) | The text displayed in the label |
| style |   [LabelStyle](#labelstyle)    | The style of the label          |

## Type Definitions

### LabelStyle

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| backgroundColor | string | The background color of the label |
| backgroundOpacity | number | The background opacity of the label |
| cornerRadius | string | The radius of the labels corner in pixels |
| pointerWidth | number | An optional width for the label arrow in pixels |
| pointerHeight | number | An optional height for the label arrow in pixels |
| pointerDirection | "UP" \| "DOWN" \| "LEFT" \| "RIGHT" | An optional direction for the label arrow |
| maxViewScale | number | An optional maximum the label will use for screen-space scaling |
| minViewScale | number | An optional minimum the label will use for screen-space scaling |
