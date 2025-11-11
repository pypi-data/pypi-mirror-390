# Tool

## `OBR.tool`

Manage custom tools, tool modes and tool actions.

# Reference

## Methods

### `create`

``` prism-code
async create(tool)
```

Create a new tool.

**Parameters**

| NAME |      TYPE       |      DESCRIPTION       |
|:----:|:---------------:|:----------------------:|
| tool | [Tool](#tool-1) | The new tool to create |

------------------------------------------------------------------------

### `remove`

``` prism-code
async remove(id)
```

Remove an existing tool.

**Parameters**

| NAME |  TYPE  |         DESCRIPTION          |
|:----:|:------:|:----------------------------:|
|  id  | string | The ID of the tool to remove |

------------------------------------------------------------------------

### `getActiveTool`

``` prism-code
async getActiveTool()
```

Returns a string of the current active tool ID.

------------------------------------------------------------------------

### `onToolChange`

``` prism-code
onToolChange(callback);
```

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| callback | (id: string) =\> void | A callback for when the current tool changes |

Returns a function that when called will unsubscribe from change events.

------------------------------------------------------------------------

### `createAction`

``` prism-code
async createAction(action)
```

Create a new tool action.

**Parameters**

|  NAME  |           TYPE            |          DESCRIPTION          |
|:------:|:-------------------------:|:-----------------------------:|
| action | [ToolAction](#toolaction) | The new tool action to create |

------------------------------------------------------------------------

### `removeAction`

``` prism-code
async removeAction(id)
```

Remove an existing tool action.

**Parameters**

| NAME |  TYPE  |             DESCRIPTION             |
|:----:|:------:|:-----------------------------------:|
|  id  | string | The ID of the tool action to remove |

------------------------------------------------------------------------

### `createMode`

``` prism-code
async createMode(mode)
```

Create a new tool mode.

**Parameters**

| NAME |         TYPE          |         DESCRIPTION         |
|:----:|:---------------------:|:---------------------------:|
| mode | [ToolMode](#toolmode) | The new tool mode to create |

------------------------------------------------------------------------

### `removeMode`

``` prism-code
async removeMode(id)
```

Remove an existing tool mode.

**Parameters**

| NAME |  TYPE  |            DESCRIPTION            |
|:----:|:------:|:---------------------------------:|
|  id  | string | The ID of the tool mode to remove |

------------------------------------------------------------------------

### `activateMode`

``` prism-code
async activateMode(toolId, modeId)
```

Activate a specific mode for a given tool.

**Parameters**

|  NAME  |  TYPE  |             DESCRIPTION             |
|:------:|:------:|:-----------------------------------:|
| toolId | string |         The ID of the tool          |
| modeId | string | The ID of the tool mode to activate |

------------------------------------------------------------------------

### `getActiveToolMode`

``` prism-code
async getActiveToolMode()
```

Returns a string of the current active tool mode ID.

------------------------------------------------------------------------

### `onToolModeChange`

``` prism-code
onToolModeChange(callback);
```

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| callback | (id: string) =\> void | A callback for when the current tool mode changes |

Returns a function that when called will unsubscribe from change events.

------------------------------------------------------------------------

### `getMetadata`

``` prism-code
async getMetadata(id)
```

Get the metadata for the given tool.

**Parameters**

| NAME |  TYPE  |    DESCRIPTION     |
|:----:|:------:|:------------------:|
|  id  | string | The ID of the tool |

Returns a [Metadata](../reference/metadata.md) object.

------------------------------------------------------------------------

### `setMetadata`

``` prism-code
async setMetadata(toolId, update)
```

Update the metadata for a given tool.

**Example**

Update the stroke color of a custom drawing tool

``` prism-code
async function handleChange(value: string) {
  await OBR.tool.setMetadata("com.example.drawing", {
    strokeColor: value,
  });
}
```

This does not override any metadata properties that already exist. For example if the metadata looks like this:

``` prism-code
{
  strokeWidth: 1,
  strokeColor: "red"
}
```

And `handleChange("blue")` is called in the example above then the resulting metadata will look like this:

``` prism-code
{
  strokeWidth: 1,
  strokeColor: "blue"
}
```

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:--:|
| toolId | string | The ID of the tool |
| update | Partial\<[Metadata](../reference/metadata.md)\> | The metadata data update to use. The metadata is spread into the existing metadata. |

------------------------------------------------------------------------

## Type Definitions

### Tool

A tool in the toolbar.

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| id | string | The ID of this tool |
| icons | [ToolIcon](#toolicon)\[\] | The icons for this tool |
| disabled | [ToolFilter](#toolfilter) | An optional filter for checking if the tool should be disabled |
| onClick | (context: [ToolContext](#toolcontext), elementId: string) =\> void \| undefined \| boolean | An optional callback for when the tool icon is clicked. By default the clicked tool will be activated. If defined return true to perform the default click action. |
| shortcut | string | An optional key shortcut for this tool |
| defaultMode | string | An optional ID of the mode to be activated by default |
| defaultMetadata | [Metadata](../reference/metadata.md) | An optional Metadata object to use as default |

------------------------------------------------------------------------

### ToolAction

A tool action defines an item in the tool menu bar.

Unlike a tool mode an action is a clickable item but won't be activated when clicked.

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| id | string | The ID of this action |
| icons | [ToolIcon](#toolicon)\[\] | The icons for this action |
| disabled | [ToolFilter](#toolfilter) | An optional filter for checking if the action should be disabled |
| onClick | (context: [ToolContext](#toolcontext), elementId: string) =\> void | An optional callback for when the action icon is clicked |
| shortcut | string | An optional key shortcut for this action |

------------------------------------------------------------------------

### ToolMode

A tool mode will be activated when clicked.

Once a mode is active it will receive pointer events such as `onToolMove` and `onToolDragMove`.

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| id | string | The ID of this mode |
| icons | [ToolIcon](#toolicon)\[\] | The icons for this mode |
| disabled | [ToolFilter](#toolfilter) | An optional filter for checking if the mode should be disabled |
| onClick | (context: [ToolContext](#toolcontext), elementId: string) =\> void \| undefined \| boolean | An optional callback for when the mode icon is clicked. By default the clicked mode will be activated. If defined return true to perform the default click action. |
| shortcut | string | An optional key shortcut for this mode |
| cursors | [ToolCursor](#toolcursor)\[\] | An optional array of cursors |
| onToolClick | (context: [ToolContext](#toolcontext), event: [ToolEvent](#toolevent)) =\> void \| undefined \| boolean | An optional callback for when a single click is made by the tool. By default the clicked item will be selected if it is unlocked. If defined return true to perform the default click action. |
| onToolDoubleClick | (context: [ToolContext](#toolcontext), event: [ToolEvent](#toolevent)) =\> void \| undefined \| boolean | An optional callback for when a double click is made by the tool. By default the clicked item will be selected event if it is locked. If defined return true to perform the default double click action. |
| onToolDown | (context: [ToolContext](#toolcontext), event: [ToolEvent](#toolevent)) =\> void | An optional callback for when the pointer enters the down state |
| onToolMove | (context: [ToolContext](#toolcontext), event: [ToolEvent](#toolevent)) =\> void | An optional callback for when the pointer moves |
| onToolUp | (context: [ToolContext](#toolcontext), event: [ToolEvent](#toolevent)) =\> void | An optional callback for when the pointer enters the up state |
| onToolDragStart | (context: [ToolContext](#toolcontext), event: [ToolEvent](#toolevent)) =\> void | An optional callback for when a drag starts on the viewport |
| onToolDragMove | (context: [ToolContext](#toolcontext), event: [ToolEvent](#toolevent)) =\> void | An optional callback for when dragging on the viewport |
| onToolDragEnd | (context: [ToolContext](#toolcontext), event: [ToolEvent](#toolevent)) =\> void | An optional callback for when a drag ends on the viewport |
| onToolDragCancel | (context: [ToolContext](#toolcontext), event: [ToolEvent](#toolevent)) =\> void | An optional callback for when a drag event is canceled by either switching modes or pressing the Escape key |
| onActivate | (context: [ToolContext](#toolcontext)) | An optional callback for when the tool mode is activated |
| onDeactivate | (context: [ToolContext](#toolcontext) ) | An optional callback for when the tool mode is deactivated |
| onKeyDown | (context: [ToolContext](#toolcontext), event: [KeyEvent](#keyevent)) =\> void | An optional callback for when a key is pressed |
| onKeyUp | (context: [ToolContext](#toolcontext), event: [KeyEvent](#keyevent)) =\> void | An optional callback for when a key is released |
| preventDrag | [ToolModeFilter](#toolmodefilter) | An optional filter for checking if the drag event should be prevented. If the filter returns true the default drag operation will be used which mimics the Move tool. |

------------------------------------------------------------------------

### ToolContext

Holds the state of the tool.

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| activeTool | string | The ID of the current active tool |
| activeMode | string | An optional ID of the current active tool mode |
| metadata | [Metadata](../reference/metadata.md) | The metadata of the current active tool |

------------------------------------------------------------------------

### ToolEvent

A pointer event for a tool mode.

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| pointerPosition | [Vector2](../reference/vector2.md) | The pointer position relative to the viewport |
| target | [Item](../reference/item.md) | An optional target for the pointer event |
| transformer | boolean | If we have a target are we selecting a transformer control point |
| altKey | boolean | Is the Alt key pressed down |
| shiftKey | boolean | Is the Shift key pressed down |
| ctrlKey | boolean | Is the Ctrl key pressed down |
| metaKey | boolean | Is the Meta key pressed down |

------------------------------------------------------------------------

### KeyEvent

A key event for a tool mode.

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| code | string | A string representation of the physical key pressed |
| key | string | A string representation of the key |
| altKey | boolean | Is the Alt key pressed down |
| shiftKey | boolean | Is the Shift key pressed down |
| ctrlKey | boolean | Is the Ctrl key pressed down |
| metaKey | boolean | Is the Meta key pressed down |
| repeat | boolean | Is the key being held down such that it is automatically repeating |

------------------------------------------------------------------------

### ToolIcon

An icon for a tool.

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| icon | string | The url of the icon as either a relative or absolute path |
| label | string | The label to use for the tooltip of the icon |
| filter | [ToolFilter](#toolfilter) | An optional filter to control when this icon will be shown |

------------------------------------------------------------------------

### ToolFilter

A filter to control if various tools, actions or modes will be shown.

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| activeTools | string\[\] | An optional array of tool IDs that can be active |
| activeModes | string\[\] | An optional array of tool mode IDs that can be active |
| permissions | [Permission](../reference/permission.md)\[\] | An optional permissions filter |
| roles | ("GM" \| "PLAYER")\[\] | An optional array of roles needed for the player, defaults to no role needed |
| metadata | [KeyFilter](../reference/filters.md#keyfilter)\[\] | An optional array of filters to run on the current tool metadata |

------------------------------------------------------------------------

### ToolModeFilter

A filter to use for a tool mode.

Extends [ToolFilter](#toolfilter).

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| target | [KeyFilter](../reference/filters.md#keyfilter)\[\] | An optional array of filters to run on the current target of a tool mode |
| dragging | boolean | An optional boolean to check the dragging state of the current tool mode |

------------------------------------------------------------------------

### ToolCursor

A cursor to use for a tool mode.

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| cursor | string | A css cursor string e.g. "pointer" |
| filter | [ToolModeFilter](#toolmodefilter) | An optional filter to run on the current tool mode |

------------------------------------------------------------------------
