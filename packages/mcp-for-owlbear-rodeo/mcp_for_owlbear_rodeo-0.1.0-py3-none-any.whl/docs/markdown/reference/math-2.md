# Math2

Math class for [Vector2](vector2.md)'s.

## Example

### Add two [Vector2](vector2.md)'s

``` prism-code
const a: Vector2 = { x: 100, y: 100 };
const b: Vector2 = { x: 50, y: 50 };
const c = Math2.add(a, b);
```

# Reference

## Methods

### `magnitudeSquared`

``` prism-code
magnitudeSquared(p);
```

Returns the squared length of vector `p`

**Parameters**

| NAME |         TYPE          |
|:----:|:---------------------:|
|  p   | [Vector2](vector2.md) |

------------------------------------------------------------------------

### `magnitude`

``` prism-code
magnitude(p);
```

Returns the length of vector `p`

**Parameters**

| NAME |         TYPE          |
|:----:|:---------------------:|
|  p   | [Vector2](vector2.md) |

------------------------------------------------------------------------

### `normalize`

``` prism-code
normalize(p);
```

Returns `p` normalized, if length of `p` is 0 `{x: 0, y: 0}` is returned

**Parameters**

| NAME |         TYPE          |
|:----:|:---------------------:|
|  p   | [Vector2](vector2.md) |

------------------------------------------------------------------------

### `dot`

``` prism-code
dot(a, b);
```

Returns the dot product between `a` and `b`

**Parameters**

| NAME |         TYPE          |
|:----:|:---------------------:|
|  a   | [Vector2](vector2.md) |
|  b   | [Vector2](vector2.md) |

------------------------------------------------------------------------

### `subtract`

``` prism-code
subtract(a, b);
```

Returns `a` minus `b`

**Parameters**

| NAME |              TYPE               |
|:----:|:-------------------------------:|
|  a   |      [Vector2](vector2.md)      |
|  b   | [Vector2](vector2.md) \| number |

------------------------------------------------------------------------

### `add`

``` prism-code
add(a, b);
```

Returns `a` plus `b`

**Parameters**

| NAME |              TYPE               |
|:----:|:-------------------------------:|
|  a   |      [Vector2](vector2.md)      |
|  b   | [Vector2](vector2.md) \| number |

------------------------------------------------------------------------

### `multiply`

``` prism-code
multiply(a, b);
```

Returns `a` multiplied by `b`

**Parameters**

| NAME |              TYPE               |
|:----:|:-------------------------------:|
|  a   |      [Vector2](vector2.md)      |
|  b   | [Vector2](vector2.md) \| number |

------------------------------------------------------------------------

### `divide`

``` prism-code
divide(a, b);
```

Returns `a` divided by `b`

**Parameters**

| NAME |              TYPE               |
|:----:|:-------------------------------:|
|  a   |      [Vector2](vector2.md)      |
|  b   | [Vector2](vector2.md) \| number |

------------------------------------------------------------------------

### `rotate`

``` prism-code
rotate(point, origin, angle);
```

Rotates a point around a given origin by an angle in degrees

Returns the rotated point

**Parameters**

|  NAME  |         TYPE          | DESCRIPTION                  |
|:------:|:---------------------:|:-----------------------------|
| point  | [Vector2](vector2.md) | Point to rotate              |
| origin | [Vector2](vector2.md) | Origin of the rotation       |
| angle  |        number         | Angle of rotation in degrees |

------------------------------------------------------------------------

### `min`

``` prism-code
min(a, b);
```

Returns the min of `a` and `b` as a Vector

**Parameters**

| NAME |              TYPE               |
|:----:|:-------------------------------:|
|  a   |      [Vector2](vector2.md)      |
|  b   | [Vector2](vector2.md) \| number |

------------------------------------------------------------------------

### `componentMin`

``` prism-code
min(a);
```

Returns the component wise minimum of `a`

**Parameters**

| NAME |         TYPE          |
|:----:|:---------------------:|
|  a   | [Vector2](vector2.md) |

------------------------------------------------------------------------

### `max`

``` prism-code
max(a, b);
```

Returns the max of `a` and `b` as a Vector

**Parameters**

| NAME |              TYPE               |
|:----:|:-------------------------------:|
|  a   |      [Vector2](vector2.md)      |
|  b   | [Vector2](vector2.md) \| number |

