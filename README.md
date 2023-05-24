# Catboy Maid

Adorably taking out the trash, nya~

In plain English, Catboy Maid helps communities share moderation info with each other.
Keep collaborative notes on users, including tallying warnings across communities, sharing ban reasons, and logging problematic messages even if they're deleted or edited.

For example, let's say EvilBastard#1234 joins your Discord server.
Following an act too heinous to describe here, you ban them.
Immediately:

- You're prompted for a reason, if one isn't already available.
  The rest of these steps proceed regardless -- messages posted will be edited with reasons when they're added.
- Previous bans in your social circle have associated EvilBastard#1234 with twitch.tv/evilbastard1234.
  evilbastard1234 is banned off your Twitch chat as well.
- Your Catboy Maid posts in its notifications channel, so your moderators and peers are aware.
- Your friend NiceBastard's Catboy Maid is watching that notifications channel.
  NiceBastard's Catboy is configured to mirror your moderation actions, so EvilBastard#1234 is banned from their Discord and evilbastard1234 is banned from their Twitch.
- Your other friend Placeholder Name has configured their Catboy to notify them when you ban, but not ban automatically.
  Their Catboy Maid posts a message with the user's info, the ban reason, and a few buttons to easily take action.
- Later, another community starts syncing their Catboy Maid with yours.
  EvilBastard#1234 is in their Discord server, so the moderators are notified of their previous ban, and the reason, and have a handy button to immediately ban them there too.

All this is completely automated, once set up, and configured through simple Discord commands.

## Running

One Catboy Maid software instance can power multiple communities' Catboy Maids, even if those communities don't necessarily share moderation info.
Each community needs to trust the host, since they'll have access to the bot tokens with permissions to perform moderation actions.

If you're planning to host, it's relatively simple, as these things go.
Catboy Maid usually comes as a Docker container.
You can run it anywhere that supports them:

- [Docker Desktop](https://docs.docker.com/get-docker/), which is probably best if you're not technically proficient
- On the command line with `docker` or `podman`, if you're confident setting up the relevant networking
- In a Kubernetes or other container cluster, if you've already got one and want to make use of it

You'll need to make sure Catboy Maid has internet access, and that you've mounted `/cm/` into the container, to store some necessary files.
For example, in Docker Desktop:

TODO: Docker Desktop step-by-step guide

Or using Podman:

```sh
TODO: podman example
```

## Federating

TODO: Figure out how federating works (Discord DMs maybe? Watching channels? Onion services? As long as it's firewall-friendly.)
