function WaterbotViewModel() {
    var self = this

    self.tasks = ko.observable()
    self.zones = ko.observable()

    $.post("/api/v0/tasks", function(data) {
        self.tasks(data) 
    })
    $.post("/api/v0/zones", function(data) {
        var zones = []
        for (var zone_id in data) {
            zone = data[zone_id]
            zones.push({
                "zone_id": zone_id,
                "name": zone["name"],
                "seconds": zone["seconds"]
            })
        }
        console.log(zones)
        self.zones(zones)
    })
}

$(document).ready(function() {
    ko.applyBindings(new WaterbotViewModel())
})
