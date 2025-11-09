from base64 import b64decode
from json import dump, loads
from re import findall
from .platform import Parts_Platform
from .Device import Inject_Device
from .Encoder import encoderjson
from .Error import ErrorMethod
from .PostData import Perager_postishon
from .RSA_ENC import deleteRSAset

from base64 import b64decode
from json import loads, dump
from re import findall

class Client:
    def __init__(self,password = None):
        self.password = password
    def register(self, platform: str, auths: str, keys: str) -> bool:
        if str(platform) in ("android",):
            keyAccount, Sh_account, Auth = deleteRSAset(keys), "".join(findall(r"\w{32}", auths)), encoderjson.changeAuthType("".join(findall(r"\w{32}", auths)))
            Keys = f"-----BEGIN RSA PRIVATE KEY-----\n{keyAccount}\n-----END RSA PRIVATE KEY-----"
        else:
            keyAccount, Sh_account, Auth = keys, "".join(findall(r"\w{32}", auths)), encoderjson.changeAuthType("".join(findall(r"\w{32}", auths)))
            Keys = loads(b64decode(keyAccount).decode('utf-8'))['d']
        method = Perager_postishon(
            plat=platform,
            OrginalAuth=Sh_account,
            auth=Auth,
            keyAccount=Keys
        )
        cli = Parts_Platform(platform).platform
        if platform == "web":
            return method.methodsRubika(
                'json',
                methode='registerDevice',
                indata=Inject_Device.WebRegister,
                wn=cli
            )
        else:
            return method.methodsRubika(
                'json',
                methode='registerDevice',
                indata=Inject_Device.AndroidRegister,
                wn=cli
            )



    def sendCode(self,platforms, numberphone: str, send_type: bool = False, password=None):
        """
        send_type: False -> 'SMS', True -> 'Internal'
        """
        cli = Parts_Platform(platforms).platform
        method = Perager_postishon()
        send_type_value = "Internal" if send_type else "SMS"

        print(numberphone)
        return method.methodsRubika(
            "login",
            methode="sendCode",
            indata={
                "phone_number": numberphone,
                "send_type": send_type_value,
                "pass_key": self.password,
            },
            wn=cli,
        )


    def signIn(self,platforms, numberphone: str, codehash, phone_code, save=None):
        publicKey, privateKey = encoderjson.rsaKeyGenerate()
        method = Perager_postishon()
        cli = Parts_Platform(platforms).platform
        if not (platforms and numberphone and codehash and phone_code):
            raise ErrorMethod("Enter the complete values ​​into the method")
        GetDataSignIn = method.methodsRubika(
            "login",
            methode="signIn",
            indata={
                "phone_number": numberphone,
                "phone_code_hash": codehash,
                "phone_code": phone_code,
                "public_key": publicKey,
                "private_key": privateKey,
            },
            wn=cli,
        )
        status = GetDataSignIn.get("data", {}).get("status")
        if status == "OK":
            data_account = dict(
                Auth=encoderjson.decryptRsaOaep(privateKey, GetDataSignIn.get("data").get("auth")),
                Key=privateKey,
            )
            if save is not None:
                with open(f"{save}.json", "a+") as f:
                    dump(data_account, f)
            return data_account

        if status == "CodeIsInvalid":
            raise ErrorMethod("Invalid Rubika login code")
        raise ErrorMethod(f"Unexpected signIn status: {status}")