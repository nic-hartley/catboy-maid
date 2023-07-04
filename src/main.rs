use std::env;

use futures::{stream::SelectAll, StreamExt};
use model::{Session, event::Event};
use platform::discord::DiscordListener;
use sqlx::SqlitePool;
use tracing::Level;

mod platform;
mod model;
mod handle;

#[tracing::instrument(level = "debug")]
async fn journal(cxn: &SqlitePool, ev: &Event) -> anyhow::Result<u64> {
    let mut session = Session(cxn.begin().await?);
    let jid = session.add_entry(ev).await?;
    session.commit().await?;
    Ok(jid)
}

#[tokio::main(flavor = "current_thread")]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .compact()
        .with_max_level(Level::DEBUG)
        .with_timer(tracing_subscriber::fmt::time::uptime())
        .with_target(false)
        .init();

    if let Err(e) = dotenvy::dotenv() {
        tracing::warn!("ignoring .env file: {:?}", e);
    }

    let db_path = env::var("DATABASE_URL")
        .expect("Database URL needs to be configured");

    let cxn = SqlitePool::connect(&db_path).await?;
    {
        let mut txn = cxn.begin().await?;
        sqlx::migrate!().run(&mut txn).await?;
        txn.commit().await?;
    }

    // SelectAll<Pin<Box<dyn Stream<Item = anyhow::Result<Event>>>>>

    let mut sources = SelectAll::new();
    if let Some(token) = env::var("DISCORD_TOKEN").ok() {
        let stream = futures::stream::unfold(
            DiscordListener::new(token).await?,
            |mut dl| async move { Some((dl.next().await, dl)) }
        );
        sources.push(Box::pin(stream));
    }

    while let Some(ev) = sources.next().await {
        let ev = match ev {
            Ok(ev) => ev,
            Err(e) => {
                tracing::error!("failed to poll: {:?}", e);
                continue;
            }
        };

        // if there's an error storing it to the journal, exit
        let jid = journal(&cxn, &ev).await?;

        // then spawn off the handler to actually do the thing
        match cxn.begin().await {
            Ok(txn) => { tokio::spawn(ev.run(Session(txn), jid)); }
            Err(e) => tracing::error!("failed to connect to db: {:?}", e),
        };
    }

    Ok(())
}
