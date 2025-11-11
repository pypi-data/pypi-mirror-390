# Action

## `OBR.action`

An extensions action is shown in the top left of a room.

When an action is clicked a popover will be shown for that action.

The action is defined in the extensions [Manifest](../reference/manifest.md) file.

# Reference

## Methods

### `getWidth`

``` prism-code
async getWidth()
```

Get the action popovers width.

Returns a number or undefined.

------------------------------------------------------------------------

### `setWidth`

``` prism-code
async setWidth(width)
```

Set the action popovers width.

**Parameters**

| NAME  |  TYPE  | DESCRIPTION                  |
|:-----:|:------:|:-----------------------------|
| width | number | The new width of the popover |

------------------------------------------------------------------------

### `getHeight`

``` prism-code
async getHeight()
```

Get the action popovers height.

Returns a number or undefined.

------------------------------------------------------------------------

### `setHeight`

``` prism-code
async setHeight(height)
```

Set the action popovers height.

**Parameters**

|  NAME  |  TYPE  | DESCRIPTION                   |
|:------:|:------:|:------------------------------|
| height | number | The new height of the popover |

------------------------------------------------------------------------

### `getBadgeText`

``` prism-code
async getBadgeText()
```

Get the actions badge text.

Returns a string or undefined.

------------------------------------------------------------------------

### `setBadgeText`

``` prism-code
async setBadgeText(badgeText)
```

Set the actions badge text.

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| badgeText | string | The new badge text of the action. Set as `undefined` to remove the badge |

------------------------------------------------------------------------

### `getBadgeBackgroundColor`

``` prism-code
async getBadgeBackgroundColor()
```

Get the actions badge background color.

Returns a string or undefined.

------------------------------------------------------------------------

### `setBadgeBackgroundColor`

``` prism-code
async setBadgeBackgroundColor(badgeBackgroundColor)
```

Set the actions badge background color.

**Parameters**

|         NAME         |  TYPE  | DESCRIPTION                                  |
|:--------------------:|:------:|:---------------------------------------------|
| badgeBackgroundColor | string | The new badge background color of the action |

------------------------------------------------------------------------

### `getIcon`

``` prism-code
async getIcon()
```

Get the actions icon.

Returns a string.

------------------------------------------------------------------------

### `setIcon`

``` prism-code
async setIcon(icon)
```

Set the actions icon.

**Parameters**

| NAME |  TYPE  | DESCRIPTION                |
|:----:|:------:|:---------------------------|
| icon | string | The new icon of the action |

------------------------------------------------------------------------

### `getTitle`

``` prism-code
async getTitle()
```

Get the actions title.

Returns a string.

------------------------------------------------------------------------

### `setTitle`

``` prism-code
async setTitle(title)
```

Set the actions title.

**Parameters**

| NAME  |  TYPE  | DESCRIPTION                 |
|:-----:|:------:|:----------------------------|
| title | string | The new title of the action |

------------------------------------------------------------------------

### `open`

``` prism-code
async open()
```

Open the action.

------------------------------------------------------------------------

### `close`

``` prism-code
async close()
```

Close the action.

------------------------------------------------------------------------

### `isOpen`

``` prism-code
async isOpen()
```

Returns true if the action is open

------------------------------------------------------------------------

### `onOpenChange`

``` prism-code
onOpenChange(callback);
```

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| callback | (isOpen: boolean) =\> void | A callback for when the action is opened or closed |

Returns a function that when called will unsubscribe from change events.

**Example**

``` prism-code
/**
 * Use an `onOpenChange` event with a React `useEffect`.
 * `onOpenChange` returns an unsubscribe event to make this easy.
 */
useEffect(
  () =>
    OBR.action.onOpenChange((isOpen) => {
      // React to the action opening or closing
    }),
  []
);
```

------------------------------------------------------------------------
