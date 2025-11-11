# Party

## `OBR.party`

The party api gives you access to other players currently in the room.

# Reference

## Methods

### `getPlayers`

``` prism-code
async getPlayers()
```

Get the other players currently in the room.

Returns an array of [Players](#player).

------------------------------------------------------------------------

### `onChange`

``` prism-code
onChange(callback);
```

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| callback | (players: [Player](../reference/player.md)\[\]) =\> void | A callback for when any connected player joins, leaves or changes |

Returns a function that when called will unsubscribe from change events.

**Example**

``` prism-code
/**
 * Use an `onChange` event with a React `useEffect`.
 * `onChange` returns an unsubscribe event to make this easy.
 */
useEffect(
  () =>
    OBR.party.onChange((party) => {
      // React to party changes
    }),
  []
);
```

------------------------------------------------------------------------
