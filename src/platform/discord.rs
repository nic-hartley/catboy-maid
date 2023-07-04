use twilight_gateway::{Shard, ShardId, Intents, Event as DiscordEvent, CloseFrame};

use crate::model::event::{Event as CmEvent};

fn why<'a>(cf: &'a Option<CloseFrame<'a>>) -> &'a str {
    match cf {
        Some(cf) => cf.reason.as_ref(),
        None => "no reason given",
    }
}

pub struct DiscordListener(Shard);

impl DiscordListener {
    #[tracing::instrument(name="connect discord", skip(token))]
    pub async fn new(token: String) -> anyhow::Result<Self> {
        let shard = Shard::new(
            ShardId::ONE, token.clone(),
            Intents::GUILDS | Intents::GUILD_MESSAGES | Intents::MESSAGE_CONTENT
        );
        let mut res = Self(shard);
        let ready = loop {
            match res.next_twilight().await? {
                // ignore some events that might come while we wait
                DiscordEvent::GatewayHello(..) => (),
                DiscordEvent::GatewayHeartbeat(..) => (),
                DiscordEvent::GatewayHeartbeatAck => (),
                // when we get `ready`  we're good to go
                DiscordEvent::Ready(r) => break r,
                // handle this particular error a little nicer
                DiscordEvent::GatewayClose(cf) => {
                    anyhow::bail!("gateway closed: {}", why(&cf));
                }
                // anything else, panic and die
                o => anyhow::bail!("got event other than ready: {:?}", o),
            };
        };
        tracing::info!("Connected as {:?} ({})", ready.user.name, ready.user.id);
        tracing::info!("In {} server(s)", ready.guilds.len());
        Ok(res)
    }

    #[inline]
    async fn next_twilight(&mut self) -> anyhow::Result<DiscordEvent> {
        loop {
            match self.0.next_event().await {
                Ok(e) => return Ok(e),
                Err(e) if e.is_fatal() => return Err(e.into()),
                Err(e) => {
                    tracing::warn!("reception failed: {:?}", e);
                    continue;
                }
            };
        }
    }

    #[tracing::instrument(skip(self))]
    pub async fn next(&mut self) -> anyhow::Result<CmEvent> {
        loop {
            let ev = self.next_twilight().await?;
            let span = tracing::debug_span!("handle event", ?ev);
            let _entered = span.enter();
            let res = match ev {
                DiscordEvent::GatewayClose(cf) => {
                    anyhow::bail!("gateway closed: {}", why(&cf));
                }
                DiscordEvent::GuildCreate(g) => CmEvent::DiscordJoin(g.id.get()),
                _ => {
                    tracing::debug!("ignoring");
                    continue;
                },
            };
            tracing::debug!("processed into {:?}", res);
            return Ok(res);
        }
    }
}
