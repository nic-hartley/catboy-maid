"""
The main interface plugging the actual platform APIs into Catboy Maid.
Generally, each module will have two halves:

- Transforming platform-specific events into database updates, to trigger
  actions living somewhere in `..pipeline`
- Listening for database updates to reflect those updates on platform
"""
