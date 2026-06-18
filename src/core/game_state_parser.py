from src.components.card import Card


class GameStateAdapter:
    @staticmethod
    def to_card(card_data):
        if not card_data:
            return None

        if "fruit" not in card_data or "number" not in card_data:
            return None

        return Card(card_data["fruit"], int(card_data["number"]), "")

    @staticmethod
    def parse_game_state(data, player_id):
        queues = data.get("card_queues", {})
        stacks = data.get("card_stacks", {})
        turn_id = data.get("turn", None)

        my_id = str(player_id)
        opp_id = None

        for pid in queues.keys():
            if str(pid) != my_id:
                opp_id = str(pid)
                break

        my_count = queues.get(my_id, 0)
        opp_count = queues.get(opp_id, 0) if opp_id else 0

        my_stack = stacks.get(my_id, [])
        my_top_card = GameStateAdapter.to_card(my_stack[-1]) if my_stack else None

        opp_top_card = None
        if opp_id:
            opp_stack = stacks.get(opp_id, [])
            if opp_stack:
                top = opp_stack[-1]
                if top.get("is_visible", True):
                    opp_top_card = GameStateAdapter.to_card(top)

        opp_next_card = GameStateAdapter.to_card(data.get("opponent_next_card"))

        return {
            "my_id": my_id,
            "opp_id": opp_id,
            "my_count": my_count,
            "opp_count": opp_count,
            "my_top_card": my_top_card,
            "opp_top_card": opp_top_card,
            "opp_next_card": opp_next_card,
            "turn_id": turn_id,
        }