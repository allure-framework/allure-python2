from pytest_bdd import scenario


@scenario("attachments_features\\attachment_in_step.feature", "Attachment in Given")
def test_given_with_attachments():
    pass


@scenario("attachments_features\\attachment_in_step.feature", "Attachment in When")
def test_when_with_attachments():
    pass


@scenario("attachments_features\\attachment_in_step.feature", "Attachment in Then")
def test_then_with_attachments():
    pass


@scenario("attachments_features\\attachment_in_exception_step.feature", "Attachment and exception in step")
def test_step_with_attachments_and_exception():
    pass


@scenario("attachments_features\\attachment_in_many_steps.feature", "Attachment in many steps")
def test_attachment_in_many_steps():
    pass


@scenario("attachments_features\\attachment_in_failed_step.feature", "Attachment in failed step")
def test_failed_step_with_attachment():
    pass


@scenario("attachments_features\\attachment_in_called_fixture.feature", "Attachment in called fixture")
def test_attachment_in_called_fixture():
    pass


@scenario("attachments_features\\attachment_in_step-fixture.feature",
          "attachment in a step, that is also a fixture")
def test_attachment_in_step_fixture():
    pass
