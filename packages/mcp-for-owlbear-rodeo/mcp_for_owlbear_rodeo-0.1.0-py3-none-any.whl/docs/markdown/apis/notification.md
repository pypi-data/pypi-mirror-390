# Notification

## `OBR.notification`

Show notifications in the Owlbear Rodeo interface.

# Reference

## Methods

### `show`

``` prism-code
async show(message, variant?)
```

Show a notification.

**Parameters**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:--:|
| message | string | The message to show in the notification |
| variant | "DEFAULT" \| "ERROR" \| "INFO" \| "SUCCESS" \| "WARNING" | An optional style variant for the notification |

Returns the notification ID as a string.

------------------------------------------------------------------------

### `close`

``` prism-code
async close(id)
```

Close a notification.

**Parameters**

| NAME |  TYPE  |             DESCRIPTION             |
|:----:|:------:|:-----------------------------------:|
|  id  | string | The ID of the notification to close |

------------------------------------------------------------------------
