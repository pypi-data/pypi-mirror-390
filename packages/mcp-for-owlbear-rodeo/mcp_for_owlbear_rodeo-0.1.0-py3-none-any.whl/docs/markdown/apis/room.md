# Room

## `OBR.room`

The room API gives you access to the current room the extension is being used in.

# Reference

**Properties**

| NAME |  TYPE  | DESCRIPTION                       |
|:----:|:------:|:----------------------------------|
|  id  | string | A unique ID for the current room. |

------------------------------------------------------------------------

## Methods

### `getPermissions`

``` prism-code
async getPermissions()
```

Get the current permissions for players in this room.

Returns a [Permission](../reference/permission.md) array.

------------------------------------------------------------------------

### `onPermissionsChange`

``` prism-code
onPermissionsChange(callback);
```

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| callback | (permissions: [Permission](../reference/permission.md)\[\]) =\> void | A callback for when the permissions of the current room changes |

Returns a function that when called will unsubscribe from change events.

**Example**

``` prism-code
/**
 * Use an `onPermissionsChange` event with a React `useEffect`.
 * `onPermissionsChange` returns an unsubscribe event to make this easy.
 */
useEffect(
  () =>
    OBR.room.onPermissionsChange((permissions) => {
      // React to rooms permissions change
    }),
  []
);
```

------------------------------------------------------------------------

### `getMetadata`

``` prism-code
async getMetadata()
```

Get the current metadata for this room.

returns a [Metadata](../reference/metadata.md) object.

------------------------------------------------------------------------

### `setMetadata`

``` prism-code
async setMetadata(update)
```

Update the metadata for this room.

See [Metadata](../reference/metadata.md) for best practices when updating metadata.

Room metadata is intended for small bits of stored data for an extension.

In total the room metadata must be under 16kB.

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| update | Partial\<[Metadata](../reference/metadata.md)\> | A partial update to this rooms metadata. The included values will be spread among the current metadata to avoid overriding other values. |

------------------------------------------------------------------------

### `onMetadataChange`

``` prism-code
onMetadataChange(callback);
```

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| callback | (metadata: [Metadata](../reference/metadata.md)) =\> void | A callback for when the metadata of the current room changes |

Returns a function that when called will unsubscribe from change events.

**Example**

``` prism-code
/**
 * Use an `onMetadataChange` event with a React `useEffect`.
 * `onMetadataChange` returns an unsubscribe event to make this easy.
 */
useEffect(
  () =>
    OBR.room.onMetadataChange((metadata) => {
      // React to rooms metadata changes
    }),
  []
);
```

------------------------------------------------------------------------
