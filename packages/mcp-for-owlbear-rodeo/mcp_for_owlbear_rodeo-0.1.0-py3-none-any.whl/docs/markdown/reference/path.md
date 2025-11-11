# Path

A raw path defined with a list of drawing commands

If you just want to draw a freeform shape see the simpler [Curve](curve.md) item

Extends [Item](item.md)

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| type | "PATH" | The type of item |
| commands | [PathCommand](#pathcommand)\[\] | The list of drawing commands |
| style | [PathStyle](#pathstyle) | The style of the path |
| fillRule | string | Either "nonzero" or "evenodd" |

## Type Definitions

### PathStyle

|  TYPE  |
|:------:|
| object |

**Properties**

|     NAME      |    TYPE    | DESCRIPTION                                     |
|:-------------:|:----------:|:------------------------------------------------|
|   fillColor   |   string   | The fill color of the shape                     |
|  fillOpacity  |   number   | The fill opacity of the shape between 0 and 1   |
|  strokeColor  |   string   | The stroke color of the shape                   |
| strokeOpacity |   number   | The stroke opacity of the shape between 0 and 1 |
|  strokeWidth  |   number   | The stroke width of the shape in pixels         |
|  strokeDash   | number\[\] | The pattern of the stroke dash                  |

### PathCommand

| TYPE |
|:--:|
| [MoveCommand](#movecommand) \| [LineCommand](#linecommand) \| [QuadCommand](#quadcommand) \| [ConicCommand](#coniccommand) \| [CubicCommand](#cubiccommand) \| [CloseCommand](#closecommand) |

### Command

| TYPE | values                                |
|:----:|:--------------------------------------|
| Enum | MOVE, LINE, QUAD, CONIC, CUBIC, CLOSE |

## Commands

### MoveCommand

Begins a new sub-path at the given `(x, y)`.

Reference.

|    TYPE    | values                             |
|:----------:|:-----------------------------------|
| number\[\] | \[[Command.Move](#command), x, y\] |

### LineCommand

Draw a line from the last point to the given `(x, y)`.

Reference.

|    TYPE    | values                             |
|:----------:|:-----------------------------------|
| number\[\] | \[[Command.Line](#command), x, y\] |

### QuadCommand

Draw a quadratic curve from the last point to `(x2, y2)` with the control point `(x1, y1)`.

Reference.

|    TYPE    | values                                       |
|:----------:|:---------------------------------------------|
| number\[\] | \[[Command.Quad](#command), x1, y1, x2, y2\] |

### ConicCommand

Draw a conic from the last point to `(x2, y2)` with the control point `(x1, y1)` and the weight `w`.

Reference.

|    TYPE    | values                                           |
|:----------:|:-------------------------------------------------|
| number\[\] | \[[Command.Conic](#command), x1, y1, x2, y2, w\] |

### CubicCommand

Draw a cubic from the last point to `(x3, y3)` with the control points `(x1, y1)` and `(x2, y2)`.

Reference.

|    TYPE    | values                                                |
|:----------:|:------------------------------------------------------|
| number\[\] | \[[Command.Cubic](#command), x1, y1, x2, y2, x3, y3\] |

### CloseCommand

Close the current sub-path.

Reference.

|    TYPE    | values                        |
|:----------:|:------------------------------|
| number\[\] | \[[Command.Close](#command)\] |
