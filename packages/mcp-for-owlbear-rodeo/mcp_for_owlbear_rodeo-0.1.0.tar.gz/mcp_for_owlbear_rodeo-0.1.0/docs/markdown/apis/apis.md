# APIs

## `OBR`

The base API to interact with Owlbear Rodeo

# Reference

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| isReady | boolean | True if the SDK has been loaded and is ready to send messages |
| isAvailable | boolean | True if the current site is embedded in an instance of Owlbear Rodeo |

**Example**

``` prism-code
if (OBR.isAvailable) {
  // The current site is embedded in Owlbear Rodeo
}
```

## Methods

### `onReady`

``` prism-code
onReady(callback);
```

**Parameters**

|   NAME   |    TYPE     | DESCRIPTION                               |
|:--------:|:-----------:|:------------------------------------------|
| callback | () =\> void | A callback for when when the SDK is ready |

Returns a function that when called will unsubscribe from change events.

**Example**

``` prism-code
/**
 * Use an `onReady` event with a React `useEffect`.
 * `onReady` returns an unsubscribe event to make this easy.
 */
useEffect(
  () =>
    OBR.onReady(() => {
      // interact with the SDK
    }),
  []
);
```

------------------------------------------------------------------------

## 📄️ Action

OBR.action

## 📄️ Assets

OBR.assets

## 📄️ Broadcast

OBR.broadcast

## 📄️ Context Menu

OBR.contextMenu

## 📄️ Interaction

OBR.interaction

## 📄️ Modal

OBR.modal

## 📄️ Notification

OBR.notification

## 📄️ Party

OBR.party

## 📄️ Player

OBR.player

## 📄️ Popover

OBR.popover

## 📄️ Room

OBR.room

## 🗃️ Scene

5 items

## 📄️ Theme

OBR.theme

## 📄️ Tool

OBR.tool

## 📄️ Viewport

OBR.viewport
