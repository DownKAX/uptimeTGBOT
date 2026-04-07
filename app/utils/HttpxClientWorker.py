import threading
import httpx
import json

from app.api.models.users import Url
from redis_client import get_sync_redis


class ClientWorker:
    def __init__(self):
        self.stats = {
            'success': 0,
            'read_timeout': 0,
            'read_error': 0,
            'connect_error': 0,
            'connect_timeout': 0,
            'pool_timeout': 0,
            'remote_protocol': 0,
            'total': 0
        }
        self.num_threads = 800
        self.threads = []
        self.r = get_sync_redis()
        self.lock = threading.Lock()

    def worker(self):
        client = httpx.Client(
            timeout=httpx.Timeout(connect=1.5, read=2.0, write=2.0, pool=2.0),
            limits=httpx.Limits(max_connections=2000, max_keepalive_connections=600),
            follow_redirects=True,
            http2=False,
            verify=False,
            trust_env=False,
        )
        while True:
            url = self.r.blpop('urls', timeout=2)
            if url is None:
                continue
            else:
                _, url = url
                url = Url(**json.loads(url))

            try:
                a = client.head(url.url)
                if url.status == 'DOWN':
                    self.r.rpush('tg_messages', json.dumps((url.url, None, "UP")))

                with self.lock:
                    self.stats['success'] += 1

            except httpx.ReadTimeout as e:
                if url.status == 'UP': self.r.rpush('tg_messages', json.dumps((str(e.request.url), str(e), "DOWN")))
                with self.lock:
                    self.stats['read_timeout'] += 1

            except httpx.ReadError as e:
                if url.status == 'UP': self.r.rpush('tg_messages', json.dumps((str(e.request.url), str(e), "DOWN")))
                with self.lock:
                    self.stats['read_error'] += 1

            except httpx.ConnectError as e:
                if url.status == 'UP': self.r.rpush('tg_messages', json.dumps((str(e.request.url), str(e), "DOWN")))
                with self.lock:
                    self.stats['connect_error'] += 1

            except httpx.ConnectTimeout as e:
                if url.status == 'UP': self.r.rpush('tg_messages', json.dumps((str(e.request.url), str(e), "DOWN")))
                with self.lock:
                    self.stats['connect_timeout'] += 1

            except httpx.PoolTimeout as e:
                if url.status == 'UP': self.r.rpush('tg_messages', json.dumps((str(e.request.url), str(e), "DOWN")))
                with self.lock:
                    self.stats['pool_timeout'] += 1

            except httpx.RemoteProtocolError as e:
                if url.status == 'UP': self.r.rpush('tg_messages', json.dumps((str(e.request.url), str(e), "DOWN")))
                with self.lock:
                    self.stats['remote_protocol'] += 1

            except httpx.TooManyRedirects as e:
                if url.status == 'UP': self.r.rpush('tg_messages', json.dumps((str(e.request.url), str(e), "DOWN")))
                with self.lock:
                    self.stats['pool_timeout'] += 1

            finally:
                with self.lock:
                    self.stats['total'] += 1
                    total = self.stats['total']
                    if total % 100 == 0:
                        print(self.stats)

    def start_workers(self):
        for _ in range(self.num_threads):
            t = threading.Thread(target=self.worker)
            t.start()
            self.threads.append(t)

        for t in self.threads:
            t.join()


entity = ClientWorker()
