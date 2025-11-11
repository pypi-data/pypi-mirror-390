# MathM

Math class for a 2D transformation [Matrix](matrix.md).

## Examples

### Find the relative transform between two items

``` prism-code
const a = buildShape().build();
const b = buildShape().build();

const aTransform = MathM.fromItem(a);
const bTransform = MathM.fromItem(b);

const invATransform = MathM.inverse(aTransform);
const relativeBTransform = MathM.multiply(invATransform, bTransform);
```

### Find the world position of a line's `startPosition`

``` prism-code
const line = buildLine().build();

const lineTransform = MathM.fromItem(line);
const startTransform = MathM.fromPosition(line.startPosition);

const worldTransform = MathM.multiply(lineTransform, startTransform);

const worldPosition = MathM.decompose(worldTransform).position;
```

# Reference

## Methods

### `inverse`

``` prism-code
inverse(matrix);
```

Returns the inverse of the given `matrix`

**Parameters**

|  NAME  |        TYPE         |
|:------:|:-------------------:|
| matrix | [Matrix](matrix.md) |

------------------------------------------------------------------------

### `multiply`

``` prism-code
multiply(a, b);
```

Returns `a` multiplied by `b`

**Parameters**

| NAME |        TYPE         |
|:----:|:-------------------:|
|  a   | [Matrix](matrix.md) |
|  b   | [Matrix](matrix.md) |

------------------------------------------------------------------------

### `fromPosition`

``` prism-code
fromPosition(position);
```

Create a new transformation matrix from a position

Returns a [Matrix](matrix.md)

**Parameters**

|   NAME   |         TYPE          |
|:--------:|:---------------------:|
| position | [Vector2](vector2.md) |

------------------------------------------------------------------------

### `fromRotation`

``` prism-code
fromRotation(rotation);
```

Create a new transformation matrix from a rotation

Returns a [Matrix](matrix.md)

**Parameters**

|   NAME   |  TYPE  | DESCRIPTION         |
|:--------:|:------:|:--------------------|
| rotation | number | Rotation in degrees |

------------------------------------------------------------------------

### `fromScale`

``` prism-code
fromScale(scale);
```

Create a new transformation matrix from a scale

Returns a [Matrix](matrix.md)

**Parameters**

| NAME  |         TYPE          |
|:-----:|:---------------------:|
| scale | [Vector2](vector2.md) |

------------------------------------------------------------------------

### `fromItem`

``` prism-code
fromItem(item);
```

Create a new transformation matrix from a [Item](item.md)

Returns a [Matrix](matrix.md)

**Parameters**

| NAME |      TYPE       |
|:----:|:---------------:|
| item | [Item](item.md) |

------------------------------------------------------------------------

### `decompose`

``` prism-code
decompose(matrix);
```

Decompose a matrix into its individual parts

Returns the position, scale and rotation (in degrees) of the matrix

**Parameters**

|  NAME  |        TYPE         |
|:------:|:-------------------:|
| matrix | [Matrix](matrix.md) |

------------------------------------------------------------------------
