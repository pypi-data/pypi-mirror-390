from typing import Any

from my_utilities.cache import CacheEngine
from my_utilities.jwt_handler.exc import UtilsJWTException, NotValidSession
from my_utilities.jwt_handler.jwt_handler import JWTHandlerConfig, JWTAuthHandler


class AuthCacheHandler:
    _key_template_access = "user_{id}_access_tokens"
    _key_template_refresh = "user_{id}_refresh_tokens"

    def __init__(
        self,
        config: JWTHandlerConfig,
        cache: CacheEngine | None = None,
        is_multy_session: bool = True,
    ):
        self._handler = JWTAuthHandler(config=config)
        self._cache = cache
        self._config = config
        self._is_multy_session = is_multy_session

    def get_pair_tokens(
        self,
        user_id: str,
        payload: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        is_add_expired: bool = True,
    ) -> tuple[str, str]:
        access_token, refresh_token = self._handler.get_tokens(
            user_id=user_id,
            payload=payload,
            header=headers,
            is_add_expired=is_add_expired,
        )
        if self._cache:
            if self._is_multy_session:
                self._cache.lpush(
                    key=self._key_template_access.format(id=user_id),
                    value=access_token,
                    # ttl=max(self._config.ttl_access_token -1, 0)
                )
                self._cache.lpush(
                    key=self._key_template_refresh.format(id=user_id),
                    value=refresh_token,
                    # ttl=max(self._config.ttl_refresh_token - 1, 0)
                )
            else:
                old_at_token = self._cache.get(
                    self._key_template_access.format(id=user_id)
                )
                old_rt_token = self._cache.get(
                    self._key_template_refresh.format(id=user_id)
                )
                if old_at_token:
                    self._cache.delete(old_at_token)
                if old_rt_token:
                    self._cache.delete(old_rt_token)
                self._cache.set(
                    key=self._key_template_access.format(id=user_id),
                    value=access_token,
                    ttl=max(self._config.ttl_access_token, 0),
                )
                self._cache.set(
                    key=self._key_template_refresh.format(id=user_id),
                    value=refresh_token,
                    ttl=max(self._config.ttl_refresh_token, 0),
                )
            self._cache.set(
                key=access_token,
                value=refresh_token,
                ttl=max(self._config.ttl_access_token, 0),
            )
            self._cache.set(
                key=refresh_token,
                value=access_token,
                ttl=max(self._config.ttl_refresh_token, 0),
            )
        return access_token, refresh_token

    def update_user_data(
        self,
        token: str,
        is_access_token: bool = True,
        new_payload: dict[str, Any] | None = None,
        new_header: dict[str, Any] | None = None,
    ) -> tuple[str, str]:
        try:
            (
                user_id,
                header_to_upload,
                payload_to_upload,
            ) = self.verify_token(token=token, is_access_token=is_access_token)
            if new_header is not None:
                header_to_upload = new_header
            if new_payload is not None:
                payload_to_upload = new_payload
            if self._cache:
                if is_access_token:
                    at = token
                    rt = self._cache.get(token)
                else:
                    at = self._cache.get(token)
                    rt = token
                if self._cache:
                    self._cache.delete(at)
                    self._cache.delete(rt)
                    if self._is_multy_session:
                        self._cache.lrem(
                            key=self._key_template_refresh.format(id=user_id), val=rt
                        )
                        self._cache.lrem(
                            key=self._key_template_access.format(id=user_id), val=at
                        )
                    else:
                        self._cache.delete(
                            key=self._key_template_refresh.format(id=user_id),
                        )
                        self._cache.delete(
                            key=self._key_template_access.format(id=user_id),
                        )
            return self.get_pair_tokens(
                user_id=user_id, payload=payload_to_upload, headers=header_to_upload
            )
        except UtilsJWTException as exc:
            raise exc

    def verify_token(
        self,
        token: str,
        is_access_token: bool = True,
        verify: bool = True,
        validate_exp: bool = True,
    ) -> tuple[str, dict[str, Any] | None, dict[str, Any] | None]:
        res = self._handler.verify_token(
            token=token,
            is_access_token=is_access_token,
            verify=verify,
            validate_exp=validate_exp,
        )
        if self._cache:
            pair_token = self._cache.get(token)
            if pair_token is None:
                raise NotValidSession()
        return res

    def delete_pair_tokens(self, token: str, is_access_token: bool = True) -> None:

        user_id, _, _ = self.verify_token(token, is_access_token)
        if not self._cache:
            return
        pair_token = self._cache.get(token)
        if is_access_token:
            at = token
            rt = pair_token
        else:
            at = pair_token
            rt = token
        if self._is_multy_session:
            self._cache.lrem(key=self._key_template_refresh.format(id=user_id), val=rt)
            self._cache.lrem(key=self._key_template_access.format(id=user_id), val=at)
            # self._cache.delete(rt)
            # self._cache.delete(at)
        else:
            self._cache.delete(
                key=self._key_template_refresh.format(id=user_id),
            )
            self._cache.delete(
                key=self._key_template_access.format(id=user_id),
            )
        self._cache.delete(at)
        self._cache.delete(rt)

        pass

    def clear_other_sessions(self, token: str, is_access_token: bool = True) -> None:
        if not self._is_multy_session:
            return
        user_id, _, _ = self.verify_token(token, is_access_token)
        if not self._cache:
            return
        pair_token = self._cache.get(token)
        key_rt = self._key_template_refresh.format(id=user_id)
        key_at = self._key_template_access.format(id=user_id)
        for item in self._cache.lrange(key_at):
            if item == pair_token or item == token:
                continue
            else:
                self._cache.lrem(key_at, item)
                tmp_pair_token = self._cache.get(item)
                self._cache.lrem(key_rt, tmp_pair_token)
                self._cache.delete(item)
                self._cache.delete(pair_token)

        pass

    def refresh_pair_tokens(self, refresh_token: str) -> tuple[str, str]:
        return self.update_user_data(refresh_token, is_access_token=False)
