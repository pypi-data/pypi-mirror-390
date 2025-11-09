import httpx
from json import dumps, loads, JSONDecodeError
from random import choices
from .Encoder import encoderjson
from .ErrorRubika import ErrorRubika
from .GetDataMethod import GetDataMethod
from .GtM import defaultapi


def SendRequests(plat: str, js: dict, OrginalAuth: str = None, auth: str = None, key: str = None, api_version: str = "6"):
    enc = encoderjson(auth, key)
    Enc = encoderjson(OrginalAuth, key)
    servers = GetDataMethod(target=defaultapi, args=()).show()
    payload = {
        "api_version": api_version,
        "auth": OrginalAuth if plat == "web" else auth,
        "data_enc": (enc if plat == "web" else Enc).encrypt(dumps(js)),
        "sign": enc.makeSignFromData((enc if plat == "web" else Enc).encrypt(dumps(js))),
    }
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if plat == "web":headers["Referer"] = "https://web.rubika.ir/"
    with httpx.Client(http2=False, timeout=20.0) as client:
        try:
            response = client.post(servers, json=payload, headers=headers)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:raise RuntimeError(f"HTTP Error: {e}")
def logger_andector(auths: str, js: dict):
    servers = defaultapi()
    enc = encoderjson(auth=auths)
    payload = {
        "api_version": "6",
        "tmp_session": auths,
        "data_enc": enc.encrypt(dumps(js)),
    }
    with httpx.Client(http2=False, timeout=20.0) as client:
        response = client.post(servers, json=payload)
        response.raise_for_status()
        return response.text

class Perager_postishon:
    def __init__(self, plat: str = None, OrginalAuth: str = None, auth: str = None, keyAccount: str = None):
        self.Plat = plat
        self.Auth = auth
        self.OrginalAuth = OrginalAuth
        self.keyAccount = keyAccount
        self.enc = None
        if keyAccount:
            self.enc = encoderjson(auth if plat == "web" else OrginalAuth, keyAccount)

    def methodsRubika(self, types: str, methode: str, indata: dict, wn: dict = None, downloads: list = None, server: str = None, podata: bytes = None, header: dict = None):
        inData = {"method": methode, "input": indata, "client": wn}

        try:
            if types == "json":
                response_text = SendRequests(
                    plat=self.Plat,
                    js=inData,
                    OrginalAuth=self.OrginalAuth,
                    auth=self.Auth,
                    key=self.keyAccount,
                )
                data_enc = loads(response_text).get("data_enc")
                sendJS = loads(self.enc.decrypt(data_enc))

                if sendJS.get("status") != "OK":
                    err = ErrorRubika(sendJS)
                    if err.Error in ["re", "ra"]:
                        return err.state
                return sendJS
            elif types == "login":
                authrnd = encoderjson.changeAuthType("".join(choices("abcdefghijklmnopqrstuvwxyz", k=32)))
                self.enc = encoderjson(auth=authrnd)
                response_text = logger_andector(authrnd, inData)
                data_enc = loads(response_text).get("data_enc")
                sendLOGIN = loads(self.enc.decrypt(data_enc))

                if sendLOGIN.get("status") != "OK":
                    err = ErrorRubika(sendLOGIN)
                    if err.Error in ["re", "ra"]:
                        return err.state
                return sendLOGIN
        except JSONDecodeError:
            raise RuntimeError("Invalid JSON response.")
        except httpx.HTTPError as e:
            raise RuntimeError(f"HTTPX error: {e}")
