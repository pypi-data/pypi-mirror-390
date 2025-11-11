# Image

An image item that loads from a url

Extends [Item](item.md)

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| type | "IMAGE" | The type of item |
| image | [ImageContent](#imagecontent) | The image to show |
| grid | [ImageGrid](#imagegrid) | The grid scale of the image |
| text | [TextContent](text-content.md) | The text displayed over the image |
| textItemType | "LABEL" \| "TEXT" | The type of text to use for this image. The "LABEL" option will display the text as a label on the bottom of the image. The "TEXT" option will display the text over the top of the image. |

## Type Definitions

### ImageContent

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| width | number | The width of the image in pixels |
| height | number | The height of the image in pixels |
| mime | string | The mime type of the image e.g. "image/jpeg" or "video/mp4" |
| url | string | The url of the image to load. The image must have CORS enabled |

### ImageGrid

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| offset | [Vector2](vector2.md)\[\] | Offset relative to the image dimensions |
| dpi | number | Dots per inch of the image. Determines the resolution of one grid cell in the image. |
