// Shows every view the skill can produce. A real workspace only keeps
// the levels the user validated.
workspace "Room booking" "Booking of a company's meeting rooms" {

    !identifiers hierarchical

    configuration {
        scope softwaresystem
    }

    // Documentation and decisions live in the project (docs/, docs/adr/), not in the workspace.
    properties {
        "structurizr.inspection.model.softwaresystem.documentation" "ignore"
        "structurizr.inspection.model.softwaresystem.decisions" "ignore"
    }

    model {
        employee = person "Employee" "Looks for a free room and books it for their meetings"
        facilityManager = person "Facility manager" "Declares the rooms, their equipment and their usage rules"

        calendar = softwareSystem "Company calendar" "Shared calendars of the employees" {
            tags "External"
        }
        identityProvider = softwareSystem "Identity provider" "Authenticates the employees (OIDC)" {
            tags "External"
        }

        roomBooking = softwareSystem "Room booking" "Shows free rooms, records bookings and releases the ones that are not used" {
            web = container "Web application" "Screens to search, book and administer rooms" "React 18" {
                tags "Web Browser"
            }
            api = container "Booking API" "Exposes the rooms, checks availability, records bookings" "Spring Boot 3, Java 21" {
                tags "High risk"

                bookingController = component "BookingController" "REST endpoints for search and booking" "Spring MVC"
                availabilityService = component "AvailabilityService" "Checks that a room is free for the slot and applies the usage rules" "Spring Bean" {
                    tags "High risk"
                }
                calendarClient = component "CalendarClient" "Adds the meeting to the organizer's calendar" "Spring RestClient"
                bookingRepository = component "BookingRepository" "Access to rooms and bookings" "Spring Data JPA"
            }
            releaseJob = container "Release batch" "Releases every night the bookings left unconfirmed" "Spring Batch" {
                tags "Medium risk"
            }
            db = container "Booking database" "Rooms, equipment and bookings" "PostgreSQL 15" {
                tags "Database"
            }
        }

        employee -> roomBooking.web "Searches for a room and books it" "HTTPS"
        facilityManager -> roomBooking.web "Declares the rooms and their rules" "HTTPS"
        roomBooking.web -> identityProvider "Authenticates the user" "OIDC"
        roomBooking.web -> roomBooking.api.bookingController "Sends searches and bookings" "REST/JSON"
        roomBooking.api.bookingController -> roomBooking.api.availabilityService "Asks whether the slot is free" "Java call"
        roomBooking.api.availabilityService -> roomBooking.api.bookingRepository "Reads the bookings for the slot" "Java call"
        roomBooking.api.availabilityService -> roomBooking.api.calendarClient "Triggers the calendar entry once the booking is accepted" "Java call"
        roomBooking.api.bookingRepository -> roomBooking.db "Reads and writes" "JDBC"
        roomBooking.api.calendarClient -> calendar "Creates the meeting event" "REST/JSON"
        roomBooking.releaseJob -> roomBooking.db "Reads unconfirmed bookings" "JDBC"
        roomBooking.releaseJob -> calendar "Cancels the events of released rooms" "REST/JSON"

        production = deploymentEnvironment "Production" {
            deploymentNode "Kubernetes cluster" "Production application cluster" "Kubernetes 1.30" {
                deploymentNode "Web pod" "Serves the React application" "nginx" {
                    containerInstance roomBooking.web
                }
                deploymentNode "API pod" "Hosts the API, two replicas" "Java 21" "" 2 {
                    containerInstance roomBooking.api
                }
                deploymentNode "CronJob" "Runs the batch every night" "Java 21" {
                    containerInstance roomBooking.releaseJob
                }
            }
            deploymentNode "Database server" "Shared instance" "PostgreSQL 15" {
                containerInstance roomBooking.db
            }
        }
    }

    views {
        systemContext roomBooking "C1-context" "Context: who uses room booking and what it exchanges with" {
            include *
            autoLayout lr
        }

        container roomBooking "C2-containers" "Containers, bordered by takeover risk level" {
            include *
            autoLayout lr
        }

        component roomBooking.api "C3-booking-api" "Components of the booking API" {
            include *
            autoLayout lr
        }

        dynamic roomBooking "Journey-nightly-release" "Journey: nightly release of unconfirmed bookings" {
            roomBooking.releaseJob -> roomBooking.db "Reads unconfirmed bookings"
            roomBooking.releaseJob -> calendar "Cancels the events of released rooms"
            autoLayout lr
        }

        dynamic roomBooking.api "Journey-room-booking" "Critical journey: booking a room and adding it to the calendar" {
            roomBooking.web -> roomBooking.api.bookingController "Sends the booking"
            roomBooking.api.bookingController -> roomBooking.api.availabilityService "Asks whether the slot is free"
            roomBooking.api.availabilityService -> roomBooking.api.bookingRepository "Reads the bookings for the slot"
            roomBooking.api.availabilityService -> roomBooking.api.calendarClient "Triggers the calendar entry"
            roomBooking.api.calendarClient -> calendar "Creates the meeting event"
            autoLayout lr
        }

        deployment roomBooking production "Deployment-production" "Production deployment" {
            include *
            autoLayout lr
        }

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
            // Read from config or docs but not proven by the code.
            element "Assumed" {
                border dashed
            }
            relationship "Assumed" {
                style dotted
            }
            // Risk levels from legacy-takeover: a thick coloured border keeps the C4 fill readable.
            element "High risk" {
                stroke #C0392B
                strokeWidth 8
            }
            element "Medium risk" {
                stroke #E67E22
                strokeWidth 6
            }
        }
    }

}
