import os.path
import os


class AttachmentWorker:

    def __init__(self, test_result, item):
        self.test_result = test_result
        self.attachments_dir = AttachmentWorker.get_path_to_attachments(item)

    @staticmethod
    def get_path_to_attachments(item):
        allure_dir = os.path.normpath(
            item.config.invocation_params.args[0].split('=')[1])
        if os.path.isabs(allure_dir):
            return allure_dir
        else:
            project_dir = str(item.config.invocation_params.dir)
            return os.path.join(project_dir, allure_dir.lstrip("\\"))

    def delete_duplicates(self):
        if len(self.test_result.attachments) == 0:
            return

        for step in self.test_result.steps:
            for attach in step.attachments:
                to_delete = self._find_duplicate(attach)
                if to_delete is not None:
                    self.test_result.attachments.remove(to_delete)
                os.remove(os.path.join(self.attachments_dir, to_delete.source))

    def _find_duplicate(self, attachment_from_step):
        for attachment in self.test_result.attachments:
            if self._are_attachments_equal(attachment, attachment_from_step):
                return attachment

        return None

    def _are_attachments_equal(self, first, second):
        first_file = open(os.path.join(self.attachments_dir, first.source), 'br')
        first_content = first_file.read()
        first_file.close()

        second_file = open(os.path.join(self.attachments_dir, second.source), 'br')
        second_content = second_file.read()
        second_file.close()

        return \
            first.name == second.name and \
            first.type == second.type and \
            first_content == second_content
