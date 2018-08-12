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

function non_empty(container) {
    for (var x in container) {
        return true
    }
    return false
}

function ui_tasks(api_tasks) {
    var tasks = []
    for (var i in api_tasks) {
        var task = api_tasks[i]
        task["scheduled_watering_time"] = human_duration(task["seconds"])
        task["submitted"] = human_datetime(task["ts_submitted"])
        task["started"] = human_datetime(task["ts_started"])
        task["terminated"] = human_datetime(task["ts_terminated"])
        task["actual_watering_time"] = maybe_human_duration(task["ts_started"], task["ts_terminated"])
        tasks.push(task)
    }
    return tasks
}

function ui_zones(api_zones, ratio) {
    var zones = []
    for (var zone_id in api_zones) {
        zone = api_zones[zone_id]
        var adjusted_seconds = Math.max(1, Math.min(zone["seconds"] * ratio / 100, 3600))
        zones.push({
            "zone_id": zone_id,
            "name": zone["name"],
            "seconds": zone["seconds"],
            "normal_watering_time": human_duration(zone["seconds"]),
            "adjusted_watering_time": human_duration(adjusted_seconds),
            "adjusted_seconds": adjusted_seconds
        })
    }
    return zones
}


function WaterbotViewModel() {
    var self = this

    self.ratio = ko.observable(100)
    self.api_pending_tasks = ko.observable()
    self.api_active_tasks = ko.observable()
    self.api_zones = ko.observable()
    self.pending_tasks = ko.observable()
    self.active_tasks = ko.observable()
    self.zones = ko.observable()
    self.any_pending = ko.observable()
    self.any_active = ko.observable()
 
    ko.computed(function() { self.pending_tasks(ui_tasks(self.api_pending_tasks())) })
    ko.computed(function() { self.active_tasks(ui_tasks(self.api_active_tasks())) })
    ko.computed(function() { self.zones(ui_zones(self.api_zones(), self.ratio())) })
    ko.computed(function() { self.any_pending(non_empty(self.api_pending_tasks())) })
    ko.computed(function() { self.any_active(non_empty(self.api_active_tasks())) })

    self.refresh = function() {
        $.post("/api/v0/active-tasks", function(data) {self.api_active_tasks(data)})
        $.post("/api/v0/pending-tasks", function(data) {self.api_pending_tasks(data)})
    }

    self.cancelTask = function(task) {
        var task_id = task["task_id"]
        console.log("Cancel: " + task_id)
        $.post("/api/v0/cancel-task/" + task_id)
            .fail(function(xhr, status, error) {
                alert(xhr.responseText)
            })
            .always(function() {
                self.refresh()
            })
    }

    self.waterZone = function(zone) {
        $.post("/api/v0/water-zone/"+zone["zone_id"]+"/"+zone["adjusted_seconds"])
            .fail(function(xhr, status, error) {
                alert(xhr.responseText)
            })
            .always(self.refresh)
    }

    self.waterAllZones = function() {
        zones = self.zones()
        var pending = zones.length
        function completion() {
            --pending;
            if (0 == pending) {
                self.refresh()
            }
        }
        for (var key in zones) {
            var zone = zones[key]
            $.post("/api/v0/water-zone/"+zone["zone_id"]+"/"+zone["adjusted_seconds"])
                .fail(function(xhr, status, error) {
                    alert(xhr.responseText)
                })
                .always(completion)
        }
    }

    $.post("/api/v0/zones", function(data) {self.api_zones(data)})
    self.refresh()
    setInterval(function(){self.refresh()}, 15000)
}

$(document).ready(function() {
    ko.applyBindings(new WaterbotViewModel())
})
