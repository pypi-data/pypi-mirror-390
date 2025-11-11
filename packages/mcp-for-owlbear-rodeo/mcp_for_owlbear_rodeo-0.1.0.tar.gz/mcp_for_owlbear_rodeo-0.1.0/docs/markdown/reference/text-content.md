# TextContent

Describes all information needed to display text.

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| richText | [RichText](#richtext) | The text formatted as a set of nodes. Used when the "RICH" type is set |
| plainText | string | The text without any formatting. Used when the "PLAIN" type is set. |
| type | "PLAIN" \| "RICH" | Does this text support rich text formatting like headings. If "PLAIN" a faster text rendering path will be used. |
| style | [TextStyle](#textstyle) | The style of the text |
| width | [TextSize](#textsize) | The width of this text content |
| height | [TextSize](#textsize) | The height of this text content |

## Type Definitions

### RichText

An array of text [descendents](#descendent).

**Examples**

A single paragraph with the text `Owlbear Rodeo`

``` prism-code
[
  {
    "type": "paragraph",
    "children": [{ "text": "Owlbear Rodeo" }]
  }
]
```

A heading, subhead and paragraph.

``` prism-code
[
  {
    "type": "heading-one",
    "children": [
      {
        "text": "Heading"
      }
    ]
  },
  {
    "type": "heading-two",
    "children": [
      {
        "text": "Subhead"
      }
    ]
  },
  {
    "type": "paragraph",
    "children": [
      {
        "text": "Paragraph"
      }
    ]
  }
]
```

A paragraph with regular, bold and italics.

``` prism-code
{
  "type": "paragraph",
  "children": [
    {
      "text": "Regular "
    },
    {
      "text": "Bold",
      "bold": true
    },
    {
      "text": " "
    },
    {
      "text": "Italics",
      "italic": true
    }
  ]
}
```

A bulleted list with a bold item.

``` prism-code
[
  {
    "type": "bulleted-list",
    "children": [
      {
        "type": "list-item",
        "children": [
          {
            "text": "List 1"
          }
        ]
      },
      {
        "type": "list-item",
        "children": [
          {
            "text": "List 2",
            "bold": true
          }
        ]
      },
      {
        "type": "list-item",
        "children": [
          {
            "text": "List 3"
          }
        ]
      }
    ]
  }
]
```

|             TYPE              |
|:-----------------------------:|
| [Descendent](#descendent)\[\] |

### Descendent

An array of [elements](#element) or [text](#text) blocks.

|         TYPE          |
|:---------------------:|
| (Element \| Text)\[\] |

### Element

| TYPE |
|:--:|
| [BulletedListElement](#bulletedlistelement) \| [NumberedListElement](#numberedlistelement) \| [HeadingOneElement](#headingoneelement) \| [HeadingTwoElement](#headingtwoelement) \| [ListItemElement](#listitemelement) \| [ParagraphElement](#paragraphelement) |

### Text

|  TYPE  |
|:------:|
| object |

**Properties**

|  NAME  |  TYPE   | DESCRIPTION                                         |
|:------:|:-------:|:----------------------------------------------------|
|  text  | string  | The text to display                                 |
| italic | boolean | An optional boolean to enable italics for this text |
|  bold  | boolean | An optional boolean to enable bold for this text    |

### TextStyle

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| fillColor | string | The fill color of the text |
| fillOpacity | number | The fill opacity of the text between 0 and 1 |
| strokeColor | string | The stroke color of the text |
| strokeOpacity | number | The stroke opacity of the text between 0 and 1 |
| strokeWidth | number | The stroke width of the text in pixels |
| textAlign | "LEFT" \| "CENTER" \| "RIGHT" | The horizontal alignment of the text |
| textAlignVertical | "BOTTOM" \| "MIDDLE" \| "TOP" | The vertical alignment of the text |
| fontFamily | string | The font for the text |
| fontSize | number | The size of the text in pixels |
| fontWeight | number | The weight of the text |
| lineHeight | number | The line height of the text relative to the font size |
| padding | number | The padding for the text in pixels |

### TextSize

The size of a text block either in pixels or the string `"AUTO"` for automatic sizing based on the content.

|       TYPE       |
|:----------------:|
| number \| "AUTO" |

## Text Elements

### BulletedListElement

Equivalent to the `<ul>` HTML element.

|  TYPE  |
|:------:|
| object |

**Properties**

|   NAME   |             TYPE              | DESCRIPTION                   |
|:--------:|:-----------------------------:|:------------------------------|
|   type   |        "bulleted-list"        | The type of this element      |
| children | [Descendent](#descendent)\[\] | The children for this element |

### NumberedListElement

Equivalent to the `<ol>` HTML element.

|  TYPE  |
|:------:|
| object |

**Properties**

|   NAME   |             TYPE              | DESCRIPTION                   |
|:--------:|:-----------------------------:|:------------------------------|
|   type   |        "numbered-list"        | The type of this element      |
| children | [Descendent](#descendent)\[\] | The children for this element |

### HeadingOneElement

Equivalent to the `<h1>` HTML element.

|  TYPE  |
|:------:|
| object |

**Properties**

|   NAME   |             TYPE              | DESCRIPTION                   |
|:--------:|:-----------------------------:|:------------------------------|
|   type   |         "heading-one"         | The type of this element      |
| children | [Descendent](#descendent)\[\] | The children for this element |

### HeadingTwoElement

Equivalent to the `<h2>` HTML element.

|  TYPE  |
|:------:|
| object |

**Properties**

|   NAME   |             TYPE              | DESCRIPTION                   |
|:--------:|:-----------------------------:|:------------------------------|
|   type   |         "heading-two"         | The type of this element      |
| children | [Descendent](#descendent)\[\] | The children for this element |

### ListItemElement

Equivalent to the `<li>` HTML element.

|  TYPE  |
|:------:|
| object |

**Properties**

|   NAME   |             TYPE              | DESCRIPTION                   |
|:--------:|:-----------------------------:|:------------------------------|
|   type   |          "list-item"          | The type of this element      |
| children | [Descendent](#descendent)\[\] | The children for this element |

### ParagraphElement

Equivalent to the `<p>` HTML element.

|  TYPE  |
|:------:|
| object |

**Properties**

|   NAME   |             TYPE              | DESCRIPTION                   |
|:--------:|:-----------------------------:|:------------------------------|
|   type   |          "paragraph"          | The type of this element      |
| children | [Descendent](#descendent)\[\] | The children for this element |
