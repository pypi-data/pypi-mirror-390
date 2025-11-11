# Metadata

The Metadata object is a common pattern in the Owlbear Rodeo SDK that allows your extension to store/share custom data.

All items in a scene have a metadata property that allows you to store custom data.

All players also have a metadata property that allows you to share custom data associated with that player.

**Best Practices**

When using a metadata property be aware that you will be sharing this resource with other extensions. This means it is necessary that you do all you can to avoid namespace collisions.

Our recommendation is that you prefix all your keys in the metadata with a common identifier for your extension.

The convention used in our tutorial and example projects is to use a reverse domain name notation such as `com.example.metadata` that represents the domain for your extension.

For example the metadata used in our [initiative tracker tutorial](https://docs.owlbear.rodeo/extensions/tutorial-initiative-tracker/implement-the-context-menu-item) looks like this:

``` prism-code
{
  "com.tutorial.initiative-tracker/metadata": {
    initiative: number,
  },
};
```

|           TYPE            |
|:-------------------------:|
| Record\<string, unknown\> |
