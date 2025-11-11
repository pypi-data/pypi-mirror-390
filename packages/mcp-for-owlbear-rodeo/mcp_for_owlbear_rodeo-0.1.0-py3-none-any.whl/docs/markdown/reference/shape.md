# Shape

A circle, rectangle, triangle or hexagon

Extends [Item](item.md)

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| type | "SHAPE" | The type of item |
| width | number | The width of the shape |
| height | number | The height of the shape |
| shapeType | "RECTANGLE" \| "CIRCLE" \| "TRIANGLE" \| "HEXAGON" | The type of shape |
| style | [ShapeStyle](#shapestyle) | The style of the shape |

## Type Definitions

### ShapeStyle

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
