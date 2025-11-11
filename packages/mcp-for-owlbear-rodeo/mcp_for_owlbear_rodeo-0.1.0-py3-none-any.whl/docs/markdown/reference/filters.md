# Filters

A common pattern in the Owlbear Rodeo SDK is the use of a Filter object to control when certain values are used.

A prevalent example is the [IconFilter](../apis/context-menu.md#contextmenuiconfilter) used in the Context Menu.

There is often times when a context menu item should have different icons depending on what is selected. For example the hidden icon should show an open eye if the selected items are visible. If the items are hidden it should show a closed eye instead.

Instead of needing to write an imperative program that listens to changes in the context menu and calls a `setIcon` method we uses a declarative approach. To create a menu item that switches between two icons we initialize our item with two icons. Each icon then has a filter that will tell Owlbear Rodeo which icon to use.

Here's an example of a visibility toggle context menu item.

``` prism-code
OBR.contextMenu.create({
  id: "com.example.visibility",
  icons: [
    {
      icon: "/show.svg",
      label: "Hide",
      // Only use the `show` icon when all selected items are visible
      filter: {
        every: [{ key: "visible", value: true }],
      },
    },
    // Use the `hide` icon by default
    {
      icon: "/hide.svg",
      label: "Show",
    },
  ],
  onClick(context) {
    OBR.scene.items.updateItems(context.items, (items) => {
      const isVisible = items.every((item) => item.visible);
      for (let item of items) {
        item.visible = !isVisible;
      }
    });
  },
});
```

In the example above a KeyFilter is used to check that the [`visible`](item.md) key is set to true on all selected items. If this filter passes then the `show.svg` icon is used. If this filter does not pass then the `hide.svg` icon is used.

### KeyFilter

The key filter is common type of filter used to check a key-value pair on an object.

**Example**

``` prism-code
// The visible property must be `true`
const a = [{ key: "visible", value: true }];

// The visible property must be `true` and the type must not equal `DRAWING`
const b = [
  { key: "visible", value: true },
  { key: "type", value: "DRAWING", operator: "!=" },
];

// The visible property must be `true` or the type must not equal `DRAWING`
const c = [
  { key: "visible", value: true, coordinator: "||" },
  { key: "type", value: "DRAWING", operator: "!=" },
];
```

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| key | string \| string\[\] | The path to the key to check. Works the same as the `path` property in lodash.get |
| value | unknown | The value to check |
| operator | "==" \| "!=" | The operator to use for the check. By default "==" is used meaning the passed value has to equal the test value. |
| coordinator | "&&" \| "\|\|" | When an array of filters are used what logical coordinator should be used to combine them. By default a logical "and" operation is used (`&&`). |
