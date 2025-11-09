from random import choices


class Inject_Device:
    @staticmethod
    def _generate_device(
        app_version: str,
        device_model: str,
        system_version: str,
        token_type: str,
        token: str = "",
        lang_code: str = "fa",
        is_multi_account: bool = False,
    ) -> dict:
        return {
            "app_version": app_version,
            "device_hash": "".join(choices("0123456789", k=26)),
            "device_model": device_model,
            "is_multi_account": is_multi_account,
            "lang_code": lang_code,
            "system_version": system_version,
            "token": token,
            "token_type": token_type,
        }
    DeviceAndroid = _generate_device.__func__(
        app_version="MA_3.0.7",
        device_model="rulog",
        system_version="SDK 28",
        token_type="Firebase",
    )
    DeviceWeb = _generate_device.__func__(
        app_version="WB_4.3.3",
        device_model="rulog",
        system_version="Windows 11",
        token_type="Web",
    )
    AndroidRegister = _generate_device.__func__(
        app_version="MA_3.0.7",
        device_model="rulog",
        system_version="SDK 28",
        token_type="Firebase",
    )
    WebRegister = _generate_device.__func__(
        app_version="WB_4.4.20",
        device_model="chrom",
        system_version="Windows 10",
        token_type="Web",
    )