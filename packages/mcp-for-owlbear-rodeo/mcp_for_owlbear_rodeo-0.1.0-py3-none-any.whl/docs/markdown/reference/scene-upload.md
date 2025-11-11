# SceneUploadBuilder

A builder for a new [SceneUpload](../apis/assets.md#sceneupload).

# Reference

## Methods

### `name`

``` prism-code
name(name);
```

Set the upload [`name`](../apis/assets.md#sceneupload).

**Parameters**

| NAME |  TYPE  | DESCRIPTION                    |
|:----:|:------:|:-------------------------------|
| name | string | The name of the uploaded scene |

Returns the current builder.

------------------------------------------------------------------------

### `fogFilled`

``` prism-code
fogFilled(filled);
```

Set the scenes fog [`filled`](../apis/fog.md).

**Parameters**

|  NAME  |  TYPE   | DESCRIPTION                     |
|:------:|:-------:|:--------------------------------|
| filled | boolean | The new filled state of the fog |

Returns the current builder.

------------------------------------------------------------------------

### `fogColor`

``` prism-code
fogColor(color);
```

Set the scenes fog [`color`](../apis/fog.md).

**Parameters**

| NAME  |  TYPE  | DESCRIPTION              |
|:-----:|:------:|:-------------------------|
| color | string | The new color of the fog |

Returns the current builder.

------------------------------------------------------------------------

### `fogStrokeWidth`

``` prism-code
fogStrokeWidth(width);
```

Set the scenes fog [`strokeWidth`](../apis/fog.md).

**Parameters**

| NAME  |  TYPE  | DESCRIPTION              |
|:-----:|:------:|:-------------------------|
| width | number | The new width fog stroke |

Returns the current builder.

------------------------------------------------------------------------

### `gridScale`

``` prism-code
gridScale(scale);
```

Set the scenes grid [`scale`](../apis/grid.md).

**Parameters**

| NAME  |  TYPE  | DESCRIPTION                   |
|:-----:|:------:|:------------------------------|
| scale | string | The new raw scale of the grid |

Returns the current builder.

------------------------------------------------------------------------

### `gridColor`

``` prism-code
gridColor(color);
```

Set the scenes grid [`color`](../apis/grid.md).

**Parameters**

| NAME  |                  TYPE                  | DESCRIPTION               |
|:-----:|:--------------------------------------:|:--------------------------|
| color | [GridColor](../apis/grid.md#gridcolor) | The new color of the grid |

Returns the current builder.

------------------------------------------------------------------------

### `gridOpacity`

``` prism-code
gridOpacity(opacity);
```

Set the scenes grid [`opacity`](../apis/grid.md).

**Parameters**

|  NAME   |  TYPE  | DESCRIPTION                                 |
|:-------:|:------:|:--------------------------------------------|
| opacity | number | The new opacity of the grid between 0 and 1 |

Returns the current builder.

------------------------------------------------------------------------

### `gridLineType`

``` prism-code
gridLineType(lineType);
```

Set the scenes grid [`lineType`](../apis/grid.md).

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| lineType | [GridLineType](../apis/grid.md#gridlinetype) | The new type of the grid line |

Returns the current builder.

------------------------------------------------------------------------

### `gridMeasurement`

``` prism-code
gridMeasurement(measurement);
```

Set the scenes grid [`measurement`](../apis/grid.md).

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| measurement | [GridMeasurement](../apis/grid.md#gridmeasurement) | The new measurement type of the grid |

Returns the current builder.

------------------------------------------------------------------------

### `gridType`

``` prism-code
gridType(type);
```

Set the scene grids [`type`](../apis/grid.md).

**Parameters**

| NAME |                 TYPE                 | DESCRIPTION              |
|:----:|:------------------------------------:|:-------------------------|
| type | [GridType](../apis/grid.md#gridtype) | The new type of the grid |

Returns the current builder.

------------------------------------------------------------------------

### `items`

``` prism-code
items(items);
```

Set the scenes default [items](item.md).

**Parameters**

| NAME  |        TYPE         | DESCRIPTION                          |
|:-----:|:-------------------:|:-------------------------------------|
| Items | [Item](item.md)\[\] | The default items used for the scene |

Returns the current builder.

------------------------------------------------------------------------

### `baseMap`

``` prism-code
baseMap(baseMap);
```

Set the scenes base map that should be included with this scene during upload.

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| baseMap | [ImageUpload](../apis/assets.md#imageupload) | The image to upload as a map |

Returns the current builder.

------------------------------------------------------------------------

### `build`

``` prism-code
build();
```

Returns the final [SceneUpload](../apis/assets.md#sceneupload).

------------------------------------------------------------------------
