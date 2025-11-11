# Fog

## `OBR.scene.fog`

Interact with the base fog settings for this scene.

# Reference

## Methods

### `getColor`

``` prism-code
async getColor()
```

Get the color of the scenes fog.

Returns a string.

------------------------------------------------------------------------

### `setColor`

``` prism-code
async setColor(color)
```

Set the color of the scenes fog.

**Parameters**

| NAME  |  TYPE  | DESCRIPTION              |
|:-----:|:------:|:-------------------------|
| color | string | The new color of the fog |

------------------------------------------------------------------------

### `getStrokeWidth`

``` prism-code
async getStrokeWidth()
```

Get the stroke width of the scenes fog.

Returns a number.

------------------------------------------------------------------------

### `setStrokeWidth`

``` prism-code
async setStrokeWidth(width)
```

Set the stroke width of the scenes fog.

**Parameters**

| NAME  |  TYPE  | DESCRIPTION              |
|:-----:|:------:|:-------------------------|
| width | number | The new width fog stroke |

------------------------------------------------------------------------

### `getFilled`

``` prism-code
async getFilled()
```

Returns true if the scene if filled with fog.

------------------------------------------------------------------------

### `setFilled`

``` prism-code
async setFilled(filled)
```

Set the filled state of the scenes fog.

**Parameters**

|  NAME  |  TYPE   | DESCRIPTION                     |
|:------:|:-------:|:--------------------------------|
| filled | boolean | The new filled state of the fog |

------------------------------------------------------------------------

### `onChange`

``` prism-code
onChange(callback);
```

**Parameters**

|   NAME   |            TYPE             | DESCRIPTION                         |
|:--------:|:---------------------------:|:------------------------------------|
| callback | (fog: [Fog](#fog)) =\> void | A callback for when the fog changes |

Returns a function that when called will unsubscribe from change events.

**Example**

``` prism-code
/**
 * Use an `onChange` event with a React `useEffect`.
 * `onChange` returns an unsubscribe event to make this easy.
 */
useEffect(
  () =>
    OBR.scene.fog.onChange((fog) => {
      // React to fog changes
    }),
  []
);
```

------------------------------------------------------------------------

## Type Definitions

### Fog

The fog state for a scene.

|  TYPE  |
|:------:|
| object |

**Properties**

|  NAME  |         TYPE          | DESCRIPTION                  |
|:------:|:---------------------:|:-----------------------------|
| filled |        boolean        | Is the fog filling the scene |
| style  | [FogStyle](#fogstyle) | The style of the fog         |

------------------------------------------------------------------------

### FogStyle

|  TYPE  |
|:------:|
| object |

**Properties**

|    NAME     |  TYPE  | DESCRIPTION                         |
|:-----------:|:------:|:------------------------------------|
|    color    | string | The color of the fog                |
| strokeWidth | number | An optional width of the fog stroke |

------------------------------------------------------------------------
