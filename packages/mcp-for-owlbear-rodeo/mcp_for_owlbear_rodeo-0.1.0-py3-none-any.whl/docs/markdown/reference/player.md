# Player

A player connected to a room.

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| id | string | The user ID for this player. This will be shared if the same player joins a room multiple times |
| connectionId | string | The ID for this players connection. This will be unique if the same player joins the room multiple times |
| role | "GM" \| "PLAYER" | The current role for the player |
| selection | string\[\] | An optional array of item IDs referencing what this player has selected |
| color | string | The chosen color for this player |
| syncView | boolean | Whether this player has sync view enabled |
| metadata | [Metadata](metadata.md) | The custom metadata for this player |

------------------------------------------------------------------------
