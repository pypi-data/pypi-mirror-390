# Convex Space Manager

A simple Python package for managing space availability in Convex databases.

## Features

- 🚀 **Simple API** - Easy-to-use interface for space management
- 🔄 **Batch Updates** - Update multiple spaces at once
- ⚡ **Real-time** - Instant updates to your Convex database
- 📦 **Lightweight** - Minimal dependencies, just Python + Convex
- 🛠️ **Flexible** - Works with any space naming convention

## Installation

```bash
pip install convex-space-manager
```

## Quick Start

```python
from convex_space_manager import convex_sync

# Your space data
spaces = ["space1", "space2", "space3", "space4", "space5"]
availability = [True, False, True, False, True]  # True = full, False = available

# Update all spaces at once
convex_sync(availability, spaces, "https://your-deployment.convex.cloud")
```

## Advanced Usage

```python
from convex_space_manager import ConvexSpaceManager

# Initialize manager
manager = ConvexSpaceManager("https://your-deployment.convex.cloud")

# Update individual spaces
manager.update_space("space1", True)   # space1 is now full
manager.update_space("space2", False)  # space2 is now available

# Update multiple spaces
spaces = ["space1", "space2", "space3"]
availability = [True, False, True]
manager.update_multiple_spaces(spaces, availability)
```

## Requirements

- Python 3.7+
- Convex deployment URL
- Convex database with `spaces` table containing `spaceName` and `isFull` fields

## Convex Schema

Your Convex database should have a `spaces` table with this structure:

```typescript
spaces: defineTable({
  spaceName: v.string(),
  isFull: v.boolean(),
}).index("by_spaceName", ["spaceName"])
```

And a mutation function:

```typescript
export const update_fullness = mutation({
  args: {
    spaceName: v.string(),
    isFull: v.boolean(),
  },
  handler: async (ctx, args) => {
    const existingSpace = await ctx.db
      .query("spaces")
      .withIndex("by_spaceName", (q) => q.eq("spaceName", args.spaceName))
      .first();

    if (existingSpace) {
      await ctx.db.patch(existingSpace._id, {
        isFull: args.isFull,
      });
    } else {
      await ctx.db.insert("spaces", {
        spaceName: args.spaceName,
        isFull: args.isFull,
      });
    }
  },
});
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
