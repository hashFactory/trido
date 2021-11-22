## Projectory

A platform meant to facilitate collaboration and file sharing. Should be a file-sharing-first platform. Sort of blog-like where anybody can submit a post to a global feed that anyone on the server can view. People on the server can then reply to the post either with another rich-media comment or plain text.

This could be web only but it would be useful to have a mobile app as well for push notifications and being able to save media offline.

### Business Model

***Personal***

Acts as a mini social network.

They host: _(free)_
- users can choose to host their own instance free of charge
- we just provide the software

We host: _(free or paid)_
- we host a free tier that places some restrictions on file size
- provide paid tier the lets users post full-size files without restrictions
    - subscription fee / month (maybe $10-20 range?)
    - Apple Pay "pool" where everyone in the server participates and subscribes for $2/month to join
        - must be easy to subscribe / unsub

***Professional***

Acts as a project tracker / easy dropoff colaboration platform.

They host: _(paid)_
- sold as a SaaS
- like personal version with more specific project tracking functions

We host: _(paid)_
- sold as a SaaS
- should be easy to spawn new instances on a per-project basis
- also bill for storage costs

### Instances

Self hosted by users or hosted by us. Access should be restricted to invite-only by the server's owner. Everything should be customizable including css styling of all components. Maybe even specific to users within a server.
Possibility of also having each private server have a public-facing page (also stylized) that lets a group showcase work or ask for help within a specific area of expertise the group could use help with. Possibly make servers peer-discoverable.

### Posts

Posts can contain any type of file or link (audio file, video, link, text, program-specific project files, zip, w/e) with additional text. Posts could be made to either showcase work, simply post for the sake of sharing it, or ask for comments / collaboration. Posts are displayed like blog entries in a main feed.

Display features:
- text
    - pure text (maybe markdown or at least html/css)
    - link + text
- visual (single or gallery)
    - images
    - videos
    - gifs
- audio
    - single track (or album or playlist)
    - album
    - playlist of files
    - spotify (detect link and embed player(?))
- files
    - software project files (.psd, .als, .blend, etc...)
    - .zip, .img, .iso, .w/e

Make it easy to listen to audio with a click-once-and-let-play function.
Everyone within the server should be able to comment.
Comments should also be able to contain rich media.
Can like / repost comments and posts.
Tag posts using custom keywords (or by color).
Tag @people in a post or comment to send them push notification.
Can also subscribe to custom keyword tags to get notified.

