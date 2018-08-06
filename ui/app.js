function human_duration(seconds) {
    if (seconds >= 3600) {
        return (seconds / 3600).toFixed(2) + " hours"
    } else if (seconds >= 60) {
        return (seconds / 60).toFixed(2) + " minutes"
    } else {
        return seconds + " seconds"
    }
}

function maybe_human_duration(start_seconds, end_seconds) {
    if (start_seconds && end_seconds) {
        return human_duration(end_seconds - start_seconds)
    } else {
        return "-"
    }
}
function human_datetime(datetime) {
    if (datetime) {
        return new Date(datetime*1000).toLocaleString()
    } else {
        return "-"
    }
}

function WaterbotViewModel() {
    var self = this

    self.tasks = ko.observable()
    self.zones = ko.observable()

    $.post("/api/v0/tasks", function(data) {
        var tasks = []
        for (var i in data) {
            var task = data[i]
            task["scheduled_watering_time"] = human_duration(task["seconds"])
            task["submitted"] = human_datetime(task["ts_submitted"])
            task["started"] = human_datetime(task["ts_started"])
            task["terminated"] = human_datetime(task["ts_terminated"])
            task["actual_watering_time"] = maybe_human_duration(task["ts_started"], task["ts_terminated"])
            tasks.push(task)
        }
        self.tasks(tasks)
    })

    $.post("/api/v0/zones", function(data) {
        var zones = []
        for (var zone_id in data) {
            zone = data[zone_id]
            zones.push({
                "zone_id": zone_id,
                "name": zone["name"],
                "seconds": zone["seconds"],
                "normal_watering_time": human_duration(zone["seconds"])
            })
        }
        self.zones(zones)
    })
}

$(document).ready(function() {
    ko.applyBindings(new WaterbotViewModel())
})
