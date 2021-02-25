import praw
import random
import socket
import webbrowser
from prawcore.exceptions import ResponseException

from src.utils import GLOBAL
from src.jsonHelper import JsonFile
from src. errors import RedditLoginFailed


class Reddit:

    def __init__(self, refresh_token=None):
        self.SCOPES = ['identity', 'history', 'read', 'save']
        self.PORT = 7634
        self.refresh_token = refresh_token
        self.redditInstance = None
        self.arguments = {
            "client_id": GLOBAL.reddit_client_id,
            "client_secret": GLOBAL.reddit_client_secret,
            "user_agent": str(socket.gethostname())
        }

    def begin(self):

        if self.refresh_token:
            self.arguments["refresh_token"] = self.refresh_token
            self.redditInstance = praw.Reddit(**self.arguments)
            try:
                self.redditInstance.auth.scopes()
                return self.redditInstance
            except ResponseException:
                self.arguments["redirect_uri"] = "http://localhost:" + \
                    str(self.PORT)
                self.redditInstance = praw.Reddit(**self.arguments)
                reddit, refresh_token = self.getRefreshToken(*self.SCOPES)
        else:
            self.arguments["redirect_uri"] = "http://localhost:" + \
                str(self.PORT)
            self.redditInstance = praw.Reddit(**self.arguments)
            reddit, refresh_token = self.getRefreshToken(*self.SCOPES)

        JsonFile(GLOBAL.configDirectory).add({
            "reddit_username": str(reddit.user.me()),
            "reddit": refresh_token
        }, "credentials")

        return self.redditInstance

    def recieve_connection(self):
        """Wait for and then return a connected socket..
        Opens a TCP connection on port 8080, and waits for a single client.
        """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', self.PORT))
        server.listen(1)
        client = server.accept()[0]
        server.close()
        return client

    @staticmethod
    def send_message(client, message):
        """Send message to client and close the connection."""
        client.send(
            'HTTP/1.1 200 OK\r\n\r\n{}'.format(message).encode('utf-8')
        )
        client.close()

    def getRefreshToken(self, *scopes):
        state = str(random.randint(0, 65000))
        url = self.redditInstance.auth.url(scopes, state, 'permanent')
        print("---Setting up the Reddit API---\n")
        print(
            "Go to this URL and login to reddit:\n",
            url,
            sep="\n",
            end="\n\n")
        webbrowser.open(url, new=2)

        client = self.recieve_connection()
        data = client.recv(1024).decode('utf-8')
        str(data)
        param_tokens = data.split(' ', 2)[1].split('?', 1)[1].split('&')
        params = dict([token.split('=')
                       for token in param_tokens])
        if state != params['state']:
            self.send_message(
                client, 'State mismatch. Expected: {} Received: {}'
                .format(state, params['state'])
            )
            raise RedditLoginFailed
        if 'error' in params:
            self.send_message(client, params['error'])
            raise RedditLoginFailed

        refresh_token = self.redditInstance.auth.authorize(params['code'])
        self.send_message(client,
                          "<script>"
                          "alert(\"You can go back to terminal window now.\");"
                          "</script>"
                          )
        return (self.redditInstance, refresh_token)
