# Scene

## `OBR.scene`

A scene is an infinite space for you to lay out images, drawings, fog and more.

# Reference

## Methods

### `isReady`

``` prism-code
async isReady()
```

Returns true if there is a scene opened and it is ready to interact with.

------------------------------------------------------------------------

### `onReadyChange`

``` prism-code
onReadyChange(callback);
```

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| callback | (ready: boolean) =\> void | A callback for when the current scene changes its ready state |

Returns a function that when called will unsubscribe from change events.

**Example**

``` prism-code
/**
 * Use an `onReadyChange` event with a React `useEffect`.
 * `onReadyChange` returns an unsubscribe event to make this easy.
 */
useEffect(
  () =>
    OBR.scene.onReadyChange((ready) => {
      if (ready) {
        // interact with the scene
      }
    }),
  []
);
```

------------------------------------------------------------------------

### `getMetadata`

``` prism-code
async getMetadata()
```

Get the current metadata for this scene.

returns a [Metadata](../reference/metadata.md) object.

------------------------------------------------------------------------

### `setMetadata`

``` prism-code
async setMetadata(update)
```

Update the metadata for this scene.

See [Metadata](../reference/metadata.md) for best practices when updating metadata.

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| update | Partial\<[Metadata](../reference/metadata.md)\> | A partial update to this scenes metadata. The included values will be spread among the current metadata to avoid overriding other values. |

------------------------------------------------------------------------

### `onMetadataChange`

``` prism-code
onMetadataChange(callback);
```

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| callback | (metadata: [Metadata](../reference/metadata.md)) =\> void | A callback for when the metadata changes |

Returns a function that when called will unsubscribe from change events.

**Example**

``` prism-code
/**
 * Use an `onMetadataChange` event with a React `useEffect`.
 * `onMetadataChange` returns an unsubscribe event to make this easy.
 */
useEffect(
  () =>
    OBR.scene.onMetadataChange((metadata) => {
      // React to metadata changes
    }),
  []
);
```

------------------------------------------------------------------------

## 📄️ Fog

OBR.scene.fog

## 📄️ Grid

OBR.scene.grid

## 📄️ History

OBR.scene.history

## 📄️ Items

OBR.scene.items

## 📄️ Local

OBR.scene.local
