*~~If~~ When you come across anything that is broken/incorrect,
please let me know (open an issue in GitHub or just message in Discord)*

# Overview

The bot's main function is to sit and wait for users to make/start/end/cancel discord events
(server drop-down in the top-left, under create channel/category).
The bot only sends (public) messages in a designated channel (e.g. #dev-events for testing purposes).

## Event creation

When an event is created, the bot will make a post in a designated channel and create a thread from it for discussion about event details.
Only the bot and admins should be able to send messages in the designated channel,
but anyone should be able to send messages in the threads.
The main event message should show Discord's built-in event view, which allows you to mark yourself as *Interested*,
as well as a couple of buttons to add and remove non-Discord-member friends and open Google Maps to the event location.

For testing (or in the case that the bot is offline when an event is created),
you can manually register the event with `/events register <event-id>`

## Event deletion

When an event is cancelled or ended, the bot will delete the associated post and thread in the designated channel.

For testing (or in the case that the bot is offline when an event is cancelled/ended),
you can manually unregister (deregister?) an event from the bot with `/events clean <event-id>`.

## Benefits

The main benefits I see of using Discord events instead of managing events ourselves are:

1. Nicer event input modals/forms (not that Huburts aren't beautiful)
with better date validation than the Discord Developer API will let you make
2. Nicer formatting on the chat message for the event itself (again, because of limitations in the Discord Developer API)
3. Built-in list of upcoming events in the sidebar under events
(although the bot is still necessary to maintain a dedicated channel for the non-Discord-member attendees management and the event discussion threads)
