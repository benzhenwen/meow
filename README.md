# Meow Bot
Counts how many times a member has meowed!

Designed specifically for the few servers it's in, not for large-scale.

## Meow Commands
get_meow_count(user, is_ephemeral) - View the number of times a user has meowed

leaderboard(is_ephemeral)          - View the top 10 meow counts

* is_ephemeral defaults to true. When true, your message is hidden to everyone but you, and is temporary.

## Privacy
Your messages are in no way stored (including overriding Disnake's default caching system). Unless opted in, meow will only ever view a message once to determine a few basic behaviours and count the number of meows.

You can opt in by dm-ing ben208 on discord. If you opt in, server members with "moderate members" permissions will be given access to a new command: get_message_cache(is_ephemeral), that will display up to the latest 25 deleted messages on your server.

## Moderator tools
**commands accessable through the "moderate members" permissions:**

get_message_cache(is_ephemeral) is designed as a tool for moderators. (if message logging opted in)

set_meow_chance(value) 0-1 sets the chance meow meows back (default value = 0.05)

set_nya_chance(value) 0-1 sets the chance meow :3 back (default value = 0.05)


# Contribution
You are welcome to clone and run this bot yourself, but please do not submit any merge requests.
