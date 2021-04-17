import pytest
from domain import lib
from domain.model.document.link import Link, LinkPreview
from tests.domain.model.document.implementations import LinkSourceImplementation, LinkTargetImplementation, \
    LinkNodeImplementation


@pytest.fixture
def link_id():
    return lib.Id()


@pytest.fixture(params=[LinkSourceImplementation, LinkNodeImplementation])
def source(request):
    return request.param([], [], LinkPreview("source", None))


@pytest.fixture(params=[LinkTargetImplementation, LinkNodeImplementation])
def target(request):
    return request.param([], [], LinkPreview("target", None))


@pytest.fixture
def link(link_id, source, content_location, target):
    link = Link(link_id, source, content_location, target)
    source.register_link(link)
    target.register_backlink(link)
    return link


@pytest.fixture
def link_without_target(link_id, source, content_location):
    link = Link(link_id, source, content_location, None)
    source.register_link(link)
    return link


def test_link_init(link, link_id, source, content_location, target):
    assert link.id == link_id
    assert link.source == source
    assert link.source_preview == source.link_preview
    assert link.location == content_location
    assert link.target == target
    assert link.target_preview == target.link_preview
    assert not link.broken
    assert not link.deleted
    assert link in source.links
    assert link in target.backlinks


def test_link_creation(source, content_location, target):
    source_links_before = [*source.links]
    target_backlinks_before = [*target.backlinks]
    link = Link.create(source, content_location, target)
    assert link in source.links
    assert link in target.backlinks
    assert link not in source_links_before
    assert link not in target_backlinks_before


def test_link_deletion(link, source, target):
    link.delete()
    assert link.deleted
    assert link not in source.links
    assert link not in target.backlinks


def test_link_deleted_when_source_deleted(link, source):
    source.delete()
    assert link.deleted


def test_link_broken_without_target(link_without_target):
    assert link_without_target.broken


def test_link_broken_when_target_deleted(link, target):
    target.delete()
    assert link.broken


def test_link_source_preview_update(link, source):
    source.link_preview.text = "updated"
    assert link.source_preview.text == "updated"


def test_link_target_preview_update(link, target):
    target.link_preview.text = "updated"
    assert link.target_preview.text == "updated"
