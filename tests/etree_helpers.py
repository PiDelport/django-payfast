"""
Test helpers: ElementTree parsing.
"""
from typing import Union, Optional  # noqa: F401
from xml.etree.ElementTree import Element, ElementTree


def text_collapsed(element):  # type: (Element) -> str
    """
    Element's text with whitespace collapsed.
    """
    chunks = (s.strip() for s in element.itertext())
    return ' '.join(s for s in chunks if s)


def text_lines(element):  # type: (Element) -> str
    """
    Element's text with lines preserved.
    """
    raw = ''.join(element.itertext())
    # We're probably not interested in outer empty lines.
    outer_stripped = raw.strip()
    # Strip each line.
    # Append newlines on all lines, including the last,
    # to ease comparison with dedent().
    stripped_linewise = ''.join(
        line.strip() + '\n'
        for line in outer_stripped.splitlines()
    )
    return stripped_linewise


_Element = Union[ElementTree, Element]


def find_id_maybe(base, id):  # type: (_Element, str) -> Optional[Element]
    """
    Return the child element with the given id, or None.
    """
    assert id.replace('-', '').isalnum(), id
    matches = base.findall('.//*[@id="{}"]'.format(id))
    if 0 == len(matches):
        return None
    elif 1 == len(matches):
        [match] = matches
        return match
    else:
        raise ValueError(
            'Found {} matching elements with id {!r}'.format(len(matches), id),
            matches,
        )


def find_id(base, id):  # type: (_Element, str) -> Element
    """
    Return the child element with the given id.

    :raise ValueError: If not found.
    """
    match = find_id_maybe(base, id)
    if match is None:
        raise ValueError('Element with id {!r} not found'.format(id))
    else:
        return match
