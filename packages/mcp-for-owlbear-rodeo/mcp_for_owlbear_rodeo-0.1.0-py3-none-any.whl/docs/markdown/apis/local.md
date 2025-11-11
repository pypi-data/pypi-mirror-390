# Local

## `OBR.scene.local`

An [Item](../reference/item.md) is the basic building block of everything shown in a Scene.

For all available items see [here](../reference/items.md).

This API is a mirror to the [Items](items.md) API but only interacts with local items.

A local item is a temporary item that will only be seen by the current user.

They are most useful for displaying feedback to the user such as showing a label when using a custom tool.

# Reference

## Methods

### `getItems`

``` prism-code
async getItems(filter)
```

Get then current local items in the scene.

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| filter | [ItemFilter](#itemfilter) | An optional filter to run on the scenes local items |

**Example**

Get local items with the given ids.

``` prism-code
const uuid = "55c04fba-9fa3-483b-8cf8-287737cbea9b";
const items = await OBR.scene.local.getItems([uuid]);
```

------------------------------------------------------------------------

### `updateItems`

``` prism-code
async updateItems(filterOrItems, update, fastUpdate)
```

Update existing local items in the scene.

To track changes and ensure immutability the update function uses an Immer `WritableDraft`.

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| filterOrItems | [ItemFilter](#itemfilter) \| [Item](../reference/item.md)\[\] | Either a filter or a list of local items to update |
| update | (draft: WritableDraft\<[Item](../reference/item.md)\[\]\>) =\> void | An update function that allows you to update an Immer `WritableDraft` of the input local items |
| fastUpdate | boolean | If true a faster update method will be used. Not all values can be updated using this method so check [here](interaction.md#interactive-values) to see if this will work. |

**Example**

Update the position of a known local item

``` prism-code
const uuid = "55c04fba-9fa3-483b-8cf8-287737cbea9b";

await OBR.scene.local.updateItems([uuid], (items) => {
  for (let item of items) {
    item.position.x += 100;
  }
});
```

------------------------------------------------------------------------

### `addItems`

``` prism-code
async addItems(items)
```

Add new local items to the scene.

To create new items you can use the item [Builders](../reference/builders.md).

**Parameters**

| NAME  |               TYPE               | DESCRIPTION            |
|:-----:|:--------------------------------:|:-----------------------|
| items | [Item](../reference/item.md)\[\] | A list of items to add |

**Example**

Add a label to the scene

``` prism-code
import OBR, { buildLabel } from "@owlbear-rodeo/sdk";

const item = buildLabel().plainText("Test").build();
OBR.scene.local.addItems([item]);
```

------------------------------------------------------------------------

### `deleteItems`

``` prism-code
async deleteItems(ids)
```

Delete existing items by their IDs.

**Parameters**

| NAME |    TYPE    | DESCRIPTION                            |
|:----:|:----------:|:---------------------------------------|
| ids  | string\[\] | A list of items to delete by their IDs |

**Example**

Delete a known local item

``` prism-code
const uuid = "55c04fba-9fa3-483b-8cf8-287737cbea9b";

OBR.scene.local.deleteItems([uuid]);
```

------------------------------------------------------------------------

### `getItemAttachments`

``` prism-code
async getItemAttachments(ids)
```

Get all items, attachments and sub-attachments for a set of item IDs.

**Parameters**

| NAME |    TYPE    | DESCRIPTION                             |
|:----:|:----------:|:----------------------------------------|
| ids  | string\[\] | A list of items to look up by their IDs |

Returns a list of [Items](../reference/item.md).

------------------------------------------------------------------------

### `getItemBounds`

``` prism-code
async getItemBounds(ids)
```

Get the axis-aligned bounding box for the given items.

**Parameters**

| NAME |    TYPE    | DESCRIPTION                             |
|:----:|:----------:|:----------------------------------------|
| ids  | string\[\] | A list of items to look up by their IDs |

Returns a [BoundingBox](../reference/bounding-box.md).

------------------------------------------------------------------------

### `onChange`

``` prism-code
onChange(callback);
```

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| callback | (items: [Item](../reference/item.md)\[\]) =\> void | A callback for when a local item changes. The items array will include all local items in the scene, not just those that changed. |

Returns a function that when called will unsubscribe from change events.

**Example**

``` prism-code
/**
 * Use an `onChange` event with a React `useEffect`.
 * `onChange` returns an unsubscribe event to make this easy.
 */
useEffect(
  () =>
    OBR.scene.local.onChange((items) => {
      // React to item changes
    }),
  []
);
```

------------------------------------------------------------------------

## Type Definitions

### ItemFilter

A filter to run on a list of items.

|   TYPE   |
|:--------:|
| function |

**Parameters**

| NAME |             TYPE             | DESCRIPTION                   |
|:----:|:----------------------------:|:------------------------------|
| item | [Item](../reference/item.md) | The item to run the filter on |

Returns a boolean. If true the item passes the filter and will be used. If false the item will be ignored.

------------------------------------------------------------------------
