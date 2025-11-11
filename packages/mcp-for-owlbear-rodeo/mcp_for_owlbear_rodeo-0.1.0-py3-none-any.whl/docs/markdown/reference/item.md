# Item

The abstract interface for all Items.

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| id | string | The ID of this item (read only) |
| type | string | The type of item |
| name | string | The name of the item |
| visible | boolean | Is this item visible |
| locked | boolean | Is this item locked |
| createdUserId | string | The user ID of the player who created this item |
| zIndex | number | The depth order of this item compared to other items on this layer |
| lastModified | string | When this item was last modified (read only) |
| lastModifiedUserId | string | The user ID of the player who last modified this item (read only) |
| position | [Vector2](vector2.md) | The position of this item |
| rotation | number | The rotation of this item in degrees |
| scale | [Vector2](vector2.md) | The scale of this item |
| metadata | [Metadata](manifest.md) | Custom metadata for this item |
| layer | [Layer](#layer) | The layer that this item is on |
| attachedTo | string | The optional ID of the item this is attached to |
| disableHit | boolean | An optional boolean to disable the hit detection for this item |
| disableAutoZIndex | boolean | An optional boolean to disable the auto z-index update for this item |
| disableAttachmentBehavior | [AttachmentBehavior](#attachmentbehavior)\[\] | An optional array of attachment behaviors to disable |
| description | string | An optional description used by assistive technology |

## Type Definitions

### Layer

| TYPE | values |
|:--:|:---|
| string | "MAP" \| "GRID" \| "DRAWING" \| "PROP" \| "MOUNT" \| "CHARACTER" \| "ATTACHMENT" \| "NOTE" \| "TEXT" \| "RULER" \| "FOG" \| "POINTER" \| "POST_PROCESS" \| "CONTROL" \| "POPOVER" |

### AttachmentBehavior

| TYPE | values |
|:--:|:---|
| string | "VISIBLE" \| "SCALE" \| "ROTATION" \| "POSITION" \| "DELETE" \| "LOCKED" \| "COPY" |
