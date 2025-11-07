from pydantic import BaseModel, Field
import uuid

from my_utilities.jwt_handler.exc import (
    IncorrectTokenError,
    TTLTokenExpiredError,
    UtilsJWTException,
    WrongTypeToken,
    UnknownError,
)
from my_utilities.singleton import SingletonMeta
import jwt
import time
from typing import Any

DEFAULT_TTL_ACCESS_TOKEN = 600
DEFAULT_TTL_REFRESH_TOKEN = 1209600


class JWTHandlerConfig(BaseModel):
    ttl_access_token: int = Field(
        DEFAULT_TTL_ACCESS_TOKEN, description="How to long live access token"
    )
    ttl_refresh_token: int = Field(
        DEFAULT_TTL_REFRESH_TOKEN, description="How to long live refresh token"
    )
    secret: str = Field(str(uuid.uuid4()), description="Secret jwt tokens")
    algorithm: str = Field("HS256", description="Algorithm encoding jwt tokens")
    user_identifier_in_user_data: str = Field(
        "id",
        description="Path in dictionary data to user identifier by keys."
        " Deep separate by keys. "
        "for dictionary: {'data':{'user':{'id': int, `some data`: `some value`}}}"
        "value: `data.user.id` ",
    )
    leeway: float = 5


class JWTAuthHandler(metaclass=SingletonMeta):
    _access_token_key = "access_token"
    _refresh_token_key = "refresh_token"
    _key_token_type = "token_type"
    _subject_key = "sub"

    def __init__(
        self,
        config: JWTHandlerConfig | None = None,
    ):  # pragma: no cover
        self._config = config or JWTHandlerConfig()
        self._internal_keys_payload = list()  # type: list[str]
        self._internal_keys_header = list()  # type: list[str]

    def _encode(
        self,
        subject: str,
        token_type: str,
        payload: dict[str, Any] | None = None,
        expires_in: int | None = None,
        header: dict[str, Any] | None = None,
    ) -> str:
        tmp_data = {
            self._subject_key: subject,
            "iat": int(time.time()),
            "uuid": str(uuid.uuid4()),
        }
        if expires_in > 0:
            tmp_data["exp"] = int(time.time()) + expires_in
        if not self._internal_keys_payload:
            self._internal_keys_payload.extend(tmp_data.keys())
        tmp_header = {self._key_token_type: token_type}
        if not self._internal_keys_header:
            self._internal_keys_header = [self._key_token_type, "alg", "typ"]

        if payload:
            tmp_data.update(payload)
        if header:
            tmp_header.update(header)

        return jwt.encode(  # type: ignore
            payload=tmp_data,
            key=self._config.secret,
            algorithm=self._config.algorithm,
            headers=tmp_header,
        )

    def _decode(
        self,
        token: str,
        verify: bool = True,
        options: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        if not options:
            options = dict()
        options.setdefault("verify_signature", verify)
        result = jwt.decode_complete(
            jwt=token,
            key=self._config.secret,
            algorithms=[
                self._config.algorithm,
            ],
            verify=verify,
            options=options,
            leeway=self._config.leeway,
        )
        return result.get("header", dict()), result.get("payload", dict())

    def get_tokens(
        self,
        user_id: str,
        payload: dict[str, Any] | None = None,
        header: dict[str, Any] | None = None,
        is_add_expired: bool = True,
    ) -> tuple[str, str]:
        at = self._encode(
            subject=str(user_id),
            token_type=self._access_token_key,
            payload=payload,
            expires_in=self._config.ttl_access_token if is_add_expired else 0,
            header=header,
        )
        rt = self._encode(
            subject=str(user_id),
            token_type=self._refresh_token_key,
            payload=payload,
            expires_in=self._config.ttl_refresh_token if is_add_expired else 0,
            header=header,
        )
        return at, rt

    def verify_token(
        self,
        token: str,
        is_access_token: bool = True,
        validate_exp: bool = True,
        verify: bool = True,
    ) -> tuple[str | None, dict[str, Any] | None, dict[str, Any] | None]:
        """
        Method for verify token

        :param token:
        :param is_access_token:
        :param validate_exp:
        :param verify:
        :exception:
        """
        options = dict(
            verify_exp=validate_exp,
            verify_signature=verify,
        )
        current_token = (
            self._access_token_key if is_access_token else self._refresh_token_key
        )

        try:
            header, payload = self._decode(token=token, verify=verify, options=options)
            if header.get(self._key_token_type, "unknown") != current_token:
                raise WrongTypeToken()
            return (
                payload.get(self._subject_key),
                self._remove_keys(header, self._internal_keys_header),
                self._remove_keys(
                    payload,
                    self._internal_keys_payload,
                ),
            )
        except (jwt.DecodeError, jwt.InvalidSignatureError) as exc:
            raise IncorrectTokenError() from exc
        except jwt.ExpiredSignatureError as exc:
            raise TTLTokenExpiredError() from exc
        except UtilsJWTException as exc:
            raise exc
        except Exception as exc:
            raise UnknownError() from exc

    @staticmethod
    def _remove_keys(
        data: dict[str, Any], list_keys: list[str], reverse: bool = False
    ) -> dict[str, Any] | None:
        if reverse:
            keys_to_remove = [key for key in data.keys() if key not in list_keys]
        else:
            keys_to_remove = list_keys
        for key in keys_to_remove:
            if key in data:
                data.pop(key)
        if not data:
            return None
        return data

    def get_subject(self, token: str) -> str | None:
        try:
            data = self._decode(token=token, verify=False)[1].get(
                self._subject_key, None
            )
            if data:
                return str(data)
        except Exception:
            pass
        return None
