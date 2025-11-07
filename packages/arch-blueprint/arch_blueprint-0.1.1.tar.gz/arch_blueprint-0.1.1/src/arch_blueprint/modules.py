from dataclasses import dataclass


@dataclass
class BlueprintModule:
    name: str
    dependencies: set[str]
    selected_modules: set[str]

    def get_namespace(self):
        return self.get_namespace_of_module(self.name)

    def find_dependencies_module_to_module_in_namespace(self):
        res = set()
        return res

        for dep in self.dependencies:
            for module in self.filter_modules:
                if dep.startswith(module) and module != self.name:
                    res.add(module)

        return res

    def find_dependencies_namespace_to_namespaces(self):
        res = set()

        for dep in self.dependencies:
            for selected_module in self.selected_modules:
                if selected_module in dep:
                    from_, to_ = self.extract_namespaces_with_same_depth(dep)
                    if from_ != to_:
                        res.add((from_,to_))

            # if (dep.startswith(module) and module != self.name
            #         and not self.is_same_namespace(module)):
            #     res.add(self.get_namespace_of_module(module))

        return res

    def is_same_namespace(self, other):
        namespace = self.get_namespace_of_module(other)
        return self.get_namespace() == namespace

    def get_namespace_of_module(self, module):
        namespace, _ = module.rsplit(".", maxsplit=1)
        return namespace

    def extract_namespaces_with_same_depth(self, module: str) -> tuple[str, str]:
        from_ = self.name.split(".")
        to_ = module.split(".")

        path_from = []
        path_to = []
        for first, second in zip(from_, to_):
            path_from.append(first)
            path_to.append(second)
            if first != second:
                break

        return ".".join(path_from), ".".join(path_to)