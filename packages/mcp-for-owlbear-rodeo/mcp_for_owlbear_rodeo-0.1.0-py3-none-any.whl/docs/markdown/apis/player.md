# Player

## `OBR.player`

The player API gives you access to the current player using Owlbear Rodeo.

# Reference

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| id | string | The user ID for this player. This will be shared if the same player joins a room multiple times |

------------------------------------------------------------------------

## Methods

### `getSelection`

``` prism-code
async getSelection()
```

Get the current selection for this player.

Returns an array of [Item](../reference/item.md) IDs or undefined if the player has no current selection.

------------------------------------------------------------------------

### `select`

``` prism-code
async select(items, replace?)
```

Select items for the player.

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| items | string\[\] | An array of item IDs to select |
| replace | boolean | An optional boolean, if true the users selection will be replaced, if false the selection will be combined with their current selection |

------------------------------------------------------------------------

### `deselect`

``` prism-code
async deselect(items)
```

Deselect a set of items or all items.

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| items | string\[\] | An optional array if item IDs to deselect, if undefined all items will be deselected |

------------------------------------------------------------------------

### `getName`

``` prism-code
async getName()
```

Get the name for this player.

Returns a string.

------------------------------------------------------------------------

### `setName`

``` prism-code
async setName(name)
```

**Parameters**

| NAME |  TYPE  | DESCRIPTION                  |
|:----:|:------:|:-----------------------------|
| name | string | The new name for this player |

------------------------------------------------------------------------

### `getColor`

``` prism-code
async getColor()
```

Get the color for this player.

Returns a string.

------------------------------------------------------------------------

### `setColor`

``` prism-code
async setColor(color)
```

**Parameters**

| NAME  |  TYPE  | DESCRIPTION                   |
|:-----:|:------:|:------------------------------|
| color | string | The new color for this player |

------------------------------------------------------------------------

### `getSyncView`

``` prism-code
async getSyncView()
```

Get whether this player currently has sync view enabled

Returns a boolean.

------------------------------------------------------------------------

### `setSyncView`

``` prism-code
async setSyncView(syncView)
```

**Parameters**

|   NAME   |  TYPE   | DESCRIPTION                             |
|:--------:|:-------:|:----------------------------------------|
| syncView | boolean | The new sync view state for this player |

------------------------------------------------------------------------

### `getId`

``` prism-code
async getId()
```

Get the user ID for this player. In most cases the `id` property should be used instead as it is synchronous.

This will be shared if the same player joins a room multiple times.

Returns a string.

------------------------------------------------------------------------

### `getRole`

``` prism-code
async getRole()
```

Get the current role for this player.

returns `"GM" | "PLAYER"`.

------------------------------------------------------------------------

### `getMetadata`

``` prism-code
async getMetadata()
```

Get the current metadata for this player.

returns a [Metadata](../reference/metadata.md) object.

------------------------------------------------------------------------

### `setMetadata`

``` prism-code
async setMetadata(update)
```

Update the metadata for this player.

See [Metadata](../reference/metadata.md) for best practices when updating metadata.

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| update | Partial\<[Metadata](../reference/metadata.md)\> | A partial update to this players metadata. The included values will be spread among the current metadata to avoid overriding other values. |

------------------------------------------------------------------------

### `hasPermission`

``` prism-code
async hasPermission(permission)
```

Does this player have the given permission.

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| permission | [Permission](../reference/permission.md) | The permission to check |

Returns a boolean.

------------------------------------------------------------------------

### `getConnectionId`

``` prism-code
async getConnectionId()
```

Get the current connection ID for this player.

This will be unique if the same player joins the room multiple times.

Returns a string.

------------------------------------------------------------------------

### `onChange`

``` prism-code
onChange(callback);
```

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| callback | (player: [Player](../reference/player.md)) =\> void | A callback for when a value on the current player changes |

Returns a function that when called will unsubscribe from change events.

**Example**

``` prism-code
/**
 * Use an `onChange` event with a React `useEffect`.
 * `onChange` returns an unsubscribe event to make this easy.
 */
useEffect(
  () =>
    OBR.player.onChange((player) => {
      // React to player changes
    }),
  []
);
```

------------------------------------------------------------------------
