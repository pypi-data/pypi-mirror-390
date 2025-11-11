# Manifest

A manifest contains information about the extension and is necessary for loading an extension.

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| name | string | The name of the extension, limited to 45 characters |
| version | string | The version number of the extension |
| manifest_version | number | The targeted manifest version |
| description | string | The description of the extension, limited to 128 characters |
| icon | string | An optional path to the extensions icon |
| author | string | An optional author to display for the extension |
| homepage_url | string | An optional link to a home page for the extension |
| action | [ManifestAction](#manifestaction) | An optional action for this extension |
| background_url | string | An optional url to load as a background script |
| permissions | [ManifestPermission](#manifestpermission)\[\] | An optional array of permissions to give to all iframes of your extension |

## Type Definitions

### ManifestAction

The action definition for a manifest.

To control the action after an extension has been loaded see the [Action API](../apis/action.md).

|  TYPE  |
|:------:|
| object |

**Properties**

|  NAME   |  TYPE  | DESCRIPTION                            |
|:-------:|:------:|:---------------------------------------|
|  title  | string | The initial title of the action        |
|  icon   | string | The initial icon of the action         |
| popover | string | The url of the popover page to load    |
|  width  | number | An optional max width for the popover  |
| height  | number | An optional max height for the popover |

### ManifestPermission

Permissions used with the iframe allow property of your extension and a reason why you need it.

|  TYPE  |
|:------:|
| object |

**Properties**

| NAME | TYPE | DESCRIPTION |
|:--:|:--:|:---|
| name | [ManifestPermissionName](#manifestpermissionname) | The name of the permission |
| reason | string | The reason for use |

### ManifestPermissionName

The currently supported values available for a manifest permission

| TYPE | values |
|:--:|:---|
| string | "clipboard-write" \| "clipboard-read" \| "autoplay" \| "bluetooth" \| "camera" \| "microphone" \| "usb" \| "display-capture" \| "hid" |