------------------------------------------------------------------------

### `componentMax`

``` prism-code
max(a);
```

Returns the component wise maximum of `a`

**Parameters**

| NAME |         TYPE          |
|:----:|:---------------------:|
|  a   | [Vector2](vector2.md) |

------------------------------------------------------------------------

### `roundTo`

``` prism-code
roundTo(p, to);
```

Rounds `p` to the nearest value of `to`

Returns the rounded vector

**Parameters**

| NAME |         TYPE          |
|:----:|:---------------------:|
|  p   | [Vector2](vector2.md) |
|  to  | [Vector2](vector2.md) |

------------------------------------------------------------------------

### `floorTo`

``` prism-code
floorTo(p, to);
```

Floors `p` to the nearest value of `to`

Returns the floored vector

**Parameters**

| NAME |         TYPE          |
|:----:|:---------------------:|
|  p   | [Vector2](vector2.md) |
|  to  | [Vector2](vector2.md) |

------------------------------------------------------------------------

### `sign`

``` prism-code
sign(a);
```

Returns the component wise sign of `a`

**Parameters**

| NAME |         TYPE          |
|:----:|:---------------------:|
|  a   | [Vector2](vector2.md) |

------------------------------------------------------------------------

### `abs`

``` prism-code
abs(a);
```

Returns the component wise absolute of `a`

**Parameters**

| NAME |         TYPE          |
|:----:|:---------------------:|
|  a   | [Vector2](vector2.md) |

------------------------------------------------------------------------

### `pow`

``` prism-code
pow(a, b);
```

Returns `a` to the power of `b`

**Parameters**

| NAME |              TYPE               |
|:----:|:-------------------------------:|
|  a   |      [Vector2](vector2.md)      |
|  b   | [Vector2](vector2.md) \| number |

------------------------------------------------------------------------

### `clamp`

``` prism-code
clamp(a, min max)
```

Returns `a` clamped between `min` and `max`

**Parameters**

| NAME |         TYPE          |
|:----:|:---------------------:|
|  a   | [Vector2](vector2.md) |
| min  |        number         |
| max  |        number         |

------------------------------------------------------------------------

### `boundingBox`

``` prism-code
boundingBox(points);
```

Returns an axis-aligned [BoundingBox](bounding-box.md) around an array of points

**Parameters**

|  NAME  |           TYPE            |
|:------:|:-------------------------:|
| points | [Vector2](vector2.md)\[\] |

------------------------------------------------------------------------

### `pointInPolygon`

``` prism-code
pointInPolygon(p, points);
```

Checks to see if a point is in a polygon

Returns true if the given point `p` is inside the polygon made by `points`

**Parameters**

|  NAME  |           TYPE            |
|:------:|:-------------------------:|
|   p    |   [Vector2](vector2.md)   |
| points | [Vector2](vector2.md)\[\] |

------------------------------------------------------------------------

### `compare`

``` prism-code
compare(a, b, threshold);
```

Returns true if the the distance between `a` and `b` is under `threshold`

**Parameters**

|   NAME    |         TYPE          |
|:---------:|:---------------------:|
|     a     | [Vector2](vector2.md) |
|     b     | [Vector2](vector2.md) |
| threshold |        number         |

------------------------------------------------------------------------

### `distance`

``` prism-code
distance(a, b);
```

Returns the euclidean distance between `a` and `b`

**Parameters**

| NAME |         TYPE          |
|:----:|:---------------------:|
|  a   | [Vector2](vector2.md) |
|  b   | [Vector2](vector2.md) |

------------------------------------------------------------------------

### `lerp`

``` prism-code
lerp(a, b, alpha);
```

Returns the linear interpolation between `a` and `b` by `alpha`

**Parameters**

| NAME  |         TYPE          |
|:-----:|:---------------------:|
|   a   | [Vector2](vector2.md) |
|   b   | [Vector2](vector2.md) |
| alpha |        number         |

------------------------------------------------------------------------

### `centroid`

``` prism-code
centroid(points);
```

Returns the centroid of the given points

**Parameters**

|  NAME  |           TYPE            |
|:------:|:-------------------------:|
| points | [Vector2](vector2.md)\[\] |

------------------------------------------------------------------------
