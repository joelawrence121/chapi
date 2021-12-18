from domain.repository import Repository


class OpeningService:

    def __init__(self):
        self.repository = Repository()

    def get_random_opening(self):
        return self.get_opening(self.repository.get_random_opening_id())

    def get_opening_by_move_stack(self, move_stack: str):
        opening_data = {'opening': None, 'variations': []}
        id = self.repository.get_opening_id_by_move_stack(move_stack)
        if id is not None:
            return self.get_opening(id)
        return opening_data

    def get_opening(self, id: int):
        opening_data = {'opening': None, 'variations': []}
        opening_data['opening'] = self.repository.get_opening(id)[0]
        opening_data['variations'] = self.repository.get_opening_variations(
            opening_data['opening']['move_stack'])
        return opening_data
