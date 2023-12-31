from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class UserRoleEnum(str, Enum):
    regulator = "regulator"
    verified_artist = "verified_artist"
    moderator = "moderator"
    editor = "editor"
    mediator = "mediator"
    contributor = "contributor"
    staff = "staff"


class GeniusBaseModel(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True, extra="allow")
    genius_id: str = Field(alias="id")
    api_path: str
    url: str

    def __repr__(self):
        return f"{self.__class__.__name__}({{}}, genius_id='{self.genius_id}')"

    def __str__(self):
        return self.__repr__()

    def __hash__(self):
        return hash(self.__class__.__name__ + str(id))


class Annotation(GeniusBaseModel):
    body: dict
    share_url: str
    state: str
    verified: bool
    authors: list[Author]
    cosigned_by: list[dict]
    verified_by: User | None

    def __repr__(self):
        return super().__repr__().format(f"state='{self.state}'")


class Author(BaseModel):
    attribution: float
    pinned_role: str | None
    user: User

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__()})"


class Referent(GeniusBaseModel):
    referent_type: str = Field(alias="_type")
    fragment: str
    annotator_id: str
    annotator_login: str
    classification: str
    referent_range: dict = Field(alias="range")
    song_id: str
    verified_annotator_ids: list
    annotatable: AnnotatableSong | WebPage
    annotations: list[Annotation]

    def __repr__(self):
        return super().__repr__().format(f"fragment='{self.fragment}'")


class Artist(GeniusBaseModel):
    image_url: str
    is_verified: bool
    header_image_url: str
    name: str

    def __repr__(self):
        return super().__repr__().format(f"name='{self.name}'")


class Performance(BaseModel):
    label: str
    artists: list[Artist]

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__()})"


class Album(GeniusBaseModel):
    full_title: str
    cover_art_url: str
    artist: Artist

    def __repr__(self):
        return super().__repr__().format(f"full_title='{self.full_title}'")


class FullAlbum(Album, GeniusBaseModel):
    name: str
    release_date: str
    cover_arts: list[dict]
    description_annotation: dict
    song_performances: list[Performance]


class AnnotatableSong(GeniusBaseModel):
    client_timestamps: dict
    context: str
    image_url: str
    title: str
    annotatable_type: str = Field("type")

    def __repr__(self):
        return super().__repr__().format(f"title='{self.title}'")


class Song(GeniusBaseModel):
    """For Songs returned by /search or /artists/:id/songs"""

    title: str
    full_title: str
    artist_names: str
    header_image_url: str
    header_image_thumbnail_url: str
    song_art_image_url: str
    song_art_image_thumbnail_url: str
    release_date_components: dict | None = None
    release_date_for_display: str | None = None
    release_date_with_abbreviated_month_for_display: str | None = None
    stats: dict
    featured_artists: list[Artist]
    primary_artist: Artist

    def __repr__(self):
        return super().__repr__().format(f"full_title='{self.full_title}'")


class FullSong(Song, GeniusBaseModel):
    # /songs/<id> fields

    album: Album
    media: list[dict]
    producer_artists: list[Artist]
    writer_artists: list[Artist]
    custom_performances: list[Performance]
    song_relationships: list[dict]


class WebPage(GeniusBaseModel):
    title: str
    domain: str
    share_url: str
    normalized_url: str
    annotation_count: int

    def __repr__(self):
        return super().__repr__().format(f"title='{self.title}'")


class User(GeniusBaseModel):
    avatar: dict
    photo_url: str | None = None
    header_image_url: str
    custom_header_image_url: str | None = None
    iq: int | None = None
    iq_for_display: str | None = None
    login: str
    name: str
    about_me: dict | None = None
    followers_count: int | None = None
    followed_users_count: int | None = None
    human_readable_role_for_display: str | None = None
    role_for_display: UserRoleEnum | None
    roles_for_display: list[UserRoleEnum] | None = None
    artist: Artist | None = None
    current_user_metadata: dict
    stats: dict | None = None

    def __repr__(self):
        return super().__repr__().format(f"name='{self.name}', login='{self.login}'")


class Me(User, GeniusBaseModel):
    email: str
    unread_messages_count: int
    unread_groups_inbox_count: int
    unread_main_activity_inbox_count: int
    unread_newsfeed_inbox_count: int
