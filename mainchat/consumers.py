import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import Room, Message


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None
        self.user = None
        self.user_inbox = None
        self.messages = None

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.room = Room.objects.get(name=self.room_name)
        self.user = self.scope['user']
        self.user_inbox = f'inbox_{self.user.username}'
        self.messages = Message.objects.filter(room=self.room).order_by('-id')[:10]

        self.accept()

        print('room name:' + self.room_name)

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

        self.send(json.dumps({
            'type': 'user_list',
            'users': [user.username for user in self.room.online.all()],
        }))

        #print(Message.objects.filter(user=self.user, room=self.room).values('id', 'content').order_by('-id')[:10])

        self.send(json.dumps({
            'type': 'message_list',
            'users': [i.user.username for i in self.messages],
            'messages': [i.content for i in self.messages],
        }))

        if self.room_name.startswith('admin_'):
            self.send(json.dumps({
                'type': 'admin_list',
                'users': [user.username for user in self.room.online.all() if user.is_staff],
                'message': 'This room is for admins only',
            }))

            if self.user.is_staff:
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'user_join',
                        'user': self.user.username,
                    }
                )
                self.room.online.add(self.user)
            return

        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'user_join',
                    'user': self.user.username,
                }
            )
            self.room.online.add(self.user)

            self.send(json.dumps({
                'type': 'command_list',
                'message': 'Welcome, here is a list of commands that you can utilise '
                        '(the list is constantly getting updated): 1st - /pm (To private message) 2nd - /leave '
                           '(To leave the chat room)',
            }))

        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_add)(
                self.user_inbox,
                self.channel_name,
            )

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'user_leave',
                    'user': self.user.username,
                }
            )
            self.room.online.remove(self.user)

        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_discard)(
                self.user_inbox,
                self.channel_name,
            )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if not self.user.is_authenticated:
            return

        if self.room_name.startswith('admin_') and not self.user.is_staff:
            return

        if message == '/deleting':
            message_lists = Message.objects.filter(user=self.user, room=self.room).order_by('-id')[:10]
            self.send(json.dumps({
                'type': 'list_msg',
                'message_lists': message_lists.count(),
                'message_lists_id': [i.id for i in message_lists],
                'message_lists_content': [i.content for i in message_lists],
            }))

        if message == '/leave':
            if self.user.is_authenticated:
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'user_leave',
                        'user': self.user.username,
                    }
                )
                self.room.online.remove(self.user)

                self.send(json.dumps({
                    'type': 'leave_room',
                    'user': self.user.username,
                    'message': 'You have successfully left the chat.',
                }))

                async_to_sync(self.channel_layer.group_discard)(
                    self.room_group_name,
                    self.channel_name,
                )

        if message.startswith('/pm '):
            splitmsg = message.split(' ', 2)
            target = splitmsg[1]
            target_msg = splitmsg[2]

            async_to_sync(self.channel_layer.group_send)(
                f'inbox_{target}',
                {
                    'type': 'private_message',
                    'user': self.user.username,
                    'message': target_msg,
                }
            )

            self.send(json.dumps({
                'type': 'pm_delivered',
                'target': target,
                'message': target_msg,
            }))
            return

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user': self.user.username,
                'message': message,
            }
        )
        Message.objects.create(user=self.user, room=self.room, content=message)

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))

    def user_join(self, event):
        self.send(text_data=json.dumps(event))

    def user_leave(self, event):
        self.send(text_data=json.dumps(event))

    def private_message(self, event):
        self.send(text_data=json.dumps(event))

    def pm_delivered(self, event):
        self.send(text_data=json.dumps(event))

    def leave_room(self, event):
        self.send(text_data=json.dumps(event))

    def command_list(self, event):
        self.send(text_data=json.dumps(event))

    def admin_list(self, event):
        self.send(text_data=json.dumps(event))

    def message_list(self, event):
        self.send(text_data=json.dumps(event))

    def list_msg(self, event):
        self.send(text_data=json.dumps(event))
