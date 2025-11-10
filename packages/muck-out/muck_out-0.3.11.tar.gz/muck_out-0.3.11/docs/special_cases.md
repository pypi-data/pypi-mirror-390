# Special cases

Here, we document activities that have caused special behavior to be implemented.
We note that code blocks involving `>>>` are run as doctests.

??? abstract "Hidden imports"
  
    ```python
    >>> from muck_out.process import normalize_activity, normalize_object
    >>> from muck_out.testing import load_asset
    >>> hubzilla_add = load_asset("hubzilla_add")
    >>> peertube_video = load_asset("peertube_video")
    >>> comments_page = load_asset("comments_page")

    ```


## Handling recipients

### Mastodon like

Mastodon sends like activities without recipients, i.e. no `to` property.
This leads would lead to the following behavior

```python
>>> mastodon_like = {
...     "@context": "https://www.w3.org/ns/activitystreams",
...     "id": "https://mastodon.social/users/the_milkman#likes/251507741",
...     "type": "Like",
...     "actor": "https://mastodon.social/users/the_milkman",
...     "object": "https://dev.bovine.social/html_display/object/019"
... }
>>> normalize_activity(mastodon_like)
Traceback (most recent call last):
...
pydantic_core._pydantic_core.ValidationError: 1 validation error for Activity
to
  List should have at least 1 item after validation, not 0 [type=too_short, input_value=[], input_type=list]
    For further information visit https://errors.pydantic.dev/2.11/v/too_short
```

In order to work around this, the actor id processing the activity can be passed:

```python
>>> mastodon_like = {
...     "@context": "https://www.w3.org/ns/activitystreams",
...     "id": "https://mastodon.social/users/the_milkman#likes/251507741",
...     "type": "Like",
...     "actor": "https://mastodon.social/users/the_milkman",
...     "object": "https://dev.bovine.social/html_display/object/019"
... }
>>> result = normalize_activity(mastodon_like,
...      actor_id="https://dev.bovine.social/actor/ABC")
>>> print(result.model_dump_json(indent=2, exclude_none=True))
{
  "@context": [
    "https://www.w3.org/ns/activitystreams"
  ],
  "id": "https://mastodon.social/users/the_milkman#likes/251507741",
  "to": [
    "https://dev.bovine.social/actor/ABC"
  ],
  "cc": [],
  "type": "Like",
  "actor": "https://mastodon.social/users/the_milkman",
  "object": "https://dev.bovine.social/html_display/object/019"
}

```

### Hubzilla Add

The issue addressed here are missing recipients

??? info "the activity"
    [:material-download: Download](./assets/hubzilla_add.json)

    ```json linenums="1"
    --8<-- "docs/assets/hubzilla_add.json"
    ```

??? example "processing in muck_out"
    ```python

    >>> result = normalize_activity(hubzilla_add,
    ...      actor_id="https://dev.bovine.social/actor/ABC")
    >>> result.field_context = []
    >>> print(result.model_dump_json(indent=2, exclude_none=True))
    {
      "@context": [],
      "id": "https://zotum.net/activity/72598b50-025c-46fc-ba62-3896a86b7fd0",
      "to": [
        "https://dev.bovine.social/actor/ABC"
      ],
      "cc": [],
      "published": "2025-10-02T08:49:49Z",
      "type": "Add",
      "actor": "https://zotum.net/channel/fentiger",
      "object": "https://macaw.social/users/andypiper#likes/464620",
      "target": "https://zotum.net/conversation/0c47b0fa-4495-4c22-8a1b-508e32300ee9"
    }
    
    ```


## Handling content format

### Peertube Video

The object has `mediaType = text/markdown`. This is processed by
muck_out.

!!! warning
    This requires installing markdown, e.g. `pip install muck_out[markdown]`.

??? info "the object"
    [:material-download: Download](./assets/peertube_video.json)

    ```json linenums="1"
    --8<-- "docs/assets/peertube_video.json"
    ```

```python
>>> peertube_video["content"].split("\n")
  ["The Fediverse has a different problem with algorithms: They're not very good.\r", '\r', 'Interviews:\r', 
  'Dawn Walker: [@dawn@cosocial.ca](https://cosocial.ca/@dawn)\r', 
  'Julian Lam: [@julian@community.nodebb.org](https://community.nodebb.org/user/julian)\r',
  'Anuj Ahooja: [@quillmatiq@mastodon.social](https://mastodon.social/@quillmatiq)\r',
  'Johannes Ernst: [@j12t@j12t.social](https://j12t.social/@j12t)\r',
  'Daniel Supernault: [@dansup@mastodon.social](https://mastodon.social/@dansup)']

>>> result = normalize_object(peertube_video)
>>> result.content.split("\n")
  ["<p>The Fediverse has a different problem with algorithms: They're not very good.</p>", '<p>Interviews:',
  'Dawn Walker: <a href="https://cosocial.ca/@dawn" rel="noopener noreferrer">@dawn@cosocial.ca</a>',
  'Julian Lam: <a href="https://community.nodebb.org/user/julian" rel="noopener noreferrer">@julian@community.nodebb.org</a>',
  'Anuj Ahooja: <a href="https://mastodon.social/@quillmatiq" rel="noopener noreferrer">@quillmatiq@mastodon.social</a>',
  'Johannes Ernst: <a href="https://j12t.social/@j12t" rel="noopener noreferrer">@j12t@j12t.social</a>',
  'Daniel Supernault: <a href="https://mastodon.social/@dansup" rel="noopener noreferrer">@dansup@mastodon.social</a></p>']


```

## No content

### Comments Page

Objects with one of the properties `content`, `name`, or `summary`
should be valid.

??? info "the object"
    [:material-download: Download](./assets/comments_page.json)

    ```json linenums="1"
    --8<-- "docs/assets/comments_page.json"
    ```

```python
>>> result = normalize_object(comments_page)
>>> comments_page["name"] = None
>>> normalize_object(comments_page)
Traceback (most recent call last):
...
ValueError: At least one of the properties content, summary, or name should be set

```