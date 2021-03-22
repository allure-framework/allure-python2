class PyFileBuilder:

    def __init__(self, name):
        self._import_line = None
        self._file_funcs = []
        self.name = name

    def add_imports(self, *modules_names):
        import_list = []

        for module in modules_names:
            import_list.append("import " + module)

        if len(import_list) != 0:
            self._import_line = "\n".join(import_list)

    def add_func(self, str_func):
        self._file_funcs.append(str_func)

    def get_content(self):
        if len(self._file_funcs) == 0:
            raise Exception("There are no functions in this file")

        content = "\n\n\n".join(self._file_funcs)

        if self._import_line is not None:
            content = self._import_line + "\n\n\n" + content

        return content
