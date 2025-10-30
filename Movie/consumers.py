import asyncio
import contextlib
import json
import platform

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from Movie.models import Video

"""
 ** Plan
    first is the first connection that user makes to get the information and those information are the information that
    has already been set in the database.
    Then a change happened and then all the data in json_data field should be reset and the new details should be set

    what are the triggers for change? has_intro, status, action, subbed.
"""

# Apply Windows event loop policy at top level if needed
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class VideoProcessingConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.movie_uuid = None
        self.last_statuses = {}
        self.update_task = None

    async def connect(self):
        self.movie_uuid = self.scope['url_route']['kwargs']['uuid']
        await self.accept()
        # await self._get_last_statuses()
        # Start background update task
        self.update_task = asyncio.create_task(self._monitor_videos())

    async def disconnect(self, close_code):
        # Cancel the monitoring loop cleanly
        if hasattr(self, 'update_task'):
            self.update_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.update_task

    @sync_to_async
    def _fetch_videos(self):
        # Fetch all Video instances for this movie
        return list(Video.objects.filter(movie__uuid=self.movie_uuid))

    async def _make_snapshot(self, video):
        data = {
            'uuid': video.uuid,
            'status': video.status,
            'current_step': 'nothing',
            'action': video.action,
            'steps': [],
            'error': video.error_message if video.status == 'failed' else None,
            'has_intro': video.has_intro,
            'subbed': video.subbed,
            **(video.json_data or {})
        }
        return data

    async def _get_status_snapshot(self):
        # Build a dict of uuid->status
        videos = await self._fetch_videos()
        snapshot = {}
        for video in videos:
            snapshot[video.uuid] = await self._make_snapshot(video)
        return snapshot

    async def _monitor_videos(self):

        try:
            while True:
                changed = []
                snapshots = await self._get_status_snapshot()
                # Determine if any status changed
                for key in snapshots:
                    value = snapshots[key]
                    status_item = self.last_statuses[key] if key in self.last_statuses.keys() else None
                    if value != status_item or value['status'] == 'processing':
                        changed.append(value)
                        self.last_statuses[key] = value
                    # If something changed or there's ongoing progress, send update
                if len(changed) > 0:
                    await self.send(json.dumps(changed))
                # Sleep for a second before next check
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            # Clean shutdown
            return