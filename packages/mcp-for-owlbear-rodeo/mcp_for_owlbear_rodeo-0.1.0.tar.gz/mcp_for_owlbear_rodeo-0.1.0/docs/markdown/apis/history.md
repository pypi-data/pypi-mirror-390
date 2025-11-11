# History

## `OBR.scene.history`

Interact with the undo/redo stack of the scene.

# Reference

## Methods

### `undo`

``` prism-code
async undo()
```

Undo the previous action.

------------------------------------------------------------------------

### `redo`

``` prism-code
async redo()
```

Redo the an action that was undone.

------------------------------------------------------------------------

### `canUndo`

``` prism-code
async canUndo()
```

Returns true if there is an action on the undo stack.

------------------------------------------------------------------------

### `canRedo`

``` prism-code
async canRedo()
```

Returns true if there is an action on the redo stack.

------------------------------------------------------------------------
