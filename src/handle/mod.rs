use std::time::Duration;

use crate::model::{event::Event, Session};

impl Event {
    pub async fn run<'c>(self, mut session: Session<'c>, jid: u64) -> anyhow::Result<()> {
        // Dispatch to the correct actual handler for this event
        match self {
            Event::DiscordJoin(id) => {
                tokio::time::sleep(Duration::from_millis((id % 10) * 100)).await;
            }
        }
        // once that's done, mark this journal entry as complete
        session.complete_entry(jid).await?;
        Ok(())
    }
}