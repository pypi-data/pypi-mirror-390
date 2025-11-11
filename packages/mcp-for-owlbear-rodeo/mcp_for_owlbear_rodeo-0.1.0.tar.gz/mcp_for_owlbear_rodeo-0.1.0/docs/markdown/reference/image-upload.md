# ImageUploadBuilder

A builder for a new [ImageUpload](../apis/assets.md#imageupload).

# Reference

### `constructor`

``` prism-code
buildImageUpload(file);
```

Create an image upload builder for the given file.

**Parameters**

| NAME |     TYPE     | DESCRIPTION              |
|:----:|:------------:|:-------------------------|
| file | File \| Blob | The image file to upload |

------------------------------------------------------------------------

## Methods

### `dpi`

``` prism-code
dpi(dpi);
```

Set the grid [`dpi`](../apis/assets.md#imageupload).

**Parameters**

| NAME |  TYPE  | DESCRIPTION               |
|:----:|:------:|:--------------------------|
| dpi  | number | The dpi of the image grid |

Returns the current builder.

------------------------------------------------------------------------

### `offset`

``` prism-code
offset(offset);
```

Set the grid [`offset`](../apis/assets.md#imageupload).

**Parameters**

|  NAME  |         TYPE          | DESCRIPTION                  |
|:------:|:---------------------:|:-----------------------------|
| offset | [Vector2](vector2.md) | The offset of the image grid |

Returns the current builder.

------------------------------------------------------------------------

### `name`

``` prism-code
name(name);
```

Set the upload [`name`](../apis/assets.md#imageupload).

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| name | string | The name of the uploaded image. If left blank and a File input is used the `file.name` property will be used |

Returns the current builder.

------------------------------------------------------------------------

### `description`

``` prism-code
description(description: string)
```

Set the items [`description`](../apis/assets.md#imageupload).

**Parameters**

|    NAME     |  TYPE  | DESCRIPTION     |
|:-----------:|:------:|:----------------|
| description | string | The description |

Returns the current builder.

------------------------------------------------------------------------

### `rotation`

``` prism-code
rotation(rotation);
```

Set the image [`rotation`](../apis/assets.md#imageupload).

**Parameters**

|   NAME   |  TYPE  | DESCRIPTION                                  |
|:--------:|:------:|:---------------------------------------------|
| rotation | number | The default rotation of the image in degrees |

Returns the current builder.

------------------------------------------------------------------------

### `scale`

``` prism-code
scale(scale);
```

Set the image [`scale`](../apis/assets.md#imageupload).

**Parameters**

| NAME  |         TYPE          | DESCRIPTION                    |
|:-----:|:---------------------:|:-------------------------------|
| scale | [Vector2](vector2.md) | The default scale of the image |

Returns the current builder.

------------------------------------------------------------------------

### `locked`

``` prism-code
locked(locked);
```

Set the items [`locked`](../apis/assets.md#imageupload) boolean.

**Parameters**

|  NAME  |  TYPE   | DESCRIPTION        |
|:------:|:-------:|:-------------------|
| locked | boolean | The locked setting |

Returns the current builder.

------------------------------------------------------------------------

### `visible`

``` prism-code
visible(visible);
```

Set the items [`visible`](../apis/assets.md#imageupload) boolean.

**Parameters**

|  NAME   |  TYPE   | DESCRIPTION         |
|:-------:|:-------:|:--------------------|
| visible | boolean | The visible setting |

Returns the current builder.

------------------------------------------------------------------------

### `text`

``` prism-code
text(text);
```

Set the images [`text content`](../apis/assets.md#imageupload).

**Parameters**

| NAME |              TYPE              | DESCRIPTION                    |
|:----:|:------------------------------:|:-------------------------------|
| text | [TextContent](text-content.md) | The content of the images text |

Returns the current builder.

------------------------------------------------------------------------

### `textItemType`

``` prism-code
textItemType(textItemType);
```

Set the images [`text item type`](../apis/assets.md#imageupload).

**Parameters**

|     NAME     |       TYPE        | DESCRIPTION                 |
|:------------:|:-----------------:|:----------------------------|
| textItemType | "LABEL" \| "TEXT" | The type of the images text |

Returns the current builder.

------------------------------------------------------------------------

### `textWidth`

``` prism-code
textWidth(width);
```

Set the image texts [`width`](../apis/assets.md#imageupload).

**Parameters**

| NAME  |                 TYPE                 | DESCRIPTION    |
|:-----:|:------------------------------------:|:---------------|
| width | [TextSize](text-content.md#textsize) | The text width |

Returns the current builder.

------------------------------------------------------------------------

### `textHeight`

``` prism-code
textHeight(height);
```

Set the image texts [`height`](../apis/assets.md#imageupload).

**Parameters**

|  NAME  |                 TYPE                 | DESCRIPTION     |
|:------:|:------------------------------------:|:----------------|
| height | [TextSize](text-content.md#textsize) | The text height |

Returns the current builder.

------------------------------------------------------------------------

### `richText`

``` prism-code
richText(richText);
```

Set the image texts [`richText`](../apis/assets.md#imageupload).

**Parameters**

|   NAME   |                 TYPE                 | DESCRIPTION   |
|:--------:|:------------------------------------:|:--------------|
| richText | [RichText](text-content.md#richtext) | The rich text |

Returns the current builder.

------------------------------------------------------------------------

### `plainText`

``` prism-code
plainText(plainText);
```

Set the image texts [`plainText`](../apis/assets.md#imageupload).

**Parameters**

|   NAME    |  TYPE  | DESCRIPTION    |
|:---------:|:------:|:---------------|
| plainText | string | The plain text |

Returns the current builder.

------------------------------------------------------------------------

### `textType`

``` prism-code
textType(textType);
```

Set the image texts [`textType`](../apis/assets.md#imageupload).

**Parameters**

|   NAME   |       TYPE        | DESCRIPTION   |
|:--------:|:-----------------:|:--------------|
| textType | "PLAIN" \| "RICH" | The text type |

Returns the current builder.

------------------------------------------------------------------------

### `textPadding`

``` prism-code
textPadding(padding);
```

Set the image text styles [`padding`](text-content.md#textstyle).

**Parameters**

|  NAME   |  TYPE  | DESCRIPTION      |
|:-------:|:------:|:-----------------|
| padding | number | The text padding |

Returns the current builder.

------------------------------------------------------------------------

### `fontFamily`

``` prism-code
fontFamily(fontFamily);
```

Set the image text styles [`fontFamily`](text-content.md#textstyle).

**Parameters**

|    NAME    |  TYPE  | DESCRIPTION          |
|:----------:|:------:|:---------------------|
| fontFamily | string | The text font family |

Returns the current builder.

------------------------------------------------------------------------

### `fontSize`

``` prism-code
fontSize(fontSize);
```

Set the image text styles [`fontSize`](text-content.md#textstyle).

**Parameters**

|   NAME   |  TYPE  | DESCRIPTION        |
|:--------:|:------:|:-------------------|
| fontSize | number | The text font size |

Returns the current builder.

------------------------------------------------------------------------

### `fontWeight`

``` prism-code
fontWeight(fontWeight);
```

Set the image text styles [`fontWeight`](text-content.md#textstyle).

**Parameters**

|    NAME    |  TYPE  | DESCRIPTION          |
|:----------:|:------:|:---------------------|
| fontWeight | number | The text font weight |

Returns the current builder.

------------------------------------------------------------------------

### `textAlign`

``` prism-code
textAlign(textAlign);
```

Set the image text styles [`textAlign`](text-content.md#textstyle).

**Parameters**

|   NAME    |             TYPE              | DESCRIPTION                   |
|:---------:|:-----------------------------:|:------------------------------|
| textAlign | "LEFT" \| "CENTER" \| "RIGHT" | The text horizontal alignment |

Returns the current builder.

------------------------------------------------------------------------

### `textAlignVertical`

``` prism-code
textAlignVertical(textAlignVertical);
```

Set the image text styles [`textAlignVertical`](text-content.md#textstyle).

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| textAlignVertical | "BOTTOM" \| "MIDDLE" \| "TOP" | The text vertical alignment |

Returns the current builder.

------------------------------------------------------------------------

### `textFillColor`

``` prism-code
textFillColor(fillColor);
```

Set the image text styles [`fillColor`](text-content.md#textstyle).

**Parameters**

|   NAME    |  TYPE  | DESCRIPTION          |
|:---------:|:------:|:---------------------|
| fillColor | string | The texts fill color |

Returns the current builder.

------------------------------------------------------------------------

### `textFillOpacity`

``` prism-code
textFillOpacity(fillOpacity);
```

Set the image text styles [`fillOpacity`](text-content.md#textstyle).

**Parameters**

|    NAME     |  TYPE  | DESCRIPTION            |
|:-----------:|:------:|:-----------------------|
| fillOpacity | number | The texts fill opacity |

Returns the current builder.

------------------------------------------------------------------------

### `textStrokeColor`

``` prism-code
textStrokeColor(strokeColor);
```

Set the image text styles [`strokeColor`](text-content.md#textstyle).

**Parameters**

|    NAME     |  TYPE  | DESCRIPTION            |
|:-----------:|:------:|:-----------------------|
| strokeColor | string | The texts stroke color |

Returns the current builder.

------------------------------------------------------------------------

### `textStrokeOpacity`

``` prism-code
textStrokeOpacity(strokeOpacity);
```

Set the image text styles [`strokeOpacity`](text-content.md#textstyle).

**Parameters**

|     NAME      |  TYPE  | DESCRIPTION              |
|:-------------:|:------:|:-------------------------|
| strokeOpacity | number | The texts stroke opacity |

Returns the current builder.

------------------------------------------------------------------------

### `textStrokeWidth`

``` prism-code
textStrokeWidth(strokeWidth);
```

Set the image text styles [`strokeWidth`](text-content.md#textstyle).

**Parameters**

|    NAME     |  TYPE  | DESCRIPTION            |
|:-----------:|:------:|:-----------------------|
| strokeWidth | number | The texts stroke width |

Returns the current builder.

------------------------------------------------------------------------

### `textLineHeight`

``` prism-code
textLineHeight(lineHeight);
```

Set the image text styles [`lineHeight`](text-content.md#textstyle).

**Parameters**

|    NAME    |  TYPE  | DESCRIPTION           |
|:----------:|:------:|:----------------------|
| lineHeight | number | The texts line height |

Returns the current builder.

------------------------------------------------------------------------

### `build`

``` prism-code
build();
```

Returns the final [ImageUpload](../apis/assets.md#imageupload).

------------------------------------------------------------------------
