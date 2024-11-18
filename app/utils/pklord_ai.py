import requests
from typing import Dict, Union, List
import json
import traceback
from app.utils import utils
from app.models.play import PredictPutCardModel

class PklordAI:
    Tokenfree = 'rkQXMnYs72qECOLs9mGD9'
    Token5 = 'ksafsdafdsdgngnvcbrth'
    """
    斗地主AI静态类
    用于处理叫地主、出牌和让牌等操作
    """
    
    # API基础URL
    BASE_URL = "http://47.116.37.81:8567/ai-poker"
    # 请求头
    HEADERS = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Request-Token': Token5
    }
    # 密码
    PASSWD = "hk25f98y"
    
    @staticmethod
    def _make_request(url: str, data: dict) -> Dict:
        """
        发送HTTP请求的通用方法
        
        Args:
            url (str): 请求URL
            data (dict): 请求数据
            
        Returns:
            Dict: 响应数据
        """
        try:
            # 确保请求数据中包含密码
            if 'passwd' not in data:
                data['passwd'] = PklordAI.PASSWD
                
            response = requests.post(
                url,
                headers=PklordAI.HEADERS,
                json=data,
                timeout=30  # 添加超时设置
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"请求失败，状态码: {response.status_code}")
                return {"code": response.status_code, "message": response.text}
                
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {str(e)}")
            print(f"异常详情: {traceback.format_exc()}")
            return {"code": -1, "message": str(e)}
        except Exception as e:
            print(f"其他异常: {str(e)}")
            print(f"异常详情: {traceback.format_exc()}")
            return {"code": -1, "message": str(e)}
    
    @staticmethod
    def call_landlord(
        self_cards: str,
        call_time: int,
        oppo_call: int,
        self_player_account_id: str = None,
        game_id: str = None,
        mode: int = 1
    ) -> Dict[str, int]:
        """
        叫地主
        
        Args:
            self_cards (str): 自己的手牌，如 "D,X,2,2,A,A,K,K,Q,J,10,9,8,7,7,6,6"
            call_time (int): 叫地主回合数，从1开始
            oppo_call (int): 上一次对手是否叫了地主，当call_time为1时，oppo_call默认为0
            self_player_account_id (str, optional): 玩家id
            game_id (str, optional): 当局游戏id
            mode (int, optional): 模式，1：正常匹配模式，2：赢，3：输，4：平。默认为1
            
        Returns:
            Dict[str, int]: 包含call和code的字典，如 {"call": 1, "code": 0}
        """
        url = f"{PklordAI.BASE_URL}/call-landlord"
        
        data = {
            "self_cards": self_cards,
            "call_time": call_time,
            "oppo_call": oppo_call
        }
        
        # 添加可选参数
        if self_player_account_id:
            data["self_player_account_id"] = self_player_account_id
        if game_id:
            data["game_id"] = game_id
        if mode != 1:
            data["mode"] = mode
            
        return PklordAI._make_request(url, data)
    
    @staticmethod
    def play_cards(predict_model: PredictPutCardModel) -> Dict[str, Union[str, int]]:
        """
        出牌
        
        Args:
            params (Dict): 包含以下键值的字典:
                - history (List[str]): 出牌历史数据
                - self_cards (str): 自己的手牌
                - self_out (str): 自己所有出过的牌
                - oppo_last_move (str): 对手上一手出牌
                - oppo_out (str): 对手所有历史出牌
                - self_win_card_num (int): 自己剩余多少张牌获胜
                - oppo_win_card_num (int): 对手剩余多少张牌获胜
                - oppo_left_cards (int): 对手剩余手牌数
                - self_player_account_id (str, optional): 玩家id
                - game_id (str, optional): 当局游戏id
                - mode (int, optional): 模式，默认为1
                
        Returns:
            Dict[str, Union[str, int]]: 包含cards和code的字典，如 {"cards": "X,D", "code": 0}
        """
        url = f"{PklordAI.BASE_URL}/play-card"
        
        params = PklordAI.prepare_play_data(predict_model)
        data = {
            "history": params.get("history", []),
            "self_cards": params.get("self_cards", ""),
            "self_out": params.get("self_out", ""),
            "oppo_last_move": params.get("oppo_last_move", ""),
            "oppo_out": params.get("oppo_out", ""),
            "self_win_card_num": params.get("self_win_card_num", 0),
            "oppo_win_card_num": params.get("oppo_win_card_num", 0),
            "oppo_left_cards": params.get("oppo_left_cards", 0)
        }
        best_actions = PklordAI._make_request(url, data)
        best_actions = best_actions.get("cards", "")
        #print(f"best_actions: {best_actions}")
        result = ''
        if (len(best_actions) == 0):
            return 'pass'
        for best_action in best_actions:
            result += best_action
        return utils.convert_card_format(result)
    
    @staticmethod
    def check(
        self_cards: str,
        check_card_num: int,
        self_player_account_id: str = None,
        game_id: str = None,
        mode: int = 1
    ) -> Dict[str, int]:
        """
        让牌
        
        Args:
            self_cards (str): 自己的手牌，一定是20张
            check_card_num (int): 当前让牌数
            self_player_account_id (str, optional): 玩家id
            game_id (str, optional): 当局游戏id
            mode (int, optional): 模式，默认为1
            
        Returns:
            Dict[str, int]: 包含check和code的字典，如 {"check": 1, "code": 0}
        """
        url = f"{PklordAI.BASE_URL}/check"
        
        data = {
            "self_cards": self_cards,
            "check_card_num": check_card_num
        }
        
        # 添加可选参数
        if self_player_account_id:
            data["self_player_account_id"] = self_player_account_id
        if game_id:
            data["game_id"] = game_id
        if mode != 1:
            data["mode"] = mode
            
        return PklordAI._make_request(url, data)
    
    @staticmethod
    def convert_card_format(cards: str) -> str:
        """
        将简化格式的牌转换为标准格式
        
        Args:
            cards (str): 简化格式的牌，如 "999TTTAAKK"
            
        Returns:
            str: 标准格式的牌，如 "9,9,9,10,10,10,A,A,K,K"
        """
        # 定义转换映射
        card_map = {
            'T': '10',
            'R': 'D',  # 大王
            'B': 'X'   # 小王
        }
        
        # 将输入字符串转为列表
        card_list = list(cards)
        
        # 转换特殊字符
        converted_cards = []
        for card in card_list:
            converted_cards.append(card_map.get(card, card))
            
        # 将列表转换为逗号分隔的字符串
        return ','.join(converted_cards)

    @staticmethod
    def convert_card_format_reverse(cards: str) -> str:
        """
        将标准格式的牌转换为简化格式
        
        Args:
            cards (str): 标准格式的牌，如 "9,9,9,10,10,10,A,A,K,K,X,D"
            
        Returns:
            str: 简化格式的牌，如 "999TTTAAKKBR"
        """
        # 定义反向转换映射
        card_map = {
            '10': 'T',
            'D': 'R',   # 大王
            'X': 'B'    # 小王
        }
        
        # 分割输入字符串
        card_list = cards.split(',')
        
        # 转换特殊字符
        converted_cards = []
        for card in card_list:
            converted_cards.append(card_map.get(card, card))
            
        # 将列表合并为单个字符串（无分隔符）
        return ''.join(converted_cards)

    @staticmethod
    def prepare_play_data(predict_model: PredictPutCardModel):
        """
        将PredictPutCardModel转换为play_cards方法所需的数据格式
        Args:
            predict_model: PredictPutCardModel实例
        Returns:
            dict: 包含处理后的数据
        """
        # 构建历史出牌记录
        history = []
        for playable in predict_model.playables:
            history.append(PklordAI.convert_card_format(playable.cards) if playable.cards else "")

        # 确定自己和对手的出牌记录
        self_out = []
        oppo_out = []
        oppo_left_cards = 20
        if predict_model.self_seat == predict_model.landlord_seat:
            oppo_left_cards = 17
            
        for playable in predict_model.playables:
            if playable.seat == predict_model.self_seat:
                if len(playable.cards) > 0:
                    self_out.append(PklordAI.convert_card_format(playable.cards))
            else:
                if len(playable.cards) > 0:
                    oppo_left_cards -= len(playable.cards)
                    oppo_out.append(PklordAI.convert_card_format(playable.cards))
        
        # 获取对手最后一手牌
        oppo_last_move = ""
        if predict_model.playables:
            last_playable = predict_model.playables[-1]
            if last_playable.cards:
                oppo_last_move = PklordAI.convert_card_format(last_playable.cards)

        # 计算获胜所需牌数
        current_hand = PklordAI.convert_card_format(predict_model.current_hand)
        
        
        # 计算对手剩余牌数
        return {
            "history": history,
            "self_cards": current_hand,
            "self_out": ','.join(self_out) if self_out else "",
            "oppo_last_move": oppo_last_move,
            "oppo_out": ','.join(oppo_out) if oppo_out else "",
            "self_win_card_num": predict_model.self_win_card_num,
            "oppo_win_card_num": predict_model.oppo_win_card_num,
            "oppo_left_cards": oppo_left_cards
        }


class PklordLocal:
    def play_cards(request):
        
        print(f"request: {request}")
        if request.pk_status != 0:
            return 'pass'
        
        current_hand = request.current_hand
        lastMove = request.playables[-1].cards if request.playables else None
        actions =  utils.get_gt_cards(lastMove,current_hand)
        print(f"actions: {actions}")
        if len(actions) <= 1:
            return "pass"
        # 去掉 "pass"
        actions = [action for action in actions if action != "pass"]
        print(f"actions: {actions}")
        # 只能出炸弹，就出炸弹
        bombs = utils.get_bombs_rockets(current_hand)
        print(f"bombs: {bombs}")
        if len(bombs) != 0 and len(bombs) >= len(actions):
            return bombs[0]
        # 去除炸弹后，最长的一个action
        non_bomb_actions = [action for action in actions if action not in bombs]
        print(f"actions: {non_bomb_actions}")
        if non_bomb_actions:  # 如果非炸弹动作不为空
            return max(non_bomb_actions, key=len)  # 返回长度最长的一个action
        
        return "pass"