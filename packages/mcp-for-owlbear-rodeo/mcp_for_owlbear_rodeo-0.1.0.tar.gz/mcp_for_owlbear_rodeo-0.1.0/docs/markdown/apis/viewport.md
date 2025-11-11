# Viewport

## `OBR.viewport`

Control the viewport of the current scene.

The viewport represents this players view of the current scene.

# Reference

## Methods

### `reset`

``` prism-code
async reset()
```

Reset the viewport to the initial view.

If no map exists in the scene this will be the origin. If a map exists the viewport will fit to this map.

Returns a [ViewportTransform](#viewporttransform) with the transform it was reset to.

------------------------------------------------------------------------

### `animateTo`

``` prism-code
async animateTo(transform)
```

Animate the viewport to the given transform.

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:--:|
| transform | [ViewportTransform](#viewporttransform) | The new transform to animate to |

------------------------------------------------------------------------

### `animateToBounds`

``` prism-code
async animateTo(bounds)
```

Animate the viewport to the given bounding box.

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:--:|
| bounds | [BoundingBox](../reference/bounding-box.md) | The bounding box to animate to |

**Example**

Zoom on to the selected items when clicking a context menu item

``` prism-code
OBR.contextMenu.create({
  id: "rodeo.owlbear.example",
  icons: [
    {
      icon: "icon.svg",
      label: "Example",
    },
  ],
  async onClick(context) {
    OBR.viewport.animateToBounds(context.selectionBounds);
  },
});
```

------------------------------------------------------------------------

### `getPosition`

``` prism-code
async getPosition()
```

Get the current position of the viewport.

Returns a [Vector2](../reference/vector2.md).

------------------------------------------------------------------------

### `setPosition`

``` prism-code
async setPosition(position)
```

Set the position of the viewport.

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:--:|
| position | [Vector2](../reference/vector2.md) | The new position of the viewport |

------------------------------------------------------------------------

### `getScale`

``` prism-code
async getScale()
```

Get the current scale of the viewport.

A scale of 1 represents a 1:1 scale.

Returns a number.

------------------------------------------------------------------------

### `setScale`

``` prism-code
async setScale(scale)
```

Set the scale of the viewport.

**Parameters**

| NAME  |  TYPE  |          DESCRIPTION          |
|:-----:|:------:|:-----------------------------:|
| scale | number | The new scale of the viewport |

------------------------------------------------------------------------

### `getWidth`

``` prism-code
async getWidth()
```

Get the width of the viewport.

Returns a number.

------------------------------------------------------------------------

### `getHeight`

``` prism-code
async getHeight()
```

Get the height of the viewport.

Returns a number.

------------------------------------------------------------------------

### `transformPoint`

``` prism-code
async transformPoint(point)
```

Transform a point from the viewport coordinate space into the screens coordinate space.

**Parameters**

| NAME  |                TYPE                |      DESCRIPTION       |
|:-----:|:----------------------------------:|:----------------------:|
| point | [Vector2](../reference/vector2.md) | The point to transform |

Returns a [Vector2](../reference/vector2.md).

------------------------------------------------------------------------

### `inverseTransformPoint`

``` prism-code
async inverseTransformPoint(point)
```

Transform a point from the screens coordinate space into the viewport coordinate space.

**Parameters**

| NAME  |                TYPE                |      DESCRIPTION       |
|:-----:|:----------------------------------:|:----------------------:|
| point | [Vector2](../reference/vector2.md) | The point to transform |

Returns a [Vector2](../reference/vector2.md).

------------------------------------------------------------------------

## Type Definitions

### ViewportTransform

|  TYPE  |
|:------:|
| object |

**Properties**

|   NAME   |                TYPE                | DESCRIPTION                  |
|:--------:|:----------------------------------:|:-----------------------------|
| position | [Vector2](../reference/vector2.md) | The position of the viewport |
|  scale   |               number               | The scale of the viewport    |
