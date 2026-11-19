# Structurizr DSL: the essentials for this skill

Full reference: https://docs.structurizr.com/dsl/language. Validated example with one view of each
type (C1, C2, one C3, two journeys, deployment):
[`../examples/workspace.dsl`](../examples/workspace.dsl). The C3 split into several views and the
`Assumed` tag only appear in the snippets below.

## Language

Identifiers in English (`roomBooking.api.bookingController`), labels in the language the user works
in: names, descriptions, unknown technologies ("to confirm"), relationships, view titles. View keys
stay without spaces or accents (see below). A component keeps the name of its class or module, as
it is in the code. Tag names (`Assumed`, `High risk`, `Medium risk`, `External`, `Database`,
`Web Browser`) stay as written here, since the styles refer to them.

## Pitfalls checked with `structurizr` 2026.09

- **A `{ … }` block spans several lines.** `x = person "A" { tags "B" }` on one line fails ("Too
  many tokens"). Open the brace at the end of the line, one statement per line.
- **`!identifiers hierarchical`** at the top: nested elements are named `system.container` and
  `system.container.component`. Without it, two `api` containers in two systems collide.
- **Scope**: `configuration { scope softwaresystem }`, otherwise the inspector asks for it.
- **Documentation and decisions**: the inspector requires `!docs` and `!adrs` as soon as a system
  has containers. They live in the project (`docs/`, `docs/adr/`), so have them ignored:
  ```
  properties {
      "structurizr.inspection.model.softwaresystem.documentation" "ignore"
      "structurizr.inspection.model.softwaresystem.decisions" "ignore"
  }
  ```
- **Technology on every relationship**, even internal ones (`"Java call"`, `"Method call"`).
  Unknown: `"to confirm"`, never made up to silence the inspector.
- **Description on every deployment node** (second argument, do not leave `""`).
- **View keys** without spaces or accents: `C2-containers`, not `C2 containers`. They serve as the
  anchor in the site URL (`index.html#C2-containers`).
- Context relationships are **deduced** from relationships between containers: do not write them
  twice.
- **At C3, keep the relationship between two containers written when several component
  relationships connect them.** Without it, C2 deduces it and keeps only the label of the first
  component relationship it meets. An explicit relationship between the two containers prevents
  that deduction: C2 keeps its label, C3 shows the detail.
- **All the styles from the start**: copy the full block of the Styles section from the first
  level. A missing style (`Component` for example) leaves the elements of the next level grey.

## Skeleton

```
workspace "<System name>" "<What it does, one sentence>" {

    !identifiers hierarchical

    configuration {
        scope softwaresystem
    }

    properties {
        "structurizr.inspection.model.softwaresystem.documentation" "ignore"
        "structurizr.inspection.model.softwaresystem.decisions" "ignore"
    }

    model {
        // 1. actors, 2. external systems, 3. the system and its containers,
        // 4. relationships, 5. deployment environments
    }

    views {
        // one view per validated level, then the full styles block (Styles section)
    }

}
```

## Elements

```
employee = person "Employee" "What they do with the system"

calendar = softwareSystem "Company calendar" "Its role as seen from the system" {
    tags "External"
}

app = softwareSystem "Name" "Description" {
    web = container "Web application" "Role" "React 18" {
        tags "Web Browser"
    }
    api = container "API" "Role" "Spring Boot 3, Java 21" {
        service = component "AvailabilityService" "Role" "Spring Bean"
    }
    db = container "Database" "What it stores" "PostgreSQL 15" {
        tags "Database"
    }
}
```

Signature: `<id> = <type> "<name>" "[description]" "[technology]" "[tags]"` (no technology for
`person` and `softwareSystem`).

## Relationships

```
employee -> app.web "Books a room" "HTTPS"
app.web -> app.api.service "Asks for the free slots" "REST/JSON"
app.api.service -> calendar "Creates the meeting event" "REST/JSON"
```

Relationship deduced with no proof in the code:

```
app.api -> calendar "Exports room occupancy" "SFTP" {
    tags "Assumed"
}
```

The source is the one that initiates the call. The description says what happens ("Creates the
event"), never "Uses". A message queue: `producer -> queue "Publishes <event>" "AMQP"` and
`consumer -> queue "Consumes <event>" "AMQP"`.

## Views

```
systemContext app "C1-context" "Readable title" {
    include *
    autoLayout lr
}
container app "C2-containers" "Readable title" {
    include *
    autoLayout lr
}
component app.api "C3-api" "Readable title" {
    include *
    autoLayout lr
}
// System scope, the default: steps between containers, no C3 required.
dynamic app "Journey-<slug>" "Journey: <name>" {
    employee -> app.web "Step 1"
    app.web -> app.api "Step 2"
    app.api -> calendar "Step 3"
    autoLayout lr
}
// Container scope, only if the container's C3 exists: steps between components.
dynamic app.api "Journey-<slug>-detail" "Journey: <name>, inside the API" {
    app.web -> app.api.service "Step 1"
    app.api.service -> calendar "Step 2"
    autoLayout lr
}
deployment app production "Deployment-production" "Readable title" {
    include *
    autoLayout lr
}
```

A busy C3, split into two views of the same container (identifiers from the example):

```
component roomBooking.api "C3-api-business" "API: availability and bookings" {
    include roomBooking.web roomBooking.api.bookingController roomBooking.api.availabilityService roomBooking.api.bookingRepository roomBooking.db
    autoLayout lr
}
component roomBooking.api "C3-api-integrations" "API: calendar integration" {
    include roomBooking.api.availabilityService roomBooking.api.calendarClient calendar
    autoLayout lr
}
```

`include` lists the elements kept; `exclude "a -> b"` removes a relationship already shown in the
other view. Each component must appear in at least one view, otherwise the inspector reports it.

`autoLayout lr` (left to right) reads better than `tb` for front end, API, database chains. A
dynamic view only cites relationships that exist in the model, or that can be deduced from it (a
relationship between components counts between their containers), otherwise validation fails.

## Deployment

```
production = deploymentEnvironment "Production" {
    deploymentNode "Cluster" "Description" "Kubernetes 1.30" {
        deploymentNode "API pod" "Description" "Java 21" "" 2 {
            containerInstance app.api
        }
    }
}
```

The `2` is the number of instances (the `""` before it is the place for tags).

## Styles

Classic C4 colours, plus the skill's tags:

```
styles {
    element "Person" {
        shape Person
        background #08427B
        color #ffffff
    }
    element "Software System" {
        background #1168BD
        color #ffffff
    }
    element "Container" {
        background #438DD5
        color #ffffff
    }
    element "Component" {
        background #85BBF0
        color #000000
    }
    element "External" {
        background #999999
        color #ffffff
    }
    element "Database" {
        shape Cylinder
    }
    element "Web Browser" {
        shape WebBrowser
    }
    element "Assumed" {
        border dashed
    }
    relationship "Assumed" {
        style dotted
    }
    element "High risk" {
        stroke #C0392B
        strokeWidth 8
    }
    element "Medium risk" {
        stroke #E67E22
        strokeWidth 6
    }
}
```

Risk is shown by the **border**: the fill stays that of the C4 level, the view stays readable.
