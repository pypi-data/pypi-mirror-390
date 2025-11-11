# Billboard

A billboard image that loads from a url.

Billboards are scaled in screen-space. This means that they will stay the same size independent to the zoom level of the scene.

*Local Only:* this Item can only be added to the local scene using the `OBR.scene.local` API.

Extends [Item](item.md)

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME  |                 TYPE                  | DESCRIPTION                 |
|:-----:|:-------------------------------------:|:----------------------------|
| type  |              "BILLBOARD"              | The type of item            |
| image | [ImageContent](image.md#imagecontent) | The image to show           |
| grid  |    [ImageGrid](image.md#imagegrid)    | The grid scale of the image |
| style |   [BillboardStyle](#billboardstyle)   | The style of the billboard  |

## Type Definitions

### BillboardStyle

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| maxViewScale | number | An optional maximum the billboard will use for screen-space scaling |
| minViewScale | number | An optional minimum the billboard will use for screen-space scaling |
