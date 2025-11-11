from logging import LogRecord
from logging.handlers import HTTPHandler
from ssl import SSLContext
from typing import List, Optional, Tuple


class HTTPHandlerCustomHeader(HTTPHandler):
    def __init__(
        self,
        host: str,
        url: str,
        method: str = "GET",
        secure: bool = True,  # noqa FBT001, FBT002
        header_key_value_pairs: Optional[List[Tuple[str, str]]] = None,
        context: Optional[SSLContext] = None,
    ) -> None:
        """Logging handler for HTTP requests with the possiblity to provide custom headers.

        :param host: https://my-host.com
        :param url: /path/to/endpoint
        :param method: HTTP verb, defaults to "GET"
        :param secure: HTTPS for True, HTTP for False, defaults to True
        :param header_key_value_pairs: _description_, defaults to None
        :param context: _description_, defaults to None
        """
        super().__init__(host=host, url=url, method=method, secure=secure, credentials=None, context=context)
        self.header_key_value_pairs = header_key_value_pairs if header_key_value_pairs else []

    def emit(self, record: LogRecord) -> None:
        """
        Emit a record.

        Send the record to the web server as a percent-encoded dictionary

        header_key_value_pairs represents arbitrary key value pairs which are put into the header
        """
        try:
            import urllib.parse  # noqa PLC0415

            host = self.host
            h = self.getConnection(host, self.secure)
            url = self.url
            data = urllib.parse.urlencode(self.mapLogRecord(record))
            if self.method == "GET":
                if url.find("?") >= 0:
                    sep = "&"
                else:
                    sep = "?"
                url = url + "%c%s" % (sep, data)  # noqa UP031
            h.putrequest(self.method, url)
            # support multiple hosts on one IP address...
            # need to strip optional :port from host, if present
            i = host.find(":")
            if i >= 0:
                host = host[:i]
            if self.method == "POST":
                h.putheader("Content-type", "application/x-www-form-urlencoded")
                h.putheader("Content-length", str(len(data)))
            for key, value in self.header_key_value_pairs:
                h.putheader(str(key), str(value))
            h.endheaders()
            if self.method == "POST":
                h.send(data.encode("utf-8"))
            h.getresponse()
        except Exception:
            self.handleError(record)
