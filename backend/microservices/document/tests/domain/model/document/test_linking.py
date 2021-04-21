def test_link_source_is_source_entity(link_from_link_source, link_source):
    assert link_from_link_source.source is link_source


def test_link_target_is_target_entity(link_from_link_source, link_target):
    assert link_from_link_source.target is link_target


def test_link_from_source_results_in_backlink_ref_on_target(link_from_link_source, link_target):
    # link is backlink
    assert link_from_link_source in link_target.backlinks
    assert link_from_link_source is link_target.get_backlink(link_from_link_source.id)


def test_deleting_the_source_of_a_link_deletes_the_link(link_from_link_source, link_source):
    link_source.delete()
    assert link_from_link_source.deleted


def test_deleting_the_target_of_a_link_makes_the_link_broken(link_from_link_source, link_target):
    link_target.delete()
    assert link_from_link_source.broken


def test_link_source_preview_is_the_link_preview_of_the_source(link_from_link_source, link_source):
    assert link_from_link_source.source_preview is link_source.link_preview


def test_link_target_preview_is_the_link_preview_of_the_target(link_from_link_source, link_target):
    assert link_from_link_source.target_preview is link_target.link_preview
