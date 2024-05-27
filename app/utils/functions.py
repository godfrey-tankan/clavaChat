import json
try:
	from urllib.parse import urlencode
	from urllib.request import build_opener, Request, HTTPHandler
	from urllib.error import HTTPError, URLError
	from urllib.request import build_opener, Request, HTTPHandler, HTTPError, URLError
except ImportError:
	pass
else:

    def request():
        url = "https://eu-test.oppwa.com/v1/checkouts"
        data = {
            'entityId' : '8a8294174b7ecb28014b9699220015ca',
            'amount' : '92.00',
            'currency' : 'EUR',
            'paymentType' : 'DB'
        }
        try:
            opener = build_opener(HTTPHandler)
            request = Request(url, data=urlencode(data).encode('utf-8'))
            request.add_header('Authorization', 'Bearer OGE4Mjk0MTc0YjdlY2IyODAxNGI5Njk5MjIwMDE1Y2N8c3k2S0pzVDg=')
            request.get_method = lambda: 'POST'
            response = opener.open(request)
            return json.loads(response.read());
        except HTTPError as e:
            return json.loads(e.read());
        except URLError as e:
            return e.reason;

    responseData = request();
    print(responseData);