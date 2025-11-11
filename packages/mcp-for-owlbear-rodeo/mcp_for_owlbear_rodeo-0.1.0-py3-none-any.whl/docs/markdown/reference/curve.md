# Curve

A shape with a list of 2D points

Extends [Item](item.md)

|  TYPE  |
|:------:|
| object |

**Properties**

|  NAME  |           TYPE            | DESCRIPTION                |
|:------:|:-------------------------:|:---------------------------|
|  type  |          "CURVE"          | The type of item           |
| points | [Vector2](vector2.md)\[\] | The list of points to draw |
| style  | [CurveStyle](#curvestyle) | The style of the curve     |

## Type Definitions

### CurveStyle

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| fillColor | string | The fill color of the shape |
| fillOpacity | number | The fill opacity of the shape between 0 and 1 |
| strokeColor | string | The stroke color of the shape |
| strokeOpacity | number | The stroke opacity of the shape between 0 and 1 |
| strokeWidth | number | The stroke width of the shape in pixels |
| strokeDash | number\[\] | The pattern of the stroke dash |
| tension | number | How much curvature to apply between points in the curve. A value of 0 will make a straight edge shape. A value of 1 will cause a large curve. |
| closed | boolean | An optional boolean when true the curve ends where it started |
