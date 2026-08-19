# media

The introduction video is on YouTube, so nothing needs to live here. The
introduction page uses:

    [youtube: D-qSe4Qr5z0 | caption]

## How the YouTube embed behaves

It is click-to-play, on purpose. Until a reader clicks, the page loads only
the thumbnail image — no YouTube player, no cookies, no tracking. On click
the player is created against `youtube-nocookie.com`. The page is also
faster for it, since the YouTube player is a heavy thing to load for a
visitor who never presses play.

The thumbnail YouTube serves is 4:3 with black bars; the stylesheet crops it
to 16:9, which removes them.

## If you ever want to host a video here instead

Put the file in this folder and use `[video: media/whatever.mp4]`. While the
file is absent the page shows a placeholder rather than a broken player.

Keep it under about 50 MB — GitHub warns above 50 MB and refuses above
100 MB. H.264 in an MP4 container plays everywhere:

    ffmpeg -i source.mov -vcodec libx264 -crf 26 -preset slow \
           -vf scale=1280:-2 -acodec aac -b:a 128k media/introduction.mp4

YouTube is the better option for anything long. This is here for short
clips you would rather not put on someone else's platform.
