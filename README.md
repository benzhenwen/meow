# Meow Bot
Counts how many times a member has meowed!

Designed specifically for the few servers it's in, not for large-scale.

## Meow Commands
get_meow_count(user, is_ephemeral) - View the number of times a user has meowed

leaderboard(is_ephemeral)          - View the top 10 meow counts

* is_ephemeral defaults to true. When true, your message is hidden to everyone but you, and is temporary.

## Privacy
Your messages are in no way stored (including overriding Disnake's default caching system). Unless opted in, meow will only ever view a message once to determine a few basic behaviours and count the number of meows.

You can opt in by dm-ing ben208 on discord. If you opt in, your server's administrators (and any specified roles) will be given access to a new command: get_message_cache(is_ephemeral), that will display up to the latest 25 deleted messages on your server.

get_message_cache(is_ephemeral) is designed as a tool for moderators.

# Contribution
You are welcome to clone and run this bot yourself, but please do not submit any merge requests.
