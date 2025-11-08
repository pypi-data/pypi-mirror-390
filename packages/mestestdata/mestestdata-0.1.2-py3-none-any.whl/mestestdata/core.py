import requests
import json
import time
from typing import Dict, Optional, List


class MESClient:
    def __init__(self, api_url: str = "http://10.141.106.183/MES_API_A6/api/MESApi"):
        """
        初始化MES API客户端
        :param api_url: MES系统API地址
        """
        self.api_url = api_url
        self.session = requests.Session()
        # 设置超时时间（秒）
        self.timeout = 30
        print('api接口为：http://10.141.106.183/MES_API_A6/api/MESApi')

    def send_command(self, command: str, input_data: str) -> Optional[Dict]:
        """
        发送指令到MES系统
        :param command: 指令代码（如"A6TE001"）
        :param input_data: 输入数据（内控码）
        :return: 响应结果字典，失败时返回None
        """
        # 构建请求数据
        payload = {
            "Data": [
                {
                    "Command": command,
                    "InputData": input_data
                }
            ]
        }

        print(f'发送的指令为{command},输入的内控码为{input_data}')

        try:
            # 发送POST请求
            response = self.session.post(
                self.api_url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )

            # 检查响应状态码
            response.raise_for_status()

            # 解析响应内容
            result = response.json()
            return result

        except requests.exceptions.Timeout:
            print("请求超时")
        except requests.exceptions.ConnectionError:
            print("连接错误，请检查内网连接")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP错误: {str(e)}")
        except json.JSONDecodeError:
            print("响应内容不是有效的JSON格式")
        except Exception as e:
            print(f"发生未知错误: {str(e)}")

        return None

    def batch_send_commands(self, commands: List[Dict]) -> List[Optional[Dict]]:
        """
        批量发送指令
        :param commands: 指令列表，每个元素为{"Command": "...", "InputData": "..."}
        :return: 响应结果列表
        """
        results = []
        for i, cmd in enumerate(commands, 1):
            print(f"处理第 {i}/{len(commands)} 条指令: {cmd.get('Command')}")
            result = self.send_command(cmd.get("Command"), cmd.get("InputData", ""))
            results.append(result)
            # 避免请求过于频繁，可根据需要调整间隔
            time.sleep(0.5)
        return results

    def parse_message(self, message: str) -> str:
        """
        按规则解析返回消息：
        - 分号前最后一个@到分号之间的数据为A（1号位）
        - 分号前倒数第二个@到最后一个@之间的数据为A1（2号位）
        - A与A1之间用/分隔
        - 不同组之间（A1与B之间）用分号分隔
        - A为空则丢弃该段
        - 若A与前面出现过的A值相同，则整段丢弃
        """
        # 处理开头的OK;标记
        if message.startswith("OK;"):
            parts = message[3:].split(";")
        else:
            parts = message.split(";")

        result = []
        seen_a_values = set()  # 用于记录已出现过的A值，实现去重

        for part in parts:
            # 跳过空段
            if not part:
                continue

            # 查找所有@的位置
            at_positions = [i for i, char in enumerate(part) if char == "@"]

            # 没有@的段跳过
            if not at_positions:
                continue

            # 提取A值：最后一个@到段尾
            a_start = at_positions[-1] + 1
            a_val = part[a_start:].strip()

            # A值为空则丢弃该段
            if not a_val:
                a_val='未备注'
                #continue

            # 如果A值已出现过，则整段丢弃
            if a_val in seen_a_values:
                continue

            # 记录A值，用于后续去重
            seen_a_values.add(a_val)

            # 提取A1值：倒数第二个@到最后一个@之间
            if len(at_positions) >= 2:
                a1_start = at_positions[-2] + 1
                a1_end = at_positions[-1]
                a1_val = part[a1_start:a1_end].strip()
            else:
                a1_val = ""

            # A与A1之间用/分隔
            if a1_val:
                result.append(f"{a_val}/{a1_val}")
            else:
                result.append(a_val)

        # 不同组之间用分号分隔
        return ";".join(result)


def mestestdata(code: str, api_url: str = "http://10.141.106.183/MES_API_A6/api/MESApi") -> str:
    """
    查询MES系统数据的简便函数
    :param code: 内控码
    :param api_url: MES系统API地址，默认为标准地址
    :return: 解析后的数据字符串，格式为"A/A1;B/B1"或"no/no"（当查询失败时）
    """
    # 创建客户端实例
    mes_client = MESClient(api_url)
    
    # 发送单条指令
    command = "A6TE001"
    inner_code = f"{code}"

    response = mes_client.send_command(command, inner_code)

    if response:
        # 检查是否有数据
        if response.get('Data') and len(response['Data']) > 0 and 'Message' in response['Data'][0]:
            raw_message = response['Data'][0]['Message']

            # 解析数据
            parsed_result = mes_client.parse_message(raw_message)
            # 如果解析结果为空，返回no/no
            #return parsed_result if parsed_result else "nofail"
            # 优先级：先判断是否包含“未备注” → 再判断是否有解析结果 → 最后返回nofail
            return '未备注' if '未备注' in str(parsed_result) else (parsed_result if parsed_result else "nofail")
        else:
            # 数据为空的情况
            return "nodata"
    else:
        # 响应为空（报错）的情况
        return "error"