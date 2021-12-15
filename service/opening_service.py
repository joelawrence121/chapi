from domain.repository import Repository


class OpeningService:

    def __init__(self):
        self.repository = Repository()

    def get_random_opening(self):
        return self.get_opening(self.repository.get_random_opening_id())

    def get_opening(self, id: int):
        opening_data = {'opening': None, 'variations': []}
        opening_data['opening'] = self.repository.get_opening(id)[0]
        opening_data['variations'] = self.repository.query_opening_by_move_stack_subset(
            opening_data['opening']['move_stack'])
        return opening_data
