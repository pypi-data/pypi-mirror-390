# Ruler

A straight line ruler

Extends [Item](item.md)

|  TYPE  |
|:------:|
| object |

**Properties**

|     NAME      |           TYPE            | DESCRIPTION                       |
|:-------------:|:-------------------------:|:----------------------------------|
|     type      |          "RULER"          | The type of item                  |
| startPosition |   [Vector2](vector2.md)   | The start position of the ruler   |
|  endPosition  |   [Vector2](vector2.md)   | The end position of the ruler     |
|  measurement  |          string           | The value to display on the ruler |
|     style     | [RulerStyle](#rulerstyle) | The style of the ruler            |

## Type Definitions

### RulerStyle

|  TYPE  |
|:------:|
| object |

**Properties**

|  NAME   |         TYPE         | DESCRIPTION                              |
|:-------:|:--------------------:|:-----------------------------------------|
| variant | "FILLED" \| "DASHED" | The visual style of the ruler background |
