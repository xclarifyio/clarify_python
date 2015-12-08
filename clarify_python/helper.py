"""
Helper functions.
"""


def process_embed(embed_items=None,
                  embed_tracks=None,
                  embed_metadata=None,
                  embed_insights=None):
    """Returns an embed field value based on the parameters."""

    result = None

    embed = ''
    if embed_items:
        embed = 'items'
    if embed_tracks:
        if embed != '':
            embed += ','
        embed += 'tracks'
    if embed_metadata:
        if embed != '':
            embed += ','
        embed += 'metadata'
    if embed_insights:
        if embed != '':
            embed += ','
        embed += 'insights'

    if embed != '':
        result = embed

    return result


def process_embed_override(href_embed=None,
                           embed_items=None,
                           embed_tracks=None,
                           embed_metadata=None,
                           embed_insights=None):
    """Returns an embed field value based on the parameters."""
    # Our defaults are None, which are the API defaults.
    final_items = None
    final_tracks = None
    final_metadata = None
    final_insights = None

    # First, figure out what was embedded in the original href.
    # If any of the embeds are there, flip the final to True
    if href_embed:
        if 'items' in href_embed:
            final_items = True
        if 'tracks' in href_embed:
            final_tracks = True
        if 'metadata' in href_embed:
            final_metadata = True
        if 'insights' in href_embed:
            final_insights = True

    # Second, override the what we have.
    # None >> Do nothing
    # True >> Set to True
    # False >> Set to None
    if embed_items is not None:
        if embed_items is True:
            final_items = True
        else:
            final_items = None
    if embed_tracks is not None:
        if embed_tracks is True:
            final_tracks = True
        else:
            final_tracks = None
    if embed_metadata is not None:
        if embed_metadata is True:
            final_metadata = True
        else:
            final_metadata = None
    if embed_insights is not None:
        if embed_insights is True:
            final_insights = True
        else:
            final_insights = None

    return process_embed(embed_items=final_items,
                         embed_tracks=final_tracks,
                         embed_metadata=final_metadata,
                         embed_insights=final_insights)


def get_embedded_items(result_collection):
    """
    Given a result_collection (returned by a previous API call that
    returns a collection, like get_bundle_list() or search()), return a
    list of embedded items with each item in the returned list
    considered a result object.

    'result_collection' a JSON object returned by a previous API
    call. The parameter 'embed_items' must have been True when the
    result_collection was originally requested.May not be None.

    Returns a list, which may be empty if no embedded items were found.
    """

    # Argument error checking.
    assert result_collection is not None

    result = []

    embedded_objects = result_collection.get('_embedded')
    if embedded_objects is not None:
        # Handle being passed a non-collection gracefully.
        result = embedded_objects.get('items', result)

    return result


def get_item_hrefs(result_collection):
    """
    Given a result_collection (returned by a previous API call that
    returns a collection, like get_bundle_list() or search()), return a
    list of item hrefs.

    'result_collection' a JSON object returned by a previous API
    call.

    Returns a list, which may be empty if no items were found.
    """

    # Argument error checking.
    assert result_collection is not None

    result = []

    links = result_collection.get('_links')
    if links is not None:
        items = links.get('items')
        if items is not None:
            for item in items:
                result.append(item.get('href'))

    return result


def get_link_href(result_object, link_relation):
    """
    Given a result_object (returned by a previous API call), return
    the link href for a link relation.

    'result_object' a JSON object returned by a previous API call. May not
    be None.
    'link_relation' the link relation for which href is required.

    Returns None if the link does not exist.
    """

    # Argument error checking.
    assert result_object is not None

    result = None

    link = result_object['_links'].get(link_relation)
    if link:
        result = link.get('href')

    return result


def get_embedded(result_object, link_relation):
    """
    Given a result_object (returned by a previous API call), return
    the embedded object for link_relation.  The returned object can be
    treated as a result object in its own right.

    'result_object' a JSON object returned by a previous API call.
    The link relation of teh embedded object must have been specified
    when the result_object was originally requested. May not be None.
    'link_relation' the link relation for which href is required. May
    not be None.

    Returns None if the embedded object does not exist.
    """

    # Argument error checking.
    assert result_object is not None
    assert link_relation is not None

    result = None

    embedded_object = result_object['_embedded']
    if embedded_object:
        result = embedded_object.get(link_relation)

    return result
