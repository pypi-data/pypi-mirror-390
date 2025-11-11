# Line

A straight line between two points

Extends [Item](item.md)

|  TYPE  |
|:------:|
| object |

**Properties**

|     NAME      |          TYPE           | DESCRIPTION                    |
|:-------------:|:-----------------------:|:-------------------------------|
|     type      |         "LINE"          | The type of item               |
| startPosition |  [Vector2](vector2.md)  | The start position of the line |
|  endPosition  |  [Vector2](vector2.md)  | The end position of the line   |
|     style     | [LineStyle](#linestyle) | The style of the curve         |

## Type Definitions

### LineStyle

|  TYPE  |
|:------:|
| object |

**Properties**

|     NAME      |    TYPE    | DESCRIPTION                                    |
|:-------------:|:----------:|:-----------------------------------------------|
|  strokeColor  |   string   | The stroke color of the line                   |
| strokeOpacity |   number   | The stroke opacity of the line between 0 and 1 |
|  strokeWidth  |   number   | The stroke width of the line in pixels         |
|  strokeDash   | number\[\] | The pattern of the line dash                   |
