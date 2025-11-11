# Items

## `OBR.scene.items`

An [Item](../reference/item.md) is the basic building block of everything shown in a Scene.

For all available items see [here](../reference/items.md).

# Reference

## Methods

### `getItems`

``` prism-code
async getItems(filter)
```

Get then current items in the scene.

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| filter | [ItemFilter](#itemfilter) | An optional filter to run on the scenes items |

**Example**

Get items with the given ids.

``` prism-code
const uuid = "55c04fba-9fa3-483b-8cf8-287737cbea9b";
const items = await OBR.scene.items.getItems([uuid]);
```

Get all images.

``` prism-code
import { isImage } from "@owlbear-rodeo/sdk";

const images = await OBR.scene.items.getItems(isImage);
```

Get all images on the Character layer

``` prism-code
import { isImage } from "@owlbear-rodeo/sdk";

const characters = await OBR.scene.items.getItems(
  (item) => item.layer === "CHARACTER" && isImage(item)
);
```

Get all images on the Character layer using Typescript

``` prism-code
import { Image, isImage } from "@owlbear-rodeo/sdk";

const characters = await OBR.scene.items.getItems(
  (item): item is Image => item.layer === "CHARACTER" && isImage(item)
);
```

------------------------------------------------------------------------

### `updateItems`

``` prism-code
async updateItems(filterOrItems, update)
```

Update existing items in the scene.

To track changes and ensure immutability the update function uses an Immer `WritableDraft`.

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| filterOrItems | [ItemFilter](#itemfilter) \| [Item](../reference/item.md)\[\] | Either a filter or a list of items to update |
| update | (draft: WritableDraft\<[Item](../reference/item.md)\[\]\>) =\> void | An update function that allows you to update an Immer `WritableDraft` of the input items |

**Example**

Lock all images

``` prism-code
import { isImage } from "@owlbear-rodeo/sdk";

await OBR.scene.items.updateItems(isImage, (images) => {
  for (let image of images) {
    image.locked = true;
  }
});
```

Turn all shapes pink

``` prism-code
import { isShape } from "@owlbear-rodeo/sdk";

await OBR.scene.items.updateItems(isShape, (shapes) => {
  for (let shape of shapes) {
    shape.style.fillColor = "pink";
  }
});
```

Hide all attachments

``` prism-code
OBR.scene.items.updateItems(
  (item) => item.layer === "ATTACHMENT",
  (items) => {
    for (let item of items) {
      item.visible = false;
    }
  }
);
```

Hide selected items when clicking a context menu item

``` prism-code
OBR.contextMenu.create({
  id: "rodeo.owlbear.example",
  icons: [
    {
      icon: "icon.svg",
      label: "Example",
    },
  ],
  onClick(context) {
    OBR.scene.items.updateItems(context.items, (items) => {
      for (let item of items) {
        item.visible = false;
      }
    });
  },
});
```

------------------------------------------------------------------------

### `addItems`

``` prism-code
async addItems(items)
```

Add new items to the scene.

To create new items you can use the item [Builders](../reference/builders.md).

**Parameters**

| NAME  |               TYPE               | DESCRIPTION            |
|:-----:|:--------------------------------:|:-----------------------|
| items | [Item](../reference/item.md)\[\] | A list of items to add |

**Example**

Add a circle shape to the scene

``` prism-code
import OBR, { buildShape } from "@owlbear-rodeo/sdk";

const item = buildShape().width(10).height(10).shapeType("CIRCLE").build();
OBR.scene.items.addItems([item]);
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

Delete selected items when clicking a context menu item

``` prism-code
OBR.contextMenu.create({
  id: "rodeo.owlbear.example",
  icons: [
    {
      icon: "icon.svg",
      label: "Example",
    },
  ],
  onClick(context) {
    const ids = context.items.map((item) => item.id);
    OBR.scene.items.deleteItems(ids);
  },
});
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

**Example**

Delete selected items and their attachments when clicking a context menu item

``` prism-code
OBR.contextMenu.create({
  id: "rodeo.owlbear.example",
  icons: [
    {
      icon: "icon.svg",
      label: "Example",
    },
  ],
  async onClick(context) {
    const ids = context.items.map((item) => item.id);
    const allItems = await OBR.scene.items.getItemAttachments(ids);
    const allIds = allItems.map((item) => item.id);
    OBR.scene.items.deleteItems(allIds);
  },
});
```

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
| callback | (items: [Item](../reference/item.md)\[\]) =\> void | A callback for when an item changes. The items array will include all items in the scene, not just those that changed. |

Returns a function that when called will unsubscribe from change events.

**Example**

``` prism-code
/**
 * Use an `onChange` event with a React `useEffect`.
 * `onChange` returns an unsubscribe event to make this easy.
 */
useEffect(
  () =>
    OBR.scene.items.onChange((items) => {
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
