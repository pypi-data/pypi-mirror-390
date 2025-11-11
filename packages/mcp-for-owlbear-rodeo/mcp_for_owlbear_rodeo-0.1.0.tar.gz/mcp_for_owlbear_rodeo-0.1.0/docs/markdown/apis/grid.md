# Grid

## `OBR.scene.grid`

Interact with the scene's grid.

# Reference

## Methods

### `getDpi`

``` prism-code
async getDpi()
```

Get the dots per inch (DPI) of the grid. Determines the resolution of one grid cell. For square grids this represents both the width and height of the grid cell. For vertically oriented hex grids this is the width of the grid cell. For horizontally oriented hex grids this is the height of the grid cell. For isometric and dimetric grids this is the post-transform height of the grid cell.

returns a number.

------------------------------------------------------------------------

### `getScale`

``` prism-code
async getScale()
```

Get the current scale of the grid.

Returns a [GridScale](#gridscale).

------------------------------------------------------------------------

### `setScale`

``` prism-code
async setScale(scale)
```

Set the scale of the grid as a raw string.

**Parameters**

| NAME  |  TYPE  | DESCRIPTION                   |
|:-----:|:------:|:------------------------------|
| scale | string | The new raw scale of the grid |

**Example**

``` prism-code
OBR.scene.grid.setScale("5ft");
```

------------------------------------------------------------------------

### `getColor`

``` prism-code
async getColor()
```

Get the current color of the grid.

Returns a [GridColor](#gridcolor).

------------------------------------------------------------------------

### `setColor`

``` prism-code
async setColor(color)
```

Set the color of the grid.

**Parameters**

| NAME  |          TYPE           | DESCRIPTION               |
|:-----:|:-----------------------:|:--------------------------|
| color | [GridColor](#gridcolor) | The new color of the grid |

**Example**

``` prism-code
OBR.scene.grid.setColor("DARK");
```

------------------------------------------------------------------------

### `getOpacity`

``` prism-code
async getOpacity()
```

Get the current opacity of the grid between 0 and 1.

Returns a number.

------------------------------------------------------------------------

### `setOpacity`

``` prism-code
async setOpacity(opacity)
```

Set the opacity of the grid.

**Parameters**

|  NAME   |  TYPE  | DESCRIPTION                                 |
|:-------:|:------:|:--------------------------------------------|
| opacity | number | The new opacity of the grid between 0 and 1 |

------------------------------------------------------------------------

### `getType`

``` prism-code
async getType()
```

Get the current grid type.

Returns a [GridType](#gridtype).

------------------------------------------------------------------------

### `setType`

``` prism-code
async setType(type)
```

Set the type of the grid.

**Parameters**

| NAME |         TYPE          | DESCRIPTION              |
|:----:|:---------------------:|:-------------------------|
| type | [GridType](#gridtype) | The new type of the grid |

**Example**

``` prism-code
OBR.scene.grid.setType("HEX_VERTICAL");
```

------------------------------------------------------------------------

### `getLineType`

``` prism-code
async getLineType()
```

Get the current grid line type.

Returns a [GridLineType](#gridlinetype).

------------------------------------------------------------------------

### `setLineType`

``` prism-code
async setLineType(lineType)
```

Set the type of the grid line.

**Parameters**

|   NAME   |             TYPE              | DESCRIPTION                   |
|:--------:|:-----------------------------:|:------------------------------|
| lineType | [GridLineType](#gridlinetype) | The new type of the grid line |

**Example**

``` prism-code
OBR.scene.grid.setLineType("DASHED");
```

------------------------------------------------------------------------

### `getMeasurement`

``` prism-code
async getMeasurement()
```

Get the current grid measurement type.

Returns a [GridMeasurement](#gridmeasurement).

------------------------------------------------------------------------

### `setMeasurement`

``` prism-code
async setMeasurement(measurement)
```

Set the measurement type of the grid.

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| measurement | [GridMeasurement](#gridmeasurement) | The new measurement type of the grid |

**Example**

``` prism-code
OBR.scene.grid.setMeasurement("EUCLIDEAN");
```

------------------------------------------------------------------------

### `getLineWidth`

``` prism-code
async getLineWidth()
```

Get the current line width of the grid in pixels.

Returns a number.

------------------------------------------------------------------------

### `setLineWidth`

``` prism-code
async setLineWidth(lineWidth)
```

Set the width of the grid lines.

**Parameters**

|   NAME    |  TYPE  | DESCRIPTION                                               |
|:---------:|:------:|:----------------------------------------------------------|
| lineWidth | number | The new line width of the grid, must be greater than zero |

------------------------------------------------------------------------

### `snapPosition`

``` prism-code
async snapPosition(position, snappingSensitivity, useCorners)
```

Snap a [Vector2](../reference/vector2.md) position to the nearest grid cell using the current grid settings.

Returns a [Vector2](../reference/vector2.md) with the new position.

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| position | [Vector2](../reference/vector2.md) | The position to snap |
| snappingSensitivity | number | An optional number between 0 and 1. Leave undefined to use the users snapping preference. A value of 0 will disable snapping. A value of 1 will completely snap to the grid. |
| useCorners | boolean | An optional boolean. If true the corners of the grid cell will be valid snap locations. Defaults to true. |
| useCenter | boolean | An optional boolean. If true the center of the grid cell will be a valid snap location. Defaults to true. |

------------------------------------------------------------------------

### `getDistance`

``` prism-code
async getDistance(from, to)
```

Get the distance between two [Vector2](../reference/vector2.md)s on the Scenes grid.

Returns the shortest distance between the two inputs using the current [GridMeasurement](#gridmeasurement) for the scene. When set to "EUCLIDEAN" this will be the exact distance. For all other measurement types this will be an integer of how many grid cells were traversed.

**Parameters**

| NAME |                TYPE                | DESCRIPTION                  |
|:----:|:----------------------------------:|:-----------------------------|
| from | [Vector2](../reference/vector2.md) | The start position in pixels |
|  to  | [Vector2](../reference/vector2.md) | The end position in pixels   |

------------------------------------------------------------------------

### `onChange`

``` prism-code
onChange(callback);
```

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| callback | (grid: [Grid](#grid)) =\> void | A callback for when the grid changes |

Returns a function that when called will unsubscribe from change events.

**Example**

``` prism-code
/**
 * Use an `onChange` event with a React `useEffect`.
 * `onChange` returns an unsubscribe event to make this easy.
 */
useEffect(
  () =>
    OBR.scene.grid.onChange((grid) => {
      // React to grid changes
    }),
  []
);
```

------------------------------------------------------------------------

## Type Definitions

### Grid

The grid for a scene.

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| dpi | number | Dots per inch of the scene. Determines the resolution of one grid cell. For square grids this represents both the width and height of the grid cell. For vertically oriented hex grids this is the width of the grid cell. For horizontally oriented hex grids this is the height of the grid cell. |
| style | [GridStyle](#gridstyle) | The style of the grid |
| type | [GridType](#gridtype) | The type of the grid |
| measurement | [GridMeasurement](#gridmeasurement) | The measurement type of the grid |
| scale | string | The raw scale of the grid. For example `5ft` |

------------------------------------------------------------------------

### GridStyle

The style of a grid.

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| lineType | [GridLineType](#gridlinetype) | The style of the grid line |
| lineOpacity | number | The opacity of the grid line between 0 and 1 |
| lineColor | [GridColor](#gridcolor) | The color of the grid line |
| lineWidth | number | The width of the grid line |

------------------------------------------------------------------------

### GridLineType

The type of a grid line.

|  TYPE  | values                          |
|:------:|:--------------------------------|
| string | "SOLID" \| "DASHED" \| "DOTTED" |

------------------------------------------------------------------------

### GridColor

The color of a grid line.

|  TYPE  | values                                     |
|:------:|:-------------------------------------------|
| string | "DARK" \| "LIGHT" \| "HIGHLIGHT" \| string |

------------------------------------------------------------------------

### GridType

The type of a grid.

| TYPE | values |
|:--:|:---|
| string | "SQUARE" \| "HEX_VERTICAL" \| "HEX_HORIZONTAL" \| "DIMETRIC" \| "ISOMETRIC" |

------------------------------------------------------------------------

### GridMeasurement

The type of a grid measurement.

|  TYPE  | values                                                     |
|:------:|:-----------------------------------------------------------|
| string | "CHEBYSHEV" \| "ALTERNATING" \| "EUCLIDEAN" \| "MANHATTAN" |

------------------------------------------------------------------------

### GridScale

The scale of a grid.

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| raw | string | The raw grid scale. For example `5ft` |
| parsed | [ParsedGridScale](#parsedgridscale) | The raw grid scale parsed into a more usable form |

### ParsedGridScale

The raw grid scale parsed into a more usable form

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| multiplier | number | The number multiplier of the scale. For example `5` for a `5ft` scale |
| unit | string | The unit of the scale. For example `ft` for a `5ft` scale |
| digits | number | The precision of the scale. For example `2` for a `5.00ft` scale |

------------------------------------------------------------------------
