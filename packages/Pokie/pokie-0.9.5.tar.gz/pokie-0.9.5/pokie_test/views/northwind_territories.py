from pokie.rest import RestView


class TerritoriesView(RestView):
    def get(self, id_record=None):
        if id_record is None:
            return self.list()

        record = self.svc.get(id_record)
        if record is None:
            return self.not_found()

        # this just returns hamburger in description
        record.territory_description = "hamburger"
        return self.success(record)
