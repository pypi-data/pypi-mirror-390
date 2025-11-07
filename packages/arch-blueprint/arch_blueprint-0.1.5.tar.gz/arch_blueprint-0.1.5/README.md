# Description

Generate modules import graph for python project. Using `plantuml` for render.

# Installation

```shell
pip install arch-blueprint
```

# Usage

Commands
```shell
python arch_blueprint --help
usage: arch_blueprint [-h] [--modules [MODULES ...]] root

Generate component diagrams in plantuml for python applications

positional arguments:
  root                  Name of root python module in project (example: 'myapp'

options:
  -h, --help            show this help message and exit
  --modules [MODULES ...], -m [MODULES ...]
                        Selected modules for rendering (examples: 'myapp.somemodule',
                        'myapp.somemodule.*', 'myapp.somemodule.**')
```

# Examples

Command usage example for `taskiq` lib
```shell
arch_blueprint taskiq -m "taskiq.api.*" "taskiq.cli.*" "taskiq.abc.*" "taskiq.result_backends.*" "taskiq.state" "taskiq.task" "taskiq.brokes.*" > out.puml
```

Example of graph

![Generated Graph](https://img.plantuml.biz/plantuml/dsvg/bLJBJiCm4BpxAuouW4GImGM1gWgeEF8DbMClZLK_mdfD15-FMnv9qxGr9w_icVNipjeFWGHIj8QJ26lzniwqaoOgY6XuGzI6-wf2qPKhJKsiOm2KtX4uAgMtLMk4sx3x0E4rL0q85Ieh0W5M0MKAjKj7mKUK42fgmAQbJOHY6nV2wfKeDnkCaMyvULvx8c-vqWYIj7UiqGeus9O-k0LR0mR6f14X_6WlHQlB81jGqG3osUpYvOgVNpy-BUuMb_Fv65pBCYcAXfQra6jmAeSXRHRiLyNok-8i2g0MHd_cARTQAGETm9EvfT5bvt5zEcyQ1VfBT_EyMDnUJwUBf4t8kJUDYFLkAN2L1V-NTwyUhI3A0zVeCngmEmwXLD7QZrEapPBJj4vGAk-qsZJ3QU11lqzXfuNoGldE5VD1nMpV_H5ee8bDUZ217_YPpTaE2zltObzpRoaRzlPmSIaSduuwatVlBYcFqpzNrZitKNzUjluvvnbtm8Z3XB4BOypsxH-fP7UaZdio_9mcQltk0dj8hKxV_HS0)


```plantuml
@startuml taskiq
!theme amiga

top to bottom direction
hide empty members

class taskiq.api.scheduler <<(M, #1ABC9C)>>

class taskiq.abc.result_backend <<(M, #1ABC9C)>>

class taskiq.abc.cmd <<(M, #1ABC9C)>>

class taskiq.abc.schedule_source <<(M, #1ABC9C)>>

class taskiq.abc.serializer <<(M, #1ABC9C)>>

class taskiq.abc.middleware <<(M, #1ABC9C)>>

class taskiq.cli.worker <<(M, #1ABC9C)>>

class taskiq.state <<(M, #2ECC71)>>

class taskiq.cli.utils <<(M, #1ABC9C)>>

class taskiq.cli.common_args <<(M, #1ABC9C)>>

class taskiq.cli.scheduler <<(M, #1ABC9C)>>

class taskiq.abc.formatter <<(M, #1ABC9C)>>

class taskiq.abc.broker <<(M, #1ABC9C)>>

class taskiq.result_backends.dummy <<(M, #1ABC9C)>>

class taskiq.task <<(M, #2ECC71)>>

class taskiq.cli.watcher <<(M, #1ABC9C)>>

class taskiq.api.receiver <<(M, #1ABC9C)>>
taskiq.result_backends -down-> taskiq.abc
taskiq.cli.worker -down-> taskiq.cli.watcher
taskiq.cli.scheduler -down-> taskiq.cli.common_args
taskiq.cli.scheduler -down-> taskiq.cli.utils
taskiq.abc.broker -down-> taskiq.abc.formatter
taskiq.task -down-> taskiq.abc
taskiq.abc -down-> taskiq.result_backends
taskiq.abc.broker -down-> taskiq.abc.result_backend
taskiq.abc.broker -down-> taskiq.abc.serializer
taskiq.api -down-> taskiq.cli
taskiq.abc.broker -down-> taskiq.abc.middleware
taskiq.cli.worker -down-> taskiq.cli.common_args
taskiq.cli.worker -down-> taskiq.cli.utils
taskiq.abc -down-> taskiq.state
taskiq.api -down-> taskiq.abc
taskiq.cli -down-> taskiq.abc
taskiq.abc.middleware -down-> taskiq.abc.broker
@enduml
```
