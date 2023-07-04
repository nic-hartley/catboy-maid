//! The core architecture of Catboy Maid is this:
//! 
//! - Events are received from the various APIs
//! - They're converted to this `Event` type
//! - The event is written to the [`journal`](super::journal) (as unhandled)
//! - Then `Event::handle` is [`spawn`ed](tokio::spawn), running it in the background
//! - When `Event::handle` completes, it marks its event as complete
//! 
//! At the center of all this is the `Event` enum, which represents every single event that Catboy Maid can handle. It
//! needs to be serializable, to be stored in the journal or spread across a cluster, and it needs to have enough info
//! to work from just that event.

use serde::{Serialize, Deserialize};

/// A thing that happened, according to the various clients.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum Event {
    /// The bot joined a Discord server
    DiscordJoin(u64),
}
