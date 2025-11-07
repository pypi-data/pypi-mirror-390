from typing import Dict, Optional
from msgspec import Struct, json, field
from .deltas.custom_type import Value 
from ..exception.errors import ParsingError

__all__ = ["User"]



GENDERS = {
    0: "unknown",
    1: "female",
    2: "male",
    3: "female",
    4: "male",
    5: "mixed",
    6: "neuter",
    7: "unknown",
    8: "female_plural",
    9: "male_plural",
    10: "neuter_plural",
    11: "unknown_plural",
    # For graphql requests
    "UNKNOWN": "unknown",
    "FEMALE": "female_singular",
    "MALE": "male_singular",
    "NEUTER": "neuter_singular",
}


# field values are set for msgspec to auto parse from fetched `Thread` info. 
class User(Struct, frozen=True, eq=False):
    """Represents a Facebook User."""
    id: str
    """Facebook `User`'s uid"""
    name: str
    """Facebook `User`'s name"""
    first_name: str = field(name="short_name", default="")
    "The first name of the `User`"
    username: str = ""
    """The username of the User"""
    gender: str = ""
    """Gender of the user."""
    url: Optional[str] = ""
    """Facebook profile url of the `User`"""
    is_friend: bool = field(name="is_viewer_friend", default=False)
    """Wether the Client account is friend with the `User`"""
    is_blocked: bool = field(name="is_message_blocked_by_viewer", default=False)
    """Wether the client blocked or blocked by the `User` """
    image: Optional[Value] = field(name="big_image_src", default=None)
    """The profile picture url of the `User`"""
    alternate_name: Optional[str] = None
    """The alternate name of the Facebook `User`"""







def extractVal(typ, obj):
    if typ is Value:
        if isinstance(obj, dict):
            return Value(next(iter(obj.values())))
        return Value()

def parse_user_graphql(payload)->Dict[str, User]:
    """Parses graphql responses that includes `User` info"""
    json_data = json.decode(payload)
    return {
        k: _parse_user(k,v) for k, v in json_data["payload"].items() 
        }


def _parse_user(k, v)->User:
    try:
        if v["id"] and v["url"]: # Check if user account deleted or deactivated id is 0
            return User(
                id=v["id"],
                name=v["name"],
                first_name=v["firstName"],
                username=v["vanity"],
                gender=GENDERS[v["gender"]],
                url=v["uri"],
                is_friend=v["is_friend"],
                is_blocked=v["is_blocked"],
                image=v["thumbSrc"],
                alternate_name=v["alternateName"]
                ) 
        else:
            return User(
                id=v["id"],
                name=v["name"],
                first_name=v["firstName"],
                username=v["vanity"] if "vanity" in v else "",
                gender=GENDERS["UNKNOWN"],
                url="",
                is_friend=False,
                is_blocked=False,
                )
    except KeyError as e:
        raise ParsingError(f"Failed to parse User ({k}). Couldn't get '{e.args[0]}' from  fetched User data.", original_exception=e)
    except Exception as e:
        raise ParsingError(f"Failed to parse User with Id: '{k}'", original_exception=e)
        
