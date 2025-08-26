from datetime import UTC, datetime
from typing import Any

from discord.ext.commands import CooldownMapping

from ...exceptions import CooldownExceeded
from ...interfaces import BlockABC
from ...interpreter import Context
from ...util import split_at_substring_zero_depth


class CooldownBlock(BlockABC):
    """
    This block implements cooldowns for running a tag.

    The parameter requires two values: ``rate`` and ``per``, split by ``|`` such that
    the parameter looks like  ``rate|per``. ``rate`` specifies the number of times the
    tag can be used within ``per`` seconds.

    The payload requires a ``key`` value, which is used to store the cooldown. The key
    should be a unique string. For example, if a channel's ID is used as the key, the
    cooldown will apply to that channel. Using the same tag in a different channel will
    have a separate cooldown with the same ``rate`` and ``per`` values.

    The payload also supports an optional ``message`` value, which is displayed when
    the cooldown is exceeded. If provided, it must be split from the ``key`` by ``|``
    such that the payload is ``key|message``. If no message is provided, a default
    message is used. The cooldown message supports two placeholders: ``{key}`` and
    ``{retry_after}``.

    **Usage**: ``{cooldown(<rate>|<per>):<key>[|message]}``

    **Aliases**: ``cooldown``

    **Parameter**: ``rate`` (required), ``per`` (required)

    **Payload**: ``key`` (required), ``message`` (optional)

    **Examples**::

        {cooldown(1|10):{user(id)}}
        # If the tag user uses the tag more than once in 10 seconds:
        # The bucket for 741074175875088424 has reached its cooldown. Retry in 3.25 seconds.

        {cooldown(3|3):{channel(id)}|Slow down! This tag can only be used 3 times per 3 seconds per channel. Try again in **{retry_after}** seconds.}
        # If the tag is used more than 3 times in 3 seconds in a channel:
        # Slow down! This tag can only be used 3 times per 3 seconds per channel. Try again in **0.74** seconds.
    """

    requires_nonempty_parameter = True
    requires_nonempty_payload = True

    COOLDOWNS: dict[Any, CooldownMapping] = {}

    @classmethod
    def create_cooldown(cls, key: Any, rate: float, per: int) -> CooldownMapping:
        cooldown = CooldownMapping.from_cooldown(rate, per, lambda x: x)
        cls.COOLDOWNS[key] = cooldown
        return cooldown

    @property
    def _accepted_names(self) -> set[str]:
        return {"cooldown"}

    def process(self, ctx: Context) -> str | None:
        if (param := ctx.node.parameter) is None or param.strip() == "":
            return None
        elif (payload := ctx.node.payload) is None or payload.strip() == "":
            return None

        parsed_param = ctx.interpret_segment(param)
        ratio = split_at_substring_zero_depth(parsed_param, "|", max_split=1)
        if len(ratio) != 2:
            return None

        try:
            rate = float(ratio[0])
            per = int(ratio[1])
        except ValueError:
            return None

        parsed_payload = ctx.interpret_segment(payload)
        key_split = split_at_substring_zero_depth(parsed_payload, "|", max_split=1)
        if len(key_split) == 2:
            key = key_split[0]
            message = key_split[1]
        else:
            key = key_split[0]
            message = None

        if (cooldown_key := ctx.response.extra_kwargs.get("cooldown_key")) is None:
            cooldown_key = ctx.original_message

        if cooldown_key in self.COOLDOWNS:
            cooldown = self.COOLDOWNS[cooldown_key]
            # noinspection PyProtectedMember
            base = cooldown._cooldown
            if base is None or (rate, per) != (base.rate, base.per):
                cooldown = self.create_cooldown(cooldown_key, rate, per)
        else:
            cooldown = self.create_cooldown(cooldown_key, rate, per)

        current = int(datetime.now(tz=UTC).timestamp())
        bucket = cooldown.get_bucket(key, current)
        if bucket is None:
            return ""
        retry_after = bucket.update_rate_limit(current)

        if retry_after is None or retry_after == 0.0:
            return ""

        retry_after = round(retry_after, 2)
        if message is not None:
            message = message.replace("{key}", str(key)).replace(
                "{retry_after}",
                str(retry_after),
            )
        else:
            message = (
                f"The bucket for {key} has reached its cooldown. Retry in "
                f"{retry_after} seconds."
            )
        raise CooldownExceeded(message, bucket, key, retry_after)
