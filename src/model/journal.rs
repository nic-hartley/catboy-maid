//! Types used for crash recovery.
//! 
//! Notably, the main crash recovery strategy is that when running, we:
//! 
//! - Rapidly writing, synchronously and in order, all events received
//! - Passing them off to (unordered, parallel, async) handling, which marks them as "complete" when done
//! - All of the database access is done within a transaction and API operations are idempotent
//! 
//! Then after a shutdown, we:
//! 
//! - Process all journaled but incomplete events
//! - Query the services for events that happened after the latest event
//! - Resume processing from there
//! 
//! This ensures we don't need to worry too much about synchronizing while handling events, but can still recover
//! cleanly without too much trouble.

/// A queued event, possibly not yet handled.
#[derive(Clone, PartialEq, Eq, PartialOrd, Ord)]
pub struct Entry {
    /// The unique ID for the event
    pub id: i64,
    /// Whether or not this event was fully and completely handled
    pub handled: bool,
    /// Miscellaneous event data (a `PlatformEvent` enum, serialized with bincode)
    pub content: Vec<u8>,
}

impl<'c> super::Session<'c> {
    /// Log that an event has happened.
    /// 
    /// The transaction should, ideally, get flushed as soon as possible.
    pub async fn add_entry(&mut self, data: &impl serde::Serialize) -> sqlx::Result<u64> {
        let bytes = bincode::serialize(data).expect("data should be serializable?");
        let rowid = sqlx::query!("INSERT INTO journal (handled, content) VALUES (0, ?)", bytes)
            .execute(&mut self.0)
            .await?
            .last_insert_rowid();
        Ok(rowid as u64)
    }

    pub async fn complete_entry(&mut self, id: u64) -> sqlx::Result<()> {
        let id = id as i64;
        sqlx::query!("UPDATE journal SET handled = 1 WHERE id = ?", id)
            .execute(&mut self.0)
            .await?;
        Ok(())
    }
}
